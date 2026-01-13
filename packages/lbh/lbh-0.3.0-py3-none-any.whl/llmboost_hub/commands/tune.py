import click
import subprocess
import time
from typing import Optional
import os
import shutil
from datetime import datetime

from llmboost_hub.commands.run import do_run
from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
    is_model_tuning,
)
from llmboost_hub.commands.completions import complete_model_names
from llmboost_hub.utils.config import config
from llmboost_hub.utils.gpu_info import get_gpu_count
from llmboost_hub.commands.stop import do_stop


def _collect_error_logs(cname: str, max_lines: int = 200) -> str:
    """
    Collect recent error log lines from the container.

    Strategy:
    - Grep case-insensitive 'error' across `worker*.log` under `config.LLMBOOST_LOGS_DIR` and tail `max_lines`.
    - Fallback to tailing any `*.log` if grep returns nothing.

    Args:
        cname: Target container name.
        max_lines: Maximum number of lines to include.

    Returns:
        Concatenated recent log lines, or empty string on failure or no logs.
    """
    try:
        grep_cmd = [
            "docker",
            "exec",
            cname,
            "sh",
            "-lc",
            f"grep -i 'error' -r {config.LLMBOOST_LOGS_DIR}/worker*.log 2>/dev/null | tail -n {max_lines}",
        ]
        out = subprocess.check_output(grep_cmd, text=True, stderr=subprocess.DEVNULL).strip()
        if out:
            return out
    except subprocess.CalledProcessError:
        pass
    except Exception:
        pass

    try:
        tail_cmd = [
            "docker",
            "exec",
            cname,
            "sh",
            "-lc",
            f"tail -n {max_lines} {config.LLMBOOST_LOGS_DIR}/*.log 2>/dev/null",
        ]
        out = subprocess.check_output(tail_cmd, text=True, stderr=subprocess.DEVNULL).strip()
        return out
    except Exception:
        return ""


