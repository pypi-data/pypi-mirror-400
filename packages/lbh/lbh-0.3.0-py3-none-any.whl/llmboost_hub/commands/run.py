import click
import os
import subprocess
import shlex
import glob
import json
from typing import List
from llmboost_hub.utils import gpu_info
from llmboost_hub.utils.config import config
from llmboost_hub.commands.prep import do_prep
from llmboost_hub.commands.list import do_list
from llmboost_hub.utils.container_utils import container_name_for_model
from llmboost_hub.utils.model_utils import (
    get_repo_from_model_id,
    get_model_name_from_model_id,
    get_model_path,
    set_model_path,
)
from llmboost_hub.commands.stop import do_stop
from llmboost_hub.commands.completions import complete_model_names


def _image_exists_locally(image_name: str) -> bool:
    """
    Return True if the image exists locally (matches repo or repo:tag).

    Args:
        image_name: Image reference to find.

    Notes:
        Uses `docker images --format` and performs relaxed matching:
        exact match, prefix match, or matching repository name without tag.
    """
    try:
        out = subprocess.check_output(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"], text=True
        )
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        # allow matching repo or repo:tag
        for l in lines:
            if l == image_name or l.startswith(image_name) or l.split(":")[0] == image_name:
                return True
        return False
    except Exception:
        return False


