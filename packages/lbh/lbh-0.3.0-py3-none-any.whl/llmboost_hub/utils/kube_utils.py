"""
Kubernetes and Helm utilities for cluster management.
"""

import json
import logging
import os
import subprocess
import base64
from typing import Optional, Dict, List, Tuple
from llmboost_hub.utils.config import config

import click

log = logging.getLogger("KUBE_UTILS")


def check_command_available(command: str) -> bool:
    """
    Check if a command is available in the system PATH.

    Args:
        command: Command name to check.

    Returns:
        True if command is available, False otherwise.
    """
    try:
        subprocess.run(
            ["which", command],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def verify_prerequisites() -> Tuple[bool, List[str]]:
    """
    Verify that required tools (kubectl, helm, docker) are installed.

    Returns:
        Tuple of (all_available, missing_tools).
    """
    required = ["kubectl", "helm", "docker"]
    missing = [cmd for cmd in required if not check_command_available(cmd)]
    return len(missing) == 0, missing


def verify_cluster_running(kubeconfig: Optional[str] = None) -> Tuple[bool, str]:
    """
    Verify that a Kubernetes cluster is accessible.

    Args:
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        Tuple of (is_running, message).
    """
    cmd = ["kubectl", "cluster-info"]
    env = os.environ.copy()
    if kubeconfig:
        env["KUBECONFIG"] = kubeconfig

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
        )
        return True, "Cluster is running"
    except subprocess.CalledProcessError as e:
        return False, f"Cluster not accessible: {e.stderr.strip()}"


