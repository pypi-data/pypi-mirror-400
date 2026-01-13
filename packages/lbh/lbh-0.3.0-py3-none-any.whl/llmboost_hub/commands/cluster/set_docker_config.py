"""
Set Docker registry credentials secret in Kubernetes cluster.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import click

from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    namespace_exists,
    run_kubectl,
)

log = logging.getLogger("CLUSTER_SET_DOCKER_CONFIG")


def do_set_docker_config(
    docker_config_path: Optional[str] = None,
    kubeconfig: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """
    Create or update Docker registry credentials secret in Kubernetes cluster.

    Args:
        docker_config_path: Path to Docker config.json file. Defaults to $HOME/.docker/config.json.
        kubeconfig: Optional path to kubeconfig file.
        verbose: If True, show detailed output.

    Returns:
        Dict with status, error, and secret_created keys.
    """
    # Verify prerequisites
    all_available, missing = verify_prerequisites()
    if not all_available:
        return {
            "status": "error",
            "error": f"Missing required tools: {', '.join(missing)}",
        }

    # Verify cluster is running
    is_running, message = verify_cluster_running(kubeconfig)
    if not is_running:
        return {"status": "error", "error": message}

    # Check if namespace exists
    if not namespace_exists(config.LBH_KUBE_NAMESPACE, kubeconfig):
        return {
            "status": "error",
            "error": f"Namespace '{config.LBH_KUBE_NAMESPACE}' does not exist. Run 'lbh cluster install' first.",
        }

    # Determine Docker config path
    if docker_config_path is None:
        docker_config_path = config.LBH_DOCKER_CONFIG

    if not os.path.exists(docker_config_path):
        return {
            "status": "error",
            "error": f"Docker config file not found at {docker_config_path}. Please run 'docker login' first.",
            "docker_config_path": docker_config_path,
        }

    # Check if secret already exists
    try:
        result = run_kubectl(
            [
                "get",
                "secret",
                config.KUBE_DOCKER_REGISTRY_SECRET_NAME,
                "-n",
                config.LBH_KUBE_NAMESPACE,
            ],
            kubeconfig=kubeconfig,
            check=False,
            verbose=verbose,
        )
        secret_exists = result.returncode == 0

        if secret_exists:
            # Delete existing secret
            if verbose:
                click.echo(
                    f"Deleting existing secret '{config.KUBE_DOCKER_REGISTRY_SECRET_NAME}'..."
                )
            run_kubectl(
                [
                    "delete",
                    "secret",
                    config.KUBE_DOCKER_REGISTRY_SECRET_NAME,
                    "-n",
                    config.LBH_KUBE_NAMESPACE,
                ],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
    except Exception as e:
        log.debug(f"Error checking/deleting existing secret: {e}")

    # Create secret
    try:
        if verbose:
            click.echo(f"Creating Docker registry secret from {docker_config_path}...")

        run_kubectl(
            [
                "create",
                "secret",
                "generic",
                config.KUBE_DOCKER_REGISTRY_SECRET_NAME,
                "-n",
                config.LBH_KUBE_NAMESPACE,
                f"--from-file=.dockerconfigjson={docker_config_path}",
                "--type=kubernetes.io/dockerconfigjson",
            ],
            kubeconfig=kubeconfig,
            check=True,
            verbose=verbose,
        )

        return {
            "status": "success",
            "secret_created": True,
            "docker_config_path": docker_config_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to create Docker registry secret: {e}",
            "docker_config_path": docker_config_path,
        }


@click.command(name="set-docker-config")
@click.option(
    "--docker-config",
    type=click.Path(exists=True),
    default=None,
    help="Path to Docker config.json file (default: $HOME/.docker/config.json)",
)
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def set_docker_config(ctx: click.Context, docker_config: Optional[str], kubeconfig: Optional[str]):
    """
    Create or update Docker registry credentials secret in Kubernetes cluster.

    This command creates a Kubernetes secret containing Docker registry credentials
    from your local Docker config file. This is required to pull private container
    images from Docker Hub or other registries.

    \b
    Prerequisites:
    - Run 'docker login' to authenticate with your registry
    - Kubernetes cluster must be installed ('lbh cluster install')

    Example:
        lbh cluster set-docker-config
        lbh cluster set-docker-config --docker-config /path/to/config.json
    """
    verbose = ctx.obj.get("VERBOSE", False)

    result = do_set_docker_config(
        docker_config_path=docker_config,
        kubeconfig=kubeconfig,
        verbose=verbose,
    )

    if result["status"] == "error":
        if "docker_config_path" in result and "not found" in result.get("error", ""):
            click.secho(result["error"], fg="red")
            click.echo(
                f"\nPlease authenticate with Docker Hub by running: docker login -u <your_docker_username>"
            )
        raise click.ClickException(result["error"])

    click.secho(
        f"Docker registry secret '{config.KUBE_DOCKER_REGISTRY_SECRET_NAME}' created successfully",
        fg="green",
        bold=True,
    )
    if verbose:
        click.echo(f"Using Docker config from: {result['docker_config_path']}")
