"""
Remove model deployments from Kubernetes cluster.
"""

import logging
from typing import Optional, List

import click

from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    namespace_exists,
    run_kubectl,
)
from llmboost_hub.utils.kube_utils import sanitize_model_name

log = logging.getLogger("CLUSTER_REMOVE")


def do_remove(
    models: List[str],
    all_models: bool = False,
    force: bool = False,
    kubeconfig: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """
    Remove model deployments from Kubernetes cluster.

    Args:
        models: List of model names to remove.
        all_models: If True, remove all model deployments.
        force: If True, forcefully delete pods by clearing finalizers.
        kubeconfig: Optional path to kubeconfig file.
        verbose: If True, show detailed output.

    Returns:
        Dict with status, error, removed_count, failed_count, and removals keys.
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
            "error": f"Namespace '{config.LBH_KUBE_NAMESPACE}' does not exist. LLMBoost cluster not installed.",
        }

    # Get list of deployments to remove
    deployments_to_remove = []

    if all_models:
        # Get all LLMBoostDeployment resources
        try:
            result = run_kubectl(
                [
                    "get",
                    config.KUBE_CRD_RESOURCE_NAME,
                    "-n",
                    config.LBH_KUBE_NAMESPACE,
                    "-o",
                    "name",
                ],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            deployments_to_remove = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to list deployments: {e}",
            }
    else:
        # Convert model names to deployment names
        for model in models:
            # Use the same sanitize_model_name function used during deployment
            deployment_name = sanitize_model_name(model)
            deployments_to_remove.append(f"llmboostdeployment.mangoboost.io/{deployment_name}")

    if not deployments_to_remove:
        return {
            "status": "success",
            "removed_count": 0,
            "failed_count": 0,
            "removals": [],
            "message": "No deployments found to remove",
        }

    # Remove deployments
    removed_count = 0
    failed_count = 0
    removal_results = []

    for deployment in deployments_to_remove:
        # Extract deployment name from resource reference format (e.g., "<resource>.<group>/name")
        deployment_name = deployment.split("/")[-1] if "/" in deployment else deployment
        result = {"deployment": deployment_name, "status": "pending"}

        try:
            run_kubectl(
                ["delete", deployment, "-n", config.LBH_KUBE_NAMESPACE],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            result["status"] = "removed"
            removed_count += 1
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            failed_count += 1

        removal_results.append(result)

    # If force flag is set, forcefully delete any remaining pods
    if force:
        try:
            # Get all pods with llmboost/deployment-group-name label
            pod_result = run_kubectl(
                [
                    "get",
                    "pods",
                    "-n",
                    config.LBH_KUBE_NAMESPACE,
                    "-l",
                    "llmboost/deployment-group-name",
                    "-o",
                    "jsonpath={.items[*].metadata.name}",
                ],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )

            pods = pod_result.stdout.strip().split() if pod_result.stdout.strip() else []

            for pod_name in pods:
                try:
                    # Remove finalizers
                    run_kubectl(
                        [
                            "patch",
                            "pod",
                            pod_name,
                            "-n",
                            config.LBH_KUBE_NAMESPACE,
                            "-p",
                            '{"metadata":{"finalizers":null}}',
                            "--type=merge",
                        ],
                        kubeconfig=kubeconfig,
                        check=False,  # Don't fail if patch fails
                        verbose=verbose,
                    )

                    # Force delete with zero grace period
                    run_kubectl(
                        [
                            "delete",
                            "pod",
                            pod_name,
                            "-n",
                            config.LBH_KUBE_NAMESPACE,
                            "--grace-period=0",
                            "--force",
                        ],
                        kubeconfig=kubeconfig,
                        check=False,  # Don't fail if delete fails
                        verbose=verbose,
                    )
                except Exception as e:
                    if verbose:
                        log.warning(f"Failed to force delete pod {pod_name}: {e}")
        except Exception as e:
            if verbose:
                log.warning(f"Failed to list pods for forced deletion: {e}")

    return {
        "status": "success" if removed_count > 0 else "error",
        "error": "No deployments were removed successfully" if removed_count == 0 else None,
        "removed_count": removed_count,
        "failed_count": failed_count,
        "removals": removal_results,
    }


@click.command(name="remove")
@click.argument("models", nargs=-1)
@click.option(
    "-A",
    "--all",
    "all_models",
    is_flag=True,
    help="Remove all model deployments",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force deletion by clearing finalizers and using zero grace period",
)
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def remove(
    ctx: click.Context, models: tuple, all_models: bool, force: bool, kubeconfig: Optional[str]
):
    """
    Remove model deployments from Kubernetes cluster.

    Remove specific models by name or all models with --all flag.

    Examples:
        lbh cluster remove facebook/opt-125m
        lbh cluster remove facebook/opt-125m meta-llama/Llama-3.2-1B-Instruct
        lbh cluster remove --all
    """
    verbose = ctx.obj.get("VERBOSE", False)

    # Validate arguments
    if not all_models and not models:
        raise click.ClickException("Either specify model names or use --all flag")

    if all_models and models:
        raise click.ClickException("Cannot specify model names when using --all flag")

    # Confirmation prompt for --all (skip if force is set)
    if all_models and not force:
        click.echo(
            f"\n{click.style('Warning:', fg='yellow', bold=True)} This will remove ALL model deployments in namespace '{config.LBH_KUBE_NAMESPACE}'."
        )
        if not click.confirm("Do you want to continue?", default=False):
            click.echo("Operation cancelled.")
            return

    result = do_remove(
        models=list(models),
        all_models=all_models,
        force=force,
        kubeconfig=kubeconfig,
        verbose=verbose,
    )

    if result["status"] == "error" and result.get("error"):
        raise click.ClickException(result["error"])

    # Display progress
    if result.get("message"):
        click.secho(result["message"], fg="yellow")
        return

    click.echo(f"\nRemoving model deployments from namespace {config.LBH_KUBE_NAMESPACE}")

    # Display per-deployment results
    for removal_result in result["removals"]:
        deployment = removal_result["deployment"]
        click.echo(f"\n  Processing: {deployment}")

        if removal_result["status"] == "removed":
            click.secho(f"    Removed successfully", fg="green")
        else:
            click.secho(f"    {removal_result.get('error', 'Failed')}", fg="red")

    # Summary
    click.echo(f"\n{click.style('Removal Summary:', fg='cyan', bold=True)}")
    click.echo(f"  Successfully removed: {click.style(str(result['removed_count']), fg='green')}")
    if result["failed_count"] > 0:
        click.echo(f"  Failed: {click.style(str(result['failed_count']), fg='red')}")

    if result["removed_count"] > 0:
        click.echo(f"\n{click.style('Model deployments removed!', fg='green', bold=True)}")
        click.echo(f"\nCheck remaining deployments:")
        click.echo(f"  lbh cluster status")