def do_tune(
    model: str,
    lbh_workspace: Optional[str],
    verbose: bool = False,
    metrics: str = "latency",
    algorithm: str = "mb_algorithm",
    wait_timeout: float = 600.0,
    poll_interval: float = 1.0,
    detached: bool = False,
    gui: bool = False,
    image: Optional[str] = None,
    model_path: Optional[str] = None,
    restart: bool = False,
    n_tuners: Optional[int] = None,
    merge_db: bool = False,
) -> dict:
    """
    Start the autotuner inside the model container and optionally wait.

    Args:
        model: Model identifier.
        lbh_workspace: Optional override for the workspace mount path.
        verbose: If True, echo detailed logs and commands.
        metrics: Primary optimization metric (`latency` or `throughput`).
        algorithm: Autotuning algorithm identifier.
        wait_timeout: Max seconds to wait for completion (ignored when detached).
        poll_interval: Seconds between tuning status checks.
        detached: If True, return right after starting the tuner.
        gui: If True, print diagnostics GUI URL using `config.LBH_GUI_PORT`.
        image: If set, force a specific docker image for the model.
        model_path: If set, local HF model directory to mount inside the container.
        restart: If True, restart the container if it is already running.
        n_tuners: Number of parallel tuners; defaults to GPU count when None.
        merge_db: If True, merge container DB into host and exit (no tuning occurs).

    Returns:
        Dict: {returncode: int, container_name: str, error: str|None}
    """
    cname = container_name_for_model(model)
    # Ensure container is running; otherwise start it via lbh run
    if not is_container_running(cname):
        if verbose:
            click.echo(f"[tune] No running container for {model}; starting via lbh run...")
        # Pass through forced image when provided
        res = do_run(
            model,
            lbh_workspace,
            verbose=verbose,
            image=image,
            model_path=model_path,
            restart=restart,
            docker_args=(),
        )  # use empty docker_args
        if res["returncode"] != 0:
            return {"returncode": res["returncode"], "container_name": "", "error": res["error"]}
        time.sleep(1)
        if not is_container_running(cname):
            return {"returncode": 1, "container_name": "", "error": "Failed to start container."}

    # Optional: print GUI URL hint
    if gui:
        try:
            gui_port = config.LBH_GUI_PORT
            click.echo(f"[tune] Diagnostics GUI: http://localhost:{gui_port}")
        except Exception:
            # Ignore failures to read/format port
            pass

    # Default n_tuners to GPU count if not provided
    if not n_tuners:
        n_tuners = get_gpu_count()

    exec_cmd = [
        "docker",
        "exec",
        "-i",
        cname,
        "llmboost",
        "tuner",
        "--model",
        model,
        "--metrics",
        metrics,
        "--algorithm",
        algorithm,
        "--n-tuners",
        f"{n_tuners}",
    ]

    # In verbose+attached mode, prefer interactive exec to surface logs
    if verbose and not detached:
        # replace `-d` for `-i` in exec_cmd
        exec_cmd = [part if part != "-d" else "-i" for part in exec_cmd]

    if merge_db:
        # Ensure backup directory exists on host
        os.makedirs(os.path.join(config.LBH_HOME, config.TUNER_DB_BACKUPS_DIRNAME), exist_ok=True)
        # Backup host DB before merging
        backup_file = os.path.join(
            config.LBH_HOME,
            config.TUNER_DB_BACKUPS_DIRNAME,
            f"inference.db.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak",
        )  # eg: inference.db.20231123_153045.bak
        shutil.copy2(config.LBH_TUNER_DB_PATH, backup_file)
        click.echo(f"[tune] Backed up host tuner database to {backup_file} before merging.")

        # Replace all args from --model with --merge-db, merging container DB into host DB
        exec_cmd = exec_cmd[: exec_cmd.index("--model")] + [
            "--merge-db",
            f"{config.LLMBOOST_TUNER_DB_BACKUP_PATH}",
        ]
        if verbose:
            click.echo(f"[tune] Merging tuner database: {' '.join(exec_cmd)}")
        subprocess.run(exec_cmd, check=True)
        click.echo("[tune] Merged tuner database from container into host database.")
        # No tuning is performed in merge-db mode
        return {"returncode": 0, "container_name": cname, "error": None}

    if verbose:
        click.echo(f"[tune] Tuning model: {' '.join(exec_cmd)}")

    # Start tuner and handle failures
    start = time.time()
    try:
        # Start the tuner process inside the container (foreground)
        subprocess.run(exec_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {
            "returncode": e.returncode,
            "container_name": cname,
            "error": f"Failed to start tuner inside container (exit {e.returncode})",
        }

    if detached:
        # Return early when running in background
        click.echo("[tune] Tuner started in background (detached).")
        return {"returncode": 0, "container_name": cname, "error": None}

    if not verbose:
        # Poll for completion with minimal feedback
        click.echo(f"[tune] Waiting for tuning to complete (timeout {wait_timeout:.1f}s)...")
        time.sleep(3.0)  # brief pause to let process start
        while (
            is_container_running(cname)
            and is_model_tuning(cname)
            and (time.time() - start < wait_timeout)
        ):
            # Minimal progress feedback
            elapsed = int(time.time() - start)
            if elapsed % 60 == 0:
                click.echo(f"{int(elapsed)}s.", nl=False)
            elif elapsed % 5 == 0:
                click.echo(".", nl=False)
            time.sleep(max(0.1, float(poll_interval)))

        # Handle container unexpectedly stopping
        if not is_container_running(cname):
            return {
                "returncode": 1,
                "container_name": cname,
                "error": "Container stopped during tuning.",
            }
        # Branch: timeout while still tuning, show recent logs
        if is_model_tuning(cname):
            logs = _collect_error_logs(cname, max_lines=200)
            msg = f"Tuning did not complete within {wait_timeout:.1f} seconds.\nNOTE: The tuning process may still be running in the background inside the container. Increase --wait-timeout to wait longer."
            if logs:
                msg += f"\nRecent logs:\n{logs}"
            return {"returncode": 0, "container_name": cname, "error": msg}

    # Completed within timeout
    elapsed = time.time() - start
    click.echo(f"[tune] Tuning finished after {elapsed:.1f} seconds.")
    return {"returncode": 0, "container_name": cname, "error": None}


@click.command(name="tune", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "--lbh-workspace", type=click.Path(), help="Override workspace path mounted inside container."
)
@click.option(
    "--metrics",
    type=click.Choice(["throughput", "latency"]),
    default="throughput",
    show_default=True,
    help="Primary optimization metric.",
)
@click.option(
    "-a",
    "--algorithm",
    type=str,
    default="mb_algorithm",
    show_default=True,
    help="Autotuning algorithm identifier.",
)
@click.option(
    "--wait-timeout",
    default=600.0,
    show_default=True,
    type=float,
    help="Maximum seconds to wait for tuning to complete (ignored in detached mode).",
)
@click.option(
    "--poll-interval",
    default=1.0,
    show_default=True,
    type=float,
    help="Seconds between tuning status checks.",
)
@click.option(
    "-d",
    "--detached",
    is_flag=True,
    help="Do not wait for tuning to complete; return immediately after starting tuner.",
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
@click.option(
    "--gui",
    is_flag=True,
    help="Print localhost URL for diagnostics GUI.",
)
@click.option(
    "-n",
    "--n-tuners",
    type=str,
    default=None,
    help="Number of parallel tuners to run (defaults to number of GPUs detected).",
)
@click.option(
    "--merge-db",
    is_flag=True,
    type=bool,
    help="Merge container DB into existing DB on host. (no tuning is performed when this flag is set)",
)
@click.pass_context
def tune(
    ctx,
    model,
    lbh_workspace,
    metrics,
    algorithm,
    wait_timeout,
    poll_interval,
    detached,
    forced_image,
    model_path,
    restart,
    gui,
    n_tuners,
    merge_db,
):
    """
    Start autotuning for a given model inside its container.
    """
    verbose = ctx.obj.get("VERBOSE", False)

    # Restart if requested
    if restart:
        stop_res = do_stop(model, None, verbose=verbose)
        if stop_res["returncode"] != 0:
            if is_container_running(container_name_for_model(model)):
                raise click.ClickException(
                    stop_res.get("error") or "Failed to stop existing container"
                )

    res = do_tune(
        model=model,
        lbh_workspace=lbh_workspace,
        verbose=verbose,
        metrics=metrics,
        algorithm=algorithm,
        wait_timeout=wait_timeout,
        poll_interval=poll_interval,
        detached=detached,
        gui=gui,
        image=forced_image,
        model_path=model_path,
        restart=restart,
        n_tuners=n_tuners,
        merge_db=merge_db,
    )
    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Tune failed")
