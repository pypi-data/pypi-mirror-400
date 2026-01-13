import click
import subprocess
import time
from typing import Optional
import socket

from llmboost_hub.commands.run import do_run
from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
    is_model_initializing,
    is_model_ready2serve,
)
from llmboost_hub.utils import gpu_info
from llmboost_hub.commands.stop import do_stop
from llmboost_hub.commands.completions import complete_model_names
from llmboost_hub.utils.config import config


def _collect_error_logs(cname: str, max_lines: int = 200) -> str:
    """
    Return recent error lines from inside the container for diagnosis.

    Strategy:
        - First: grep -i 'error' across `worker*.log` in `config.LLMBOOST_LOGS_DIR` and tail the last `max_lines` lines.
        - Fallback: tail any `*.log` in `config.LLMBOOST_LOGS_DIR`.

    Args:
        cname: Container name.
        max_lines: Maximum lines to return.

    Returns:
        Joined log lines, or empty string when unavailable.
    """
    try:
        logs_dir = config.LLMBOOST_LOGS_DIR
        grep_cmd = [
            "docker",
            "exec",
            cname,
            "sh",
            "-lc",
            f"grep -i 'error' -r {logs_dir}/worker*.log 2>/dev/null | tail -n {max_lines}",
        ]
        out = subprocess.check_output(grep_cmd, text=True, stderr=subprocess.DEVNULL).strip()
        if out:
            return out
    except subprocess.CalledProcessError:
        pass
    except Exception:
        pass

    try:
        logs_dir = config.LLMBOOST_LOGS_DIR
        tail_cmd = [
            "docker",
            "exec",
            cname,
            "sh",
            "-lc",
            f"tail -n {max_lines} {logs_dir}/*.log 2>/dev/null",
        ]
        out = subprocess.check_output(tail_cmd, text=True, stderr=subprocess.DEVNULL).strip()
        return out
    except Exception:
        return ""


