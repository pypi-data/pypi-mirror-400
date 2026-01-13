"""
Install LLMBoost Helm chart and cluster resources.
"""

import json
import logging
import subprocess
import sys
import os
from typing import Optional

import click

from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    run_helm,
    get_cluster_secrets,
    print_cluster_secrets,
)
from llmboost_hub.commands.cluster.set_docker_config import do_set_docker_config

log = logging.getLogger("CLUSTER_INSTALL")


def do_install(
    kubeconfig: Optional[str] = None,
    extra_helm_args: tuple = (),
    verbose: bool = False,
) -> dict:
    """
    Install LLMBoost Helm chart and cluster infrastructure.

    Args:
        kubeconfig: Optional path to kubeconfig file.
        extra_helm_args: Extra arguments to pass to helm install.
        verbose: If True, show detailed output.

    Returns:
        Dict with status, error, secrets, and config_exists keys.
    """
    # Verify prerequisites
    all_available, missing = verify_prerequisites()
    if not all_available:
        return {
            "status": "error",
            "error": f"Missing required tools: {', '.join(missing)}. Please install kubectl, helm, and docker.",
        }

    if verbose:
        click.secho("All required tools installed", fg="green")

    # Verify cluster is running
    is_running, message = verify_cluster_running(kubeconfig)
    if not is_running:
        return {"status": "error", "error": message}

    if verbose:
        click.secho("Kubernetes cluster is accessible", fg="green")

    # Check if chart is already installed
    try:
        result = run_helm(
            ["list", "-n", config.LBH_KUBE_NAMESPACE, "-o", "json"],
            kubeconfig=kubeconfig,
            check=True,
            verbose=verbose,
        )
        releases = json.loads(result.stdout) if result.stdout else []
        for release in releases:
            if release.get("name") == config.LBH_HELM_RELEASE_NAME:
                return {
                    "status": "error",
                    "error": f"LLMBoost Helm chart is already installed. Use 'lbh cluster status' to check status or 'lbh cluster uninstall' before reinstalling.",
                }
    except subprocess.CalledProcessError:
        # Namespace or release doesn't exist, continue with installation
        pass

    # Check if Helm repository already exists
    try:
        result = run_helm(
            ["repo", "list", "-o", "json"], kubeconfig=kubeconfig, check=True, verbose=verbose
        )
        repos = json.loads(result.stdout) if result.stdout else []
        repo_exists = any(r.get("name") == config.LBH_HELM_REPO_NAME for r in repos)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        repo_exists = False

    # Add Helm repository if it doesn't exist
    if not repo_exists:
        if verbose:
            click.echo(f"\nAdding Helm repository: {config.LBH_HELM_REPO_NAME}")
        try:
            run_helm(
                ["repo", "add", config.LBH_HELM_REPO_NAME, config.LBH_HELM_REPO_URL],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            if verbose:
                click.secho("Helm repository added", fg="green")
        except subprocess.CalledProcessError as e:
            return {"status": "error", "error": f"Failed to add Helm repository: {e.stderr}"}
    elif verbose:
        click.echo(f"\nUpgrading Helm repository '{config.LBH_HELM_REPO_NAME}'")
        try:
            run_helm(
                ["repo", "upgrade", config.LBH_HELM_REPO_NAME],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            if verbose:
                click.secho("Helm repository upgraded", fg="green")
        except subprocess.CalledProcessError as e:
            return {"status": "error", "error": f"Failed to upgrade Helm repository: {e.stderr}"}

    # Update Helm repositories
    if verbose:
        click.echo("\nUpdating Helm repositories")
    try:
        run_helm(["repo", "update"], kubeconfig=kubeconfig, check=True, verbose=verbose)
        if verbose:
            click.secho("Helm repositories updated", fg="green")
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": f"Failed to update Helm repositories: {e.stderr}"}

    # Search and verify chart
    if verbose:
        click.echo(f"\nVerifying chart: {config.LBH_HELM_CHART_NAME}")
    try:
        result = run_helm(
            ["search", "repo", config.LBH_HELM_REPO_NAME],
            kubeconfig=kubeconfig,
            check=True,
            verbose=verbose,
        )
        if config.LBH_HELM_CHART_NAME not in result.stdout:
            return {"status": "error", "error": "Chart not found in repository"}
        if verbose:
            click.secho("Chart found in repository", fg="green")
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": f"Failed to search Helm repository: {e.stderr}"}

    # Install Helm chart
    click.echo(f"Installing chart: {config.LBH_HELM_REPO_NAME}/{config.LBH_HELM_CHART_NAME}")
    click.echo(f"  Namespace: {config.LBH_KUBE_NAMESPACE}")
    click.echo(f"  Release name: {config.LBH_HELM_RELEASE_NAME}")
    click.echo("This may take a few minutes...")

    helm_install_cmd = [
        "install",
        config.LBH_HELM_RELEASE_NAME,
        f"{config.LBH_HELM_REPO_NAME}/{config.LBH_HELM_CHART_NAME}",
        "-n",
        config.LBH_KUBE_NAMESPACE,
        "--create-namespace",
    ]

    # Add extra helm arguments
    if extra_helm_args:
        helm_install_cmd.extend(extra_helm_args)
        if verbose:
            click.echo(f"  Extra args: {' '.join(extra_helm_args)}")

    try:
        result = run_helm(helm_install_cmd, kubeconfig=kubeconfig, check=True, verbose=verbose)
        click.secho("Helm chart installed successfully", fg="green", bold=True)
        if verbose and result.stdout:
            click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "error": f"Failed to install Helm chart: {e.stderr if e.stderr else str(e)}",
        }

    # Get access credentials
    secrets = get_cluster_secrets(config.LBH_KUBE_NAMESPACE, kubeconfig)

    return {
        "status": "success",
        "secrets": secrets,
        "config_exists": os.path.exists(config.LBH_CLUSTER_CONFIG_PATH),
    }


@click.command(name="install")
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.argument("extra_helm_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def install(ctx: click.Context, kubeconfig: Optional[str], extra_helm_args):
    """
    Install LLMBoost Helm chart and cluster infrastructure.

    This command sets up the necessary Kubernetes resources for multi-node
    LLMBoost deployments including the operator, monitoring UI, and ingress.

    Pass additional Helm arguments after -- (e.g., lbh cluster install -- --set foo=bar)

    \b
    Prerequisites:
    - Kubernetes cluster must be running and accessible
    - kubectl, helm, and docker must be installed
    """
    verbose = ctx.obj.get("VERBOSE", False)

    result = do_install(
        kubeconfig=kubeconfig,
        extra_helm_args=extra_helm_args,
        verbose=verbose,
    )

    if result["status"] == "error":
        raise click.ClickException(result["error"])

    # Print access credentials
    click.echo()
    print_cluster_secrets(result["secrets"], verbose=True)

    # Set up Docker registry credentials
    click.echo(f"\n{click.style('Setting up Docker registry credentials...', fg='cyan')}")

    docker_result = do_set_docker_config(
        docker_config_path=None,  # Use default path
        kubeconfig=kubeconfig,
        verbose=verbose,
    )

    if docker_result["status"] == "success":
        click.secho(
            f"Docker registry secret '{config.KUBE_DOCKER_REGISTRY_SECRET_NAME}' created successfully",
            fg="green",
        )
    else:
        click.secho(
            f"Warning: Failed to create Docker registry secret: {docker_result.get('error', 'Unknown error')}",
            fg="yellow",
        )
        click.echo(f"You may need to manually configure it using: lbh cluster set-docker-config")
        if "docker_config_path" in docker_result:
            click.echo(
                f"Please ensure you've run 'docker login' and the config exists at: {docker_result['docker_config_path']}"
            )

    # Check if cluster config exists and auto-deploy
    if result["config_exists"]:
        click.echo(f"\nFound cluster configuration at {config.LBH_CLUSTER_CONFIG_PATH}")
        click.echo("  Running 'lbh cluster deploy' to deploy models...")

        # Import and run deploy command
        from llmboost_hub.commands.cluster.deploy import deploy as deploy_cmd

        ctx.invoke(deploy_cmd, config_file=config.LBH_CLUSTER_CONFIG_PATH, kubeconfig=kubeconfig)
    else:
        click.echo(f"\nNo cluster configuration found at {config.LBH_CLUSTER_CONFIG_PATH}")
        click.echo(f"  Create a configuration file and run 'lbh cluster deploy' to deploy models.")
        click.echo(f"\n  Template: {config.LBH_HOME}/utils/template_cluster_config.jsonc")

    click.echo(f"\n{click.style('LLMBoost cluster installation complete!', fg='green', bold=True)}")

    click.echo(f"\nNext steps:")
    click.echo(f"  1. Create cluster config: {config.LBH_CLUSTER_CONFIG_PATH}")
    click.echo(f"  2. Deploy models: lbh cluster deploy")
    click.echo(f"  3. Check status: lbh cluster status")