def _wait_for_running(container_name: str, timeout_sec: float = 10.0) -> bool:
    """
    Poll docker inspect until the container is reported running or timeout.

    Args:
        container_name: Target container name.
        timeout_sec: Maximum seconds to wait.

    Returns:
        True if running within the timeout window; False otherwise.
    """
    import time

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            out = subprocess.check_output(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out.lower() == "true":
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def _ensure_inference_db_symlink(cname: str, verbose: bool = False) -> None:
    """
    Ensure the container's inference DB points at the host DB (mounted).

    Steps:
        1) If host DB file (`config.LBH_TUNER_DB_PATH`) is missing, copy from container (`config.LLMBOOST_TUNER_DB_PATH`).
        2) Back up container DB file (`config.LLMBOOST_TUNER_DB_PATH` -> `config.LLMBOOST_TUNER_DB_BACKUP_PATH`).
        3) Symlink container DB -> mounted host DB inside container:
           `config.LLMBOOST_TUNER_DB_PATH` -> `config.CONTAINER_LBH_HOME`/basename(`config.LBH_TUNER_DB_PATH`).

    Args:
        cname: Container name.
        verbose: If True, echo docker exec steps.

    Raises:
        ClickException: If host DB cannot be created or ensured.
    """
    host_home = config.LBH_HOME
    host_db = config.LBH_TUNER_DB_PATH
    try:
        os.makedirs(host_home, exist_ok=True)
        if not os.path.exists(host_db):
            if verbose:
                click.echo(f"[run] Creating host inference DB at {host_db}...")
            # Copy from container if exists
            copy_cmd = [
                "docker",
                "cp",
                f"{cname}:{config.LLMBOOST_TUNER_DB_PATH}",
                host_db,
            ]
            try:
                subprocess.run(copy_cmd, check=True)
            except Exception as e:
                raise click.ClickException(
                    f"Host inference DB '{host_db}' not found; and failed to copy from container.\n{e}"
                )
    except Exception as e:
        raise click.ClickException(f"Failed to ensure host inference DB at '{host_db}'.\n{e}")

    def _exec(cmd):
        if verbose:
            click.echo(f"[run] docker exec: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                click.echo(f"[run] Warning: exec failed: {e}")

    # Create data dir inside container
    _exec(
        [
            "docker",
            "exec",
            cname,
            "mkdir",
            "-p",
            f"{os.path.dirname(config.LLMBOOST_TUNER_DB_PATH)}",
        ]
    )
    # Backup DB inside container
    _exec(
        [
            "docker",
            "exec",
            cname,
            "sh",
            "-lc",
            f"cp {config.LLMBOOST_TUNER_DB_PATH} {config.LLMBOOST_TUNER_DB_BACKUP_PATH}",
        ]
    )

    # Symlink container DB -> host DB
    _exec(
        [
            "docker",
            "exec",
            cname,
            "sh",
            "-lc",
            f'ln -sfn {os.path.join(config.CONTAINER_LBH_HOME, f"{os.path.basename(config.LBH_TUNER_DB_PATH)}")} {config.LLMBOOST_TUNER_DB_PATH}',
        ]
    )


def do_run(
    model: str,
    lbh_workspace: str | None,
    docker_args: tuple,
    verbose: bool = False,
    image: str | None = None,
    model_path: str | None = None,
    restart: bool = False,
) -> dict:
    """
    Start a model container with recommended defaults (overridable via `docker_args`).

    Behavior:
        - Network/IPC/security defaults for ML workloads.
        - Mounts:
            * `config.LBH_HOME` -> `/llmboost_hub` (and sets `LBH_HOME`)
            * `lbh_workspace` (or `config.LBH_WORKSPACE`) -> `/user_workspace` (workdir=`/workspace`)
            * models: either `--model_path` or `config.LBH_HOME/models/<repo>` -> `config.LLMBOOST_MODELS_DIR`
        - GPU flags:
            * NVIDIA: `--gpus all`
            * AMD: `--device /dev/dri` and `--device /dev/kfd`
        - Detached keepalive (`tail -f /dev/null`) for later exec calls.
        - Ensures inference DB symlink and license symlink inside container.

    Args:
        model: Model identifier.
        lbh_workspace: Optional workspace dir to mount.
        docker_args: Extra docker args passed after `--`.
        verbose: If True, echo docker command and exec steps.
        image: Optional forced image (required when multiple images match).
        model_path: Optional local HF model directory to mount directly.
        restart: If True, restart the container if it is already running.

    Returns:
        Dict: {returncode: int, container_name: str, command: list[str], error: str|None}
    """
    lbh_home = config.LBH_HOME
    workspace = lbh_workspace or config.LBH_WORKSPACE
    os.makedirs(workspace, exist_ok=True)

    # Restart if requested
    if restart:
        stop_res = do_stop(model, None, verbose=verbose)
        if stop_res["returncode"] != 0:
            msg = (stop_res.get("error") or "").lower()
            if "not running" not in msg:
                raise click.ClickException(
                    stop_res.get("error") or "Failed to stop existing container"
                )

    # Resolve docker image
    resolved_image = image
    if not resolved_image:
        matching = do_list(query=model, verbose=verbose)["lookup_df"]
        if len(matching) == 0:
            return {
                "returncode": 1,
                "container_name": "",
                "command": [],
                "error": f"No image found for model '{model}'. Use --image to specify explicitly.",
            }
        unique_images: List[str] = sorted(set(matching["docker_image"].astype(str).tolist()))
        if len(unique_images) > 1:
            return {
                "returncode": 1,
                "container_name": "",
                "command": [],
                "error": f"Multiple images found for model '{model}': {', '.join(unique_images)}. Use --image to choose.",
            }
        resolved_image = unique_images[0]
    click.echo(f"Using image '{resolved_image}'.")

    # Auto-prep missing model if configured
    prep_needed_msg: str = ""

    # if `--model_path` is given
    if model_path:
        # validate model path contains ('*config.json' file, AND contains '_name_or_path' or 'architectures' keys) AND ('vocab.json' or 'tokenizer_config.json' file)

        transformed_model_path = os.path.abspath(os.path.expanduser(os.path.dirname(model_path)))
        config_files = glob.glob(
            os.path.join(transformed_model_path, "**", "*config.json"), recursive=True
        )
        if not config_files:
            return {
                "returncode": 1,
                "container_name": "",
                "command": [],
                "error": f"Model path '{transformed_model_path}' does not contain any '*config.json' files.",
            }
        valid_config_found = False
        for cfg_file in config_files:
            try:
                with open(cfg_file, "r") as f:
                    cfg = json.load(f)
                if any(k in cfg for k in ["_name_or_path", "architectures"]):
                    # Check for vocab/tokenizer files
                    vocab_json = os.path.join(os.path.dirname(cfg_file), "vocab.json")
                    tokenizer_config_json = os.path.join(
                        os.path.dirname(cfg_file), "tokenizer_config.json"
                    )
                    if os.path.exists(vocab_json) or os.path.exists(tokenizer_config_json):
                        valid_config_found = True
                        break
            except Exception:
                continue
        if not valid_config_found:
            return {
                "returncode": 1,
                "container_name": "",
                "command": [],
                "error": f"Model path '{transformed_model_path}' does not appear to be a valid Hugging Face model directory, or is an unsupported model. Please ensure it contains a '*config.json' file with either '_name_or_path' or 'architectures' keys, and a 'vocab.json' or 'tokenizer_config.json' file.",
            }
        host_model_path: str = os.path.abspath(transformed_model_path)  # path to model on host

        # Save user-provided model path to mapping file for future use
        try:
            set_model_path(model, host_model_path)
            if verbose:
                click.echo(f"Saved model path to mapping: {model} -> {host_model_path}")
        except Exception as e:
            if verbose:
                click.echo(f"Warning: Failed to save model path to mapping file: {e}")
    else:
        # Check mapping file first for the model path
        mapped_path = get_model_path(model)
        if mapped_path:
            host_model_path = mapped_path
            if verbose:
                click.echo(f"Using model path from mapping: {host_model_path}")
        else:
            # Derive repo from full repo id (e.g., 'meta-llama/Llama-3.2-1B-Instruct' => 'meta-llama')
            repo_name = get_repo_from_model_id(model)
            model_name = get_model_name_from_model_id(model)
            host_model_path: str = os.path.join(
                config.LBH_MODELS, repo_name, model_name
            )  # path to model on host

        if not os.path.exists(host_model_path):
            prep_needed_msg += f"Model '{model}' does not exist locally. Please ensure model's 'Repo/Name' exactly matches the name on https://huggingface.co. Please login to huggingface-cli, then run '{__name__.split('.')[0]} prep {model}' or 'hf download {model} --local-dir {host_model_path}' to download the model."

    container_model_path = os.path.join(
        config.LLMBOOST_MODELS_DIR, get_model_name_from_model_id(model)
    )  # path to model inside container
    click.echo(
        f"Mounting model: {host_model_path} {f'<- {config.LLMBOOST_MODELS_DIR}' if verbose else ''}"
    )

    # GPU flags
    gpu_flags: List[str] = []
    if len(gpu_info.get_nvidia_gpus()) > 0:
        gpu_flags = ["--gpus", "all"]
    elif len(gpu_info.get_amd_gpus()) > 0:
        gpu_flags = ["--device", "/dev/dri:/dev/dri", "--device", "/dev/kfd:/dev/kfd"]

    # Keep the container alive so subsequent exec works reliably
    keep_alive_flags: List[str] = ["tail", "-f", "/dev/null"]

    container_name = container_name_for_model(model)

    # Only accept docker args passed after `--`
    extra = list(docker_args or ())

    # Ensure image exists locally (pull as needed)
    if not _image_exists_locally(resolved_image):
        prep_needed_msg += f"Docker image '{resolved_image}' missing locally. Please login to docker (`docker login -u <username>`), then run '{__name__.split('.')[0]} prep {model}' (recommended) or 'docker pull {resolved_image}' to pull the image."

    # Prep model, if missing and configured
    if prep_needed_msg != "":
        if config.LBH_AUTO_PREP:
            prep_res = do_prep(model, verbose=verbose)
            if prep_res["status"] == "error":
                return {
                    "returncode": 1,
                    "container_name": "",
                    "command": [],
                    "error": prep_res["error"],
                }
        else:
            return {
                "returncode": 1,
                "container_name": "",
                "command": [],
                "error": prep_needed_msg,
            }

    # Base docker run with recommended defaults; start detached
    docker_cmd = (
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "--name",
            container_name,
            "--network",
            "host",
            "--group-add",
            "video",
            "--ipc",
            "host",
            "--cap-add",
            "SYS_PTRACE",
            "--security-opt",
            "seccomp=unconfined",
            "-v",
            f"{host_model_path}:{container_model_path}",
            "-v",
            f"{lbh_home}:{config.CONTAINER_LBH_HOME}",
            "-v",
            f"{workspace}:{config.CONTAINER_USER_WORKSPACE}",
            "-e",
            f"LBH_HOME={config.CONTAINER_LBH_HOME}",
            "-e",
            f"HF_TOKEN={os.environ.get('HF_TOKEN', os.environ.get('HUGGINGFACE_TOKEN', ''))}",
            "-w",
            f"{config.LLMBOOST_WORKSPACE}",
        ]
        + gpu_flags
        + extra
        + [resolved_image]
        + keep_alive_flags
    )

    if verbose:
        click.echo("[run] Executing Docker command:")
        click.echo(" ".join(docker_cmd))

    # Start container detached
    try:
        subprocess.run(docker_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {
            "returncode": e.returncode,
            "container_name": container_name,
            "command": docker_cmd,
            "error": f"Docker run failed (exit {e.returncode})",
        }

    # Wait until running
    if not _wait_for_running(container_name, timeout_sec=15.0):
        return {
            "returncode": 1,
            "container_name": container_name,
            "command": docker_cmd,
            "error": "Container failed to stay running after start.",
        }

    _ensure_inference_db_symlink(container_name, verbose=verbose)

    # Symlink for license inside container
    # - License: /llmboost_hub/license.skm <- /workspace/license.skm
    def _exec(cmd):
        if verbose:
            click.echo(f"[run] docker exec: {' '.join(shlex.quote(x) for x in cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if verbose:
                click.echo(f"[run] Warning: exec failed: {e}")

    _exec(
        [
            "docker",
            "exec",
            container_name,
            "mkdir",
            "-p",
            config.LLMBOOST_WORKSPACE,
            config.LLMBOOST_MODELS_DIR,
        ]
    )
    _exec(
        [
            "docker",
            "exec",
            container_name,
            "ln",
            "-sfn",
            os.path.join(
                config.CONTAINER_LBH_HOME,
                os.path.basename(config.LBH_LICENSE_PATH),
            ),
            config.LLMBOOST_LICENSE_PATH,
        ]
    )

    # No interactive handling (by design)
    return {
        "returncode": 0,
        "container_name": container_name,
        "command": docker_cmd,
        "error": None,
    }


@click.command(
    context_settings={"ignore_unknown_options": True, "help_option_names": ["-h", "--help"]}
)
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "--lbh-workspace", type=click.Path(), help="Override workspace path mounted inside container."
)
@click.option(
    "-i",
    "--image",
    "forced_image",
    type=str,
    default=None,
    help="Force a specific docker image (required when multiple images match the model).",
)
@click.option(
    "-m",
    "--model_path",
    "model_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    default=None,
    help=f"Local HF model directory to mount inside the container.",
)
@click.option(
    "-r",
    "--restart",
    is_flag=True,
    help="Restart the container if it is running before starting.",
)
@click.argument("docker_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx: click.Context, model, lbh_workspace, forced_image, model_path, restart, docker_args):
    """
    Run a model container with defaults; pass extra docker flags after `--`.
    """
    verbose = ctx.obj.get("VERBOSE", False)

    res = do_run(
        model,
        lbh_workspace,
        docker_args,
        verbose=verbose,
        image=forced_image,
        model_path=model_path,
        restart=restart,
    )

    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Docker run failed")

    # No extra presentation needed on success
