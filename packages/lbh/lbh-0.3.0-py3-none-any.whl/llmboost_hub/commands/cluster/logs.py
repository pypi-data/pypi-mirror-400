"""
View logs from model or management pods.
"""

import logging
from typing import Optional, List

import click

from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    namespace_exists,
    get_pods_status,
    run_kubectl,
)

log = logging.getLogger("CLUSTER_LOGS")


def do_logs(
    models: bool,
    management: bool,
    tail_args: tuple = (),
    grep_args: tuple = (),
    awk_args: tuple = (),
    kubeconfig: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """
    Execute tail/grep/awk commands on /workspace/logs/* inside pods.

    Args:
        models: If True, execute on model pods.
        management: If True, execute on management pods.
        tail_args: Additional arguments to pass to tail command.
        grep_args: Additional arguments to pass to grep command.
        awk_args: Additional arguments to pass to awk command.
        kubeconfig: Optional path to kubeconfig file.
        verbose: If True, show detailed output.

    Returns:
        Dict with status, error, and results keys.
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

    # Get all pods
    all_pods = get_pods_status(config.LBH_KUBE_NAMESPACE, kubeconfig)

    # Filter pods based on flags
    target_pods = []

    for pod in all_pods:
        labels = pod.get("labels", {})
        if not isinstance(labels, dict):
            labels = {}

        # Model pods have llmboost/deployment-group-name label
        model_name = labels.get("llmboost/deployment-group-name")

        if models and model_name:
            target_pods.append(pod)
        elif management and not model_name:
            target_pods.append(pod)

    if not target_pods:
        return {
            "status": "success",
            "message": "No pods found matching the criteria",
            "results": [],
        }

    # Execute commands on all target pods
    results = []

    # For management pods, show kubectl logs with optional filtering
    if management and not models:
        # Determine if we need to apply tail/grep/awk
        has_filters = tail_args or grep_args or awk_args

        for pod in target_pods:
            pod_name = pod.get("name", "")

            try:
                # Get kubectl logs
                result = run_kubectl(
                    ["logs", pod_name, "-n", config.LBH_KUBE_NAMESPACE, "--all-containers=true"],
                    kubeconfig=kubeconfig,
                    verbose=verbose,
                )

                logs_output = result.stdout if result.stdout else ""

                # Apply filtering if specified
                if has_filters and logs_output:
                    import subprocess

                    if tail_args:
                        cmd = ["tail"] + list(tail_args)
                    elif grep_args:
                        cmd = ["grep"] + list(grep_args)
                    elif awk_args:
                        cmd = ["awk"] + list(awk_args)
                    else:
                        cmd = None

                    if cmd:
                        try:
                            filter_result = subprocess.run(
                                cmd,
                                input=logs_output,
                                capture_output=True,
                                text=True,
                            )
                            logs_output = (
                                filter_result.stdout if filter_result.stdout else logs_output
                            )
                        except Exception:
                            pass  # Use original logs if filtering fails

                results.append(
                    {
                        "pod": pod_name,
                        "status": "success",
                        "type": "kubectl_logs",
                        "stdout": logs_output,
                        "stderr": result.stderr if result.stderr else "",
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "pod": pod_name,
                        "status": "error",
                        "type": "kubectl_logs",
                        "error": str(e),
                    }
                )

        return {
            "status": "success",
            "results": results,
            "command": "kubectl logs",
            "management_only": True,
        }

    # For model pods, show kubectl logs first, then workspace logs
    for pod in target_pods:
        pod_name = pod.get("name", "")

        # First, get kubectl logs
        try:
            kubectl_result = run_kubectl(
                ["logs", pod_name, "-n", config.LBH_KUBE_NAMESPACE, "--all-containers=true"],
                kubeconfig=kubeconfig,
                verbose=verbose,
            )

            results.append(
                {
                    "pod": pod_name,
                    "status": "success",
                    "type": "kubectl_logs",
                    "stdout": kubectl_result.stdout if kubectl_result.stdout else "",
                    "stderr": kubectl_result.stderr if kubectl_result.stderr else "",
                }
            )
        except Exception as e:
            results.append(
                {
                    "pod": pod_name,
                    "status": "error",
                    "type": "kubectl_logs",
                    "error": str(e),
                }
            )

        # Then, run tail/grep/awk on /workspace/logs/*
        # Determine which command to run
        if tail_args:
            command = "tail"
            args = list(tail_args)
        elif grep_args:
            command = "grep"
            args = list(grep_args)
        elif awk_args:
            command = "awk"
            args = list(awk_args)
        else:
            # Default: tail last 10 lines
            command = "tail"
            args = ["-n", "10"]

        shell_command = f"{command} {' '.join(args)} /workspace/logs/*"

        try:
            workspace_result = run_kubectl(
                [
                    "exec",
                    pod_name,
                    "-n",
                    config.LBH_KUBE_NAMESPACE,
                    "--",
                    "sh",
                    "-c",
                    shell_command,
                ],
                kubeconfig=kubeconfig,
                verbose=verbose,
            )

            results.append(
                {
                    "pod": pod_name,
                    "status": "success",
                    "type": "workspace_logs",
                    "command": f"{command} {' '.join(args)}",
                    "stdout": workspace_result.stdout if workspace_result.stdout else "",
                    "stderr": workspace_result.stderr if workspace_result.stderr else "",
                }
            )
        except Exception as e:
            results.append(
                {
                    "pod": pod_name,
                    "status": "error",
                    "type": "workspace_logs",
                    "command": f"{command} {' '.join(args)}",
                    "error": str(e),
                }
            )

    return {
        "status": "success",
        "results": results,
    }


@click.command(name="logs")
@click.option(
    "--models",
    is_flag=True,
    help="Execute on model deployment pods (default)",
)
@click.option(
    "--management",
    is_flag=True,
    help="Execute on management/monitoring pods",
)
@click.option(
    "--tail",
    multiple=True,
    help="Arguments to pass to tail command (e.g., --tail -n --tail 20)",
)
@click.option(
    "--grep",
    multiple=True,
    help="Arguments to pass to grep command (e.g., --grep -i --grep error)",
)
@click.option(
    "--awk",
    multiple=True,
    help="Arguments to pass to awk command",
)
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def logs(
    ctx,
    models: bool,
    management: bool,
    tail: tuple,
    grep: tuple,
    awk: tuple,
    kubeconfig: Optional[str],
):
    """
    View logs from /workspace/logs/* inside model or management pods.

    Executes tail, grep, or awk commands on log files inside pods.
    By default, shows last 10 lines from model pods.

    Examples:
        lbh cluster logs
        lbh cluster logs --tail -n --tail 20
        lbh cluster logs --grep -i --grep error
        lbh cluster logs --management
        lbh cluster logs --models --management --tail -f
    """
    verbose = ctx.obj.get("VERBOSE", False)

    # If neither models nor management specified, default to models only
    if not models and not management:
        models = True

    # Validate: only one command type can be specified
    command_count = sum([bool(tail), bool(grep), bool(awk)])
    if command_count > 1:
        raise click.ClickException("Only one of --tail, --grep, or --awk can be specified")

    result = do_logs(
        models=models,
        management=management,
        tail_args=tail,
        grep_args=grep,
        awk_args=awk,
        kubeconfig=kubeconfig,
        verbose=verbose,
    )

    if result["status"] == "error" and result.get("error"):
        raise click.ClickException(result["error"])

    if result.get("message"):
        click.secho(result["message"], fg="yellow")
        return

    # Check if this is management-only mode
    if result.get("management_only"):
        # Display as table for management logs
        from tabulate import tabulate
        import shutil

        terminal_width = shutil.get_terminal_size().columns
        # Reserve space for pod name column and table borders
        max_log_width = max(50, terminal_width - 40)

        table_data = []
        for pod_result in result["results"]:
            pod_name = pod_result["pod"]

            if pod_result["status"] == "error":
                last_log = click.style(
                    f"Error: {pod_result.get('error', 'Unknown error')}", fg="red"
                )
            else:
                logs = pod_result.get("stdout", "")
                if logs:
                    # Get the last non-empty line
                    lines = [line for line in logs.splitlines() if line.strip()]
                    if lines:
                        last_log = lines[-1]
                        # Truncate if too long
                        if len(last_log) > max_log_width:
                            last_log = last_log[: max_log_width - 3] + "..."
                    else:
                        last_log = click.style("(no logs)", fg="yellow")
                else:
                    last_log = click.style("(no logs)", fg="yellow")

            table_data.append([pod_name, last_log])

        click.echo()
        click.echo(tabulate(table_data, headers=["Pod", "Last Log"], tablefmt="simple"))
        click.echo()
        return

    # Display results grouped by pod
    click.echo()

    # Group results by pod
    pods_data = {}
    for pod_result in result["results"]:
        pod_name = pod_result["pod"]
        if pod_name not in pods_data:
            pods_data[pod_name] = []
        pods_data[pod_name].append(pod_result)

    # Display each pod's logs
    for pod_name, pod_results in pods_data.items():
        click.echo(f"{click.style('Pod:', fg='cyan', bold=True)} {pod_name}")
        click.echo()

        for pod_result in pod_results:
            log_type = pod_result.get("type", "")

            if pod_result["status"] == "error":
                error_label = (
                    "kubectl logs"
                    if log_type == "kubectl_logs"
                    else pod_result.get("command", "workspace logs")
                )
                click.secho(
                    f"  Error ({error_label}): {pod_result.get('error', 'Unknown error')}", fg="red"
                )
                continue

            # Show label for the log type
            if log_type == "kubectl_logs":
                click.echo(f"  {click.style('kubectl logs:', fg='yellow')}")
            elif log_type == "workspace_logs":
                command = pod_result.get("command", "")
                click.echo(f"  {click.style(f'/workspace/logs/* ({command}):', fg='yellow')}")

            # Display stdout
            if pod_result.get("stdout"):
                # Indent the output
                for line in pod_result["stdout"].splitlines():
                    click.echo(f"    {line}")

            # Display stderr (always forward as-is)
            if pod_result.get("stderr"):
                for line in pod_result["stderr"].splitlines():
                    click.echo(f"    {line}", err=True)

            click.echo()

        click.echo("---")
        click.echo()
