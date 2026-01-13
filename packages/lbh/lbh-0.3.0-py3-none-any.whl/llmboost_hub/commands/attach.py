import click
import subprocess

from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
)
from llmboost_hub.commands.completions import complete_model_names


def do_attach(model: str | None, container: str | None, verbose: bool = False) -> dict:
    """
    Attach to a running container and open an interactive shell (bash -> sh fallback).

    Args:
        model: Model identifier used to derive container name when 'container' is not provided.
        container: Explicit container name to attach to.
        verbose: If True, echo informative messages.

    Returns:
        Dict: {returncode: int, container_name: str, error: str|None}
    """
    cname = container or (container_name_for_model(model) if model else None)
    if not cname:
        return {"returncode": 1, "container_name": "", "error": "No model or container specified."}

    # Early return if target is not running
    if not is_container_running(cname):
        return {
            "returncode": 1,
            "container_name": cname,
            "error": f"Container '{cname}' is not running.",
        }

    # Prefer bash; fall back to sh on failure
    exec_cmd = ["docker", "exec", "-it", cname, "bash"]
    if verbose:
        click.echo(f"[attach] Opening shell in container '{cname}'...")
    try:
        subprocess.run(exec_cmd, check=True)
        return {"returncode": 0, "container_name": cname, "error": None}
    except subprocess.CalledProcessError:
        exec_cmd = ["docker", "exec", "-it", cname, "/bin/sh"]
        try:
            subprocess.run(exec_cmd, check=True)
            return {"returncode": 0, "container_name": cname, "error": None}
        except subprocess.CalledProcessError as e:
            return {
                "returncode": e.returncode,
                "container_name": cname,
                "error": f"Attach failed (exit {e.returncode})",
            }


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=False, shell_complete=complete_model_names)
@click.option(
    "-c",
    "--container",
    "container",
    type=str,
    help="Container name to attach to (overrides model).",
)
@click.pass_context
def attach(ctx: click.Context, model, container):
    """
    Attach to a running model container and open a shell.

    Equivalent to 'docker exec -it <container> bash'.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    res = do_attach(model, container, verbose=verbose)
    if res["returncode"] != 0:
        raise click.ClickException(res["error"] or "Attach failed")