def run_kubectl(
    args: List[str],
    kubeconfig: Optional[str] = None,
    check: bool = True,
    capture_output: bool = True,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run a kubectl command with optional kubeconfig.

    Args:
        args: kubectl command arguments.
        kubeconfig: Optional path to kubeconfig file.
        check: Whether to raise exception on non-zero exit.
        capture_output: Whether to capture stdout/stderr.

    Returns:
        CompletedProcess instance.
    """
    cmd = ["kubectl"] + args
    env = os.environ.copy()
    if kubeconfig:
        env["KUBECONFIG"] = kubeconfig

    if verbose:
        click.echo(f"Running kubectl command: {' '.join(cmd)}")

    return subprocess.run(
        cmd,
        check=check,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
        env=env,
        text=True,
    )


def run_helm(
    args: List[str],
    kubeconfig: Optional[str] = None,
    check: bool = True,
    capture_output: bool = True,
    verbose: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run a helm command with optional kubeconfig.

    Args:
        args: helm command arguments.
        kubeconfig: Optional path to kubeconfig file.
        check: Whether to raise exception on non-zero exit.
        capture_output: Whether to capture stdout/stderr.

    Returns:
        CompletedProcess instance.
    """
    cmd = ["helm"] + args
    env = os.environ.copy()
    if kubeconfig:
        env["KUBECONFIG"] = kubeconfig

    if verbose:
        click.echo(f"Running helm command: {' '.join(cmd)}")

    return subprocess.run(
        cmd,
        check=check,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
        env=env,
        text=True,
    )


def detect_gpu_types(kubeconfig: Optional[str] = None) -> List[str]:
    """
    Detect available GPU types in the cluster by checking node labels.

    Args:
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        List of detected GPU types ('nvidia', 'amd', or both).
    """
    gpu_types = set()

    try:
        # Check for NVIDIA GPUs
        result = run_kubectl(
            ["get", "nodes", "-o", "json"],
            kubeconfig=kubeconfig,
        )
        nodes_data = json.loads(result.stdout)

        for node in nodes_data.get("items", []):
            labels = node.get("metadata", {}).get("labels", {})
            status = node.get("status", {})
            capacity = status.get("capacity", {})
            allocatable = status.get("allocatable", {})

            # Check for NVIDIA GPU resources
            if "nvidia.com/gpu" in capacity or "nvidia.com/gpu" in allocatable:
                gpu_types.add("nvidia")

            # Check for AMD GPU resources
            if "amd.com/gpu" in capacity or "amd.com/gpu" in allocatable:
                gpu_types.add("amd")

            # Also check node labels for GPU vendor info
            for label_key in labels:
                if "nvidia" in label_key.lower():
                    gpu_types.add("nvidia")
                if "amd" in label_key.lower() or "radeon" in label_key.lower():
                    gpu_types.add("amd")

    except Exception as e:
        log.warning(f"Failed to detect GPU types: {e}")

    return sorted(list(gpu_types))


def namespace_exists(namespace: str, kubeconfig: Optional[str] = None) -> bool:
    """
    Check if a Kubernetes namespace exists.

    Args:
        namespace: Namespace name.
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        True if namespace exists, False otherwise.
    """
    try:
        run_kubectl(
            ["get", "namespace", namespace],
            kubeconfig=kubeconfig,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def sanitize_model_name(name: str) -> str:
    """
    Sanitize a name to comply with Kubernetes DNS-1035 label requirements.

    DNS-1035 label rules:
    - Must consist of lower case alphanumeric characters or '-'
    - Must start with an alphabetic character
    - Must end with an alphanumeric character
    - Maximum length of 63 characters

    Args:
        name: Input name to sanitize.

    Returns:
        Sanitized name compliant with DNS-1035.
    """
    import re

    # Convert to lowercase and replace slashes with hyphens
    sanitized = name.lower().replace("/", "--")

    # Replace any non-alphanumeric characters (except hyphens) with hyphens
    sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)

    # Ensure it starts with an alphabetic character
    # If it starts with a digit or hyphen, prefix with 'model-'
    if not sanitized or not sanitized[0].isalpha():
        sanitized = "model-" + sanitized

    # Ensure it ends with an alphanumeric character
    sanitized = sanitized.rstrip("-")

    # Truncate to 63 characters (DNS label limit)
    if len(sanitized) > 63:
        sanitized = sanitized[:63].rstrip("-")

    return sanitized


def get_service_endpoints(
    namespace: str, kubeconfig: Optional[str] = None
) -> Dict[str, Dict[str, str]]:
    """
    Get service endpoints in a namespace.

    Args:
        namespace: Namespace to query.
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        Dict mapping service name to endpoint information.
    """
    endpoints = {}

    try:
        result = run_kubectl(
            ["get", "services", "-n", namespace, "-o", "json"],
            kubeconfig=kubeconfig,
        )
        services_data = json.loads(result.stdout)

        for svc in services_data.get("items", []):
            name = svc.get("metadata", {}).get("name", "")
            spec = svc.get("spec", {})
            svc_type = spec.get("type", "ClusterIP")
            ports = spec.get("ports", [])

            endpoint_info = {
                "type": svc_type,
                "cluster_ip": spec.get("clusterIP", ""),
                "ports": [],
            }

            for port in ports:
                port_info = {
                    "port": port.get("port"),
                    "target_port": port.get("targetPort"),
                    "protocol": port.get("protocol", "TCP"),
                }
                if "nodePort" in port:
                    port_info["node_port"] = port["nodePort"]
                endpoint_info["ports"].append(port_info)

            # Get external IPs if LoadBalancer
            if svc_type == "LoadBalancer":
                status = svc.get("status", {})
                ingress = status.get("loadBalancer", {}).get("ingress", [])
                external_ips = []
                for ing in ingress:
                    if "ip" in ing:
                        external_ips.append(ing["ip"])
                    elif "hostname" in ing:
                        external_ips.append(ing["hostname"])
                endpoint_info["external_ips"] = external_ips

            endpoints[name] = endpoint_info

    except Exception as e:
        log.warning(f"Failed to get service endpoints: {e}")

    return endpoints


@staticmethod
def get_cluster_secrets_format() -> Dict[str, Dict[str, str] | str]:
    """
    Kubernetes secrets format for LLMBoost cluster.
    Maps display label to Kubernetes secret path (secret-name.key).

    Secret names match actual Helm chart deployed resources:
    - headlamp-admin: Created directly in management_ui.yaml
    - llmboost-grafana: Created by kube-prometheus-stack subchart

    Format: "Display Label": "secret-name.key" or {"Field": "secret-name.key"}
    """

    return {
        "Management UI": f"{config.LBH_HELM_RELEASE_NAME}-headlamp-admin.token",
        "Monitoring UI": {
            "Username": f"{config.LBH_HELM_RELEASE_NAME}-grafana.admin-user",
            "Password": f"{config.LBH_HELM_RELEASE_NAME}-grafana.admin-password",
        },
    }


def get_cluster_secrets(namespace: str, kubeconfig: Optional[str] = None) -> Dict[str, str]:
    """
    Get LLMBoost cluster secrets using the format from _Constants.

    Args:
        namespace: Kubernetes namespace.
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        Dict mapping display labels to secret values or nested dicts for grouped credentials.
        Example: {"Management UI Token": "eyJh...", "Monitoring UI Credentials": {"Username": "admin", ...}}
    """

    secrets_format = get_cluster_secrets_format()
    result = {}

    try:
        # Get all secrets from namespace
        kube_result = run_kubectl(
            ["get", "secrets", "-n", namespace, "-o", "json"],
            kubeconfig=kubeconfig,
        )
        secrets_data = json.loads(kube_result.stdout)

        # Build a lookup dict: secret-name.key -> decoded value
        secrets_lookup = {}
        for secret in secrets_data.get("items", []):
            secret_name = secret.get("metadata", {}).get("name", "")
            secret_data = secret.get("data", {})

            for key, value in secret_data.items():
                try:
                    decoded = base64.b64decode(value).decode("utf-8")
                    secrets_lookup[f"{secret_name}.{key}"] = decoded
                except Exception:
                    secrets_lookup[f"{secret_name}.{key}"] = ""

        # Map according to secrets_format
        for label, path in secrets_format.items():
            if isinstance(path, dict):
                # Nested credentials (e.g., username + password)
                result[label] = {}
                for field, field_path in path.items():
                    result[label][field] = secrets_lookup.get(field_path, "")
            else:
                # Single credential
                result[label] = secrets_lookup.get(path, "")

    except Exception as e:
        log.warning(f"Failed to get cluster secrets: {e}")

    return result


def print_cluster_secrets(secrets: Dict[str, str], verbose: bool = False) -> None:
    """
    Print cluster secrets in a consistent format.

    Args:
        secrets: Secrets dict from get_cluster_secrets().
        verbose: If True, show full values; if False, mask sensitive data.
    """

    def mask_value(value: str) -> str:
        """Mask a secret value for display."""
        if not value:
            return "<not found>"
        if verbose:
            return value
        if len(value) > 10:
            return f"{value[:4]}...{value[-4:]}"
        return "***"

    click.echo(click.style("Access Credentials:", fg="cyan", bold=True))

    if not secrets:
        click.echo("  No secrets found")
        return

    for label, value in secrets.items():
        click.echo(f"\n  {click.style(label, fg='yellow', bold=True)}:")

        if isinstance(value, dict):
            # Nested credentials
            for field, field_value in value.items():
                click.echo(f"    {field}: {mask_value(field_value)}")
        else:
            # Single value
            click.echo(f"    {mask_value(value)}")

    click.echo()


def get_pods_status(namespace: str, kubeconfig: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Get pod status information in a namespace.

    Args:
        namespace: Namespace to query.
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        List of pod information dicts.
    """
    pods = []

    try:
        result = run_kubectl(
            ["get", "pods", "-n", namespace, "-o", "json"],
            kubeconfig=kubeconfig,
        )
        pods_data = json.loads(result.stdout)

        for pod in pods_data.get("items", []):
            metadata = pod.get("metadata", {})
            status = pod.get("status", {})

            pod_info = {
                "name": metadata.get("name", ""),
                "labels": metadata.get("labels", {}),
                "status": status.get("phase", "Unknown"),
                "node": status.get("nodeName", ""),
                "pod_ip": status.get("podIP", ""),
            }

            # Get container statuses
            container_statuses = status.get("containerStatuses", [])
            if container_statuses:
                ready = all(cs.get("ready", False) for cs in container_statuses)
                pod_info["ready"] = ready
            else:
                pod_info["ready"] = False

            pods.append(pod_info)

    except Exception as e:
        log.warning(f"Failed to get pod status: {e}")

    return pods