def do_serve(
    model: str,
    lbh_workspace: str | None,
    verbose: bool = False,
    host: str = "0.0.0.0",
    port: int = config.LBH_SERVE_PORT,
    wait_timeout: float = 600.0,
    poll_interval: float = 1.0,
    detached: bool = False,
    force: bool = False,
    image: Optional[str] = None,
    model_path: Optional[str] = None,
    restart: bool = False,
    llmboost_args: tuple = (),
) -> dict:
    """
    Start llmboost serve in the container and optionally wait for readiness.

    Args:
        model: Target model identifier.
        lbh_workspace: Optional host path to mount as /user_workspace.
        verbose: If True, echo docker exec command and progress.
        host: Bind address passed to the service.
        port: Bind port passed to the service.
        wait_timeout: Max seconds to wait for readiness (ignored if detached).
        poll_interval: Seconds between readiness checks.
        detached: If True, start and return immediately without polling.
        force: If True, bypass pre-flight GPU utilization guard.
        image: If set, force a specific docker image for the model.
        model_path: If set, local HF model directory to mount inside the container.
        restart: If True, restart the container if it is already running.
        llmboost_args: Extra arguments to pass to llmboost serve command.

    Returns:
        Dict: {returncode: int, container_name: str, error: str|None}
    """

    # Guard: prevent accidental start if GPUs are already in use (unless forced)
    if not force and gpu_info.any_gpu_in_use():
        return {
            "returncode": 1,
            "container_name": "",
            "error": "Detected non-zero GPU utilization (compute or VRAM). Decrease GPU memory utilization or reduce GPU memory used by other processes. Use -f/--force to bypass.",
        }

    cname = container_name_for_model(model)
    if not is_container_running(cname):
        # Start container if missing
        if verbose:
            click.echo(f"[serve] No running container for {model}; starting via lbh run...")
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
            return {
                "returncode": 1,
                "container_name": "",
                "error": "Failed to start container for model.",
            }

    # Launch llmboost serve detached by default; switch to interactive on verbose+attached
    exec_cmd = [
        "docker",
        "exec",
        "-d",
        cname,
        "llmboost",
        "serve",
        "--host",
        host,
        "--port",
        str(port),
        "--model_name",
        model,
    ] + list(llmboost_args or ())

    if verbose and not detached:
        # Replace -d with -i to surface logs interactively during startup
        exec_cmd = [part if part != "-d" else "-i" for part in exec_cmd]

    if verbose:
        click.echo("[tune] Executing inside container:")
        click.echo(" ".join(exec_cmd))

    try:
        subprocess.run(exec_cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {
            "returncode": e.returncode,
            "container_name": cname,
            "error": f"Failed to start service inside container (exit {e.returncode})\n{_collect_error_logs(cname, max_lines=200)}",
        }

    # If detached, return immediately (no readiness polling)
    start = time.time()
    time.sleep(3.0)  # brief pause to let process start

    if detached:
        click.echo(
            f"[serve] Started llmboost serve in background (detached). Not waiting for readiness."
        )
        return {"returncode": 0, "container_name": cname, "error": None}

    click.echo(
        f"[serve] Waiting for server to become ready on {host}:{port} (timeout {wait_timeout:.1f}s)..."
    )

    # Poll until it is no longer initializing or timeout is reached
    while is_model_initializing(cname) and (time.time() - start < wait_timeout):
        elapsed = int(time.time() - start)
        if elapsed % 60 == 0:  # every minute
            click.echo(f"{int(elapsed)}s.", nl=False)
        elif elapsed % 5 == 0:  # every 5 seconds
            click.echo(".", nl=False)
        time.sleep(max(0.1, float(poll_interval)))

    elapsed = time.time() - start
    if is_model_ready2serve(cname, host=host, port=port):
        click.echo(f"[serve] Server is ready after {elapsed:.1f} seconds.")
        return {"returncode": 0, "container_name": cname, "error": None}
    else:
        error_logs = _collect_error_logs(cname, max_lines=200)
        error_msg = f"Server failed to become ready within {wait_timeout:.1f} seconds."
        if error_logs:
            error_msg += f"\nRecent error logs:\n{error_logs}"
        return {"returncode": 1, "container_name": cname, "error": error_msg}


@click.command(
    context_settings={"ignore_unknown_options": True, "help_option_names": ["-h", "--help"]}
)
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "--lbh-workspace", type=click.Path(), help="Override workspace path mounted inside container."
)
@click.option("--host", default="0.0.0.0", show_default=True, help="Host address to bind to.")
@click.option(
    "--port", default=config.LBH_SERVE_PORT, show_default=True, help="Port to bind to.", type=int
)
@click.option(
    "--wait-timeout",
    default=600.0,
    show_default=True,
    type=float,
    help="Maximum seconds to wait for the server to become ready.",
)
@click.option(
    "--poll-interval",
    default=1.0,
    show_default=True,
    type=float,
    help="Seconds between readiness checks.",
)
@click.option(
    "-d",
    "--detached",
    is_flag=True,
    help="Do not wait for server readiness; return immediately after starting serve.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Ignore GPU utilization checks before starting serve.",
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
@click.argument("llmboost_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def serve(
    ctx,
    model,
    lbh_workspace,
    host,
    port,
    wait_timeout,
    poll_interval,
    detached,
    force,
    forced_image,
    model_path,
    restart,
    llmboost_args,
):
    """
    Start llmboost server inside the model container.

    Extra arguments after -- are forwarded to the llmboost serve command.
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

    res = do_serve(
        model,
        lbh_workspace,
        verbose=verbose,
        host=host,
        port=port,
        wait_timeout=wait_timeout,
        poll_interval=poll_interval,
        detached=detached,
        force=force,
        image=forced_image,
        model_path=model_path,
        restart=restart,
        llmboost_args=llmboost_args,
    )
    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Serve failed")
