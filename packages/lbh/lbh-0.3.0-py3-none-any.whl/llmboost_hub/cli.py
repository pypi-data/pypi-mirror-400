import click

from llmboost_hub.commands import (
    attach,
    cluster,
    completions,
    fetch,
    list as list_cmd,
    login,
    prep,
    run,
    serve,
    status as status_cmd,
    stop,
    test_cmd,
    tune,
)
from importlib import metadata

try:
    pkg_name = "llmboost_hub"
    pkg_version = metadata.version(pkg_name)
except metadata.PackageNotFoundError:
    pkg_name = "lbh"
    pkg_version = metadata.version(pkg_name)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=pkg_version, package_name=pkg_name, message="llmboost_hub (lbh) version %(version)s"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose mode.")
@click.pass_context
def main(ctx: click.Context, verbose):
    """LLMBoost Hub (lbh): Manage LLMBoost model containers and environments to run, serve, and tune large language models."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose


# Register commands
main.add_command(attach.attach)
main.add_command(cluster.cluster)
main.add_command(completions.completions)
main.add_command(fetch.fetch)
main.add_command(list_cmd.list_models)
main.add_command(login.login)
main.add_command(prep.prep)
main.add_command(run.run)
main.add_command(serve.serve)
main.add_command(status_cmd.status_cmd)
main.add_command(stop.stop)
main.add_command(test_cmd.test_cmd)
main.add_command(tune.tune)

if __name__ == "__main__":
    main()
