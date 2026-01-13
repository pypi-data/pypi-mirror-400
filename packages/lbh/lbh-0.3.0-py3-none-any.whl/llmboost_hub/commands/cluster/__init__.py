"""
Main cluster command group for multi-node deployment orchestration.
"""

import click
from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import get_cluster_secrets, print_cluster_secrets

from llmboost_hub.commands.cluster import (
    install,
    deploy,
    uninstall,
    status,
    remove,
    logs,
)
from llmboost_hub.commands.cluster.set_docker_config import do_set_docker_config


@click.group(name="cluster", invoke_without_command=True)
@click.option(
    "--show-secrets",
    is_flag=True,
    help="Display secrets for accessing management and monitoring endpoints",
)
@click.option(
    "--set-docker-config",
    type=click.Path(exists=True),
    default=None,
    help=f"Path to Docker config.json file (default: {config.LBH_DOCKER_CONFIG})",
)
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def cluster(ctx: click.Context, show_secrets: bool, set_docker_config: str, kubeconfig: str):
    """
    Orchestrate multi-node LLMBoost deployments using Kubernetes and Helm.

    Manage cluster-wide model deployments across multiple nodes with automatic
    load balancing, monitoring, and resource allocation.
    """
    # Store flags in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["SHOW_SECRETS"] = show_secrets

    # If no subcommand provided, check for flags and show appropriate message
    if ctx.invoked_subcommand is None:
        if show_secrets:
            print_cluster_secrets(
                get_cluster_secrets(namespace=config.LBH_KUBE_NAMESPACE, kubeconfig=kubeconfig),
                verbose=True,
            )

        # Handle --set-docker-config flag (must run before subcommands)
        if set_docker_config:
            verbose = ctx.obj.get("VERBOSE", False)

            result = do_set_docker_config(
                docker_config_path=set_docker_config,
                kubeconfig=kubeconfig,
                verbose=verbose,
            )

            if result["status"] == "error":
                if "set_docker_config" in result and "not found" in result.get("error", ""):
                    click.secho(result["error"], fg="red")
                    click.echo(
                        f"\nPlease authenticate with Docker Hub by running: docker login -u <your_docker_username>"
                    )
                raise click.ClickException(result["error"])

            from llmboost_hub.utils.config import config as lbh_config

            click.secho(
                f"Docker registry secret '{lbh_config.KUBE_DOCKER_REGISTRY_SECRET_NAME}' created successfully",
                fg="green",
                bold=True,
            )
            if verbose:
                click.echo(f"Using Docker config from: {result['docker_config_path']}")

            # Exit after handling the flag
            ctx.exit(0)


# Register subcommands
cluster.add_command(install.install)
cluster.add_command(deploy.deploy)
cluster.add_command(remove.remove)
cluster.add_command(uninstall.uninstall)
cluster.add_command(status.status)
cluster.add_command(logs.logs)
