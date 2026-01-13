import click
import subprocess
import time

from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
)
from llmboost_hub.commands.completions import complete_model_names


def do_stop(model: str, container: str | None, verbose: bool = False) -> dict:
    """
    Stop the model's container.

    Args:
        model: Model identifier (used when container is not directly provided).
        container: Optional explicit container name to stop.
        verbose: If True, echo the docker command.

    Returns:
        Dict: {returncode: int, container_name: str, error: str|None}
    """
    cname = container or container_name_for_model(model)

    # Fast-fail if target container is not running
    if not is_container_running(cname):
        return {
            "returncode": 1,
            "container_name": cname,
            "error": f"Container '{cname}' is not running.",
        }
    cmd = ["docker", "stop", cname]
    if verbose:
        click.echo("[stop] " + " ".join(cmd))

    # Track if docker stop returned an error
    docker_error = None
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        docker_error = e.returncode
        if verbose:
            click.echo(
                f"[stop] docker stop returned exit code {e.returncode}, checking actual container state..."
            )

    # Verify container actually stopped (even if docker returned an error)
    # Docker sometimes throws "did not receive an exit event" but container is actually stopped
    time.sleep(0.5)  # brief pause to let state update
    if not is_container_running(cname):
        # Container successfully stopped
        return {"returncode": 0, "container_name": cname, "error": None}

    # Container is still running - this is a real failure
    return {
        "returncode": docker_error or 1,
        "container_name": cname,
        "error": (
            f"Docker stop failed - container is still running (docker exit code: {docker_error})"
            if docker_error
            else "Container is still running"
        ),
    }


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "-c", "--container", "container", type=str, help="Container name to stop (overrides model)."
)
@click.pass_context
def stop(ctx: click.Context, model, container):
    """
    Stops a running container for a given model (or explicit name).
    """
    verbose = ctx.obj.get("VERBOSE", False)
    res = do_stop(model, container, verbose=verbose)
    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Stop failed")
