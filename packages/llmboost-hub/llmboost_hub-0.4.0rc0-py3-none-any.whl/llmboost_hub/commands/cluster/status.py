"""
Display status of LLMBoost cluster deployments.
"""

import logging
import socket
from typing import Optional, List, Dict

import click
from tabulate import tabulate

from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    namespace_exists,
    get_pods_status,
    get_service_endpoints,
    get_cluster_secrets,
    print_cluster_secrets,
    run_kubectl,
)

log = logging.getLogger("CLUSTER_STATUS")


def get_pod_logs(
    pod_name: str,
    namespace: str,
    kubeconfig: Optional[str],
    lines: int = 5,
) -> str:
    """
    Get recent logs from a pod.

    Args:
        pod_name: Name of the pod.
        namespace: Kubernetes namespace.
        kubeconfig: Optional path to kubeconfig file.
        lines: Number of recent log lines to retrieve.

    Returns:
        Log content as string, or error message.
    """
    try:
        result = run_kubectl(
            ["logs", pod_name, "-n", namespace, f"--tail={lines}", "--all-containers=true"],
            kubeconfig=kubeconfig,
        )
        return result.stdout.strip() if result.stdout else ""
    except Exception as e:
        return f"[Error getting logs: {e}]"


def get_pod_restarts(pod_info: Dict) -> int:
    """
    Extract restart count from pod info.

    Args:
        pod_info: Pod information dict from get_pods_status.

    Returns:
        Total restart count across all containers.
    """
    # Note: get_pods_status doesn't currently return restart count
    # We'll need to enhance it or fetch it here
    return 0  # TODO: Implement restart count fetching


def get_pod_message(pod_info: Dict, verbose: bool, kubeconfig: Optional[str]) -> str:
    """
    Get status message for a pod, including logs if not ready.

    Args:
        pod_info: Pod information dict.
        verbose: If True, show more log lines.
        kubeconfig: Optional path to kubeconfig file.

    Returns:
        Status message string.
    """
    if pod_info.get("ready"):
        return "Running"

    # Pod is not ready, get logs
    pod_name = pod_info.get("name", "")
    namespace = config.LBH_KUBE_NAMESPACE
    lines = 5 if verbose else 1

    logs = get_pod_logs(pod_name, namespace, kubeconfig, lines)

    if not logs:
        return f"Status: {pod_info.get('status', 'Unknown')}"

    # Truncate logs for display
    log_lines = logs.split("\n")
    if not verbose and len(log_lines) > 1:
        return log_lines[0][:100]  # First line, max 100 chars
    elif verbose:
        return "\n".join(log_lines)
    else:
        return logs[:100]  # Max 100 chars


def do_status(
    kubeconfig: Optional[str] = None,
    show_secrets: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Get the status of LLMBoost cluster deployments.

    Args:
        kubeconfig: Optional path to kubeconfig file.
        show_secrets: If True, include secrets in response.
        verbose: If True, show full unmasked secrets.

    Returns:
        Dict with status, error, pods, services, secrets, and model_deployments keys.
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
            "error": f"Namespace '{config.LBH_KUBE_NAMESPACE}' does not exist. LLMBoost cluster not installed. Run 'lbh cluster install' first.",
        }

    # Get pods status
    pods = get_pods_status(config.LBH_KUBE_NAMESPACE, kubeconfig)
    services = get_service_endpoints(config.LBH_KUBE_NAMESPACE, kubeconfig)

    # Group pods by model deployment
    model_deployments = {}
    management_pods = []

    for pod in pods:
        labels = pod.get("labels", {})
        if not isinstance(labels, dict):
            labels = {}
        pod_name = pod.get("name", "")

        # Check if it's a model deployment pod (has llmboost/deployment-group-name label)
        model_name = labels.get("llmboost/deployment-group-name")
        if model_name:
            if model_name not in model_deployments:
                model_deployments[model_name] = []
            model_deployments[model_name].append(pod)
        else:
            # Management/monitoring pods
            management_pods.append(pod)

    # Get secrets if requested
    secrets = {}
    if show_secrets or verbose:
        secrets = get_cluster_secrets(config.LBH_KUBE_NAMESPACE, kubeconfig)

    return {
        "status": "success",
        "pods": pods,
        "services": services,
        "secrets": secrets,
        "model_deployments": model_deployments,
        "management_pods": management_pods,
    }


@click.command(name="status")
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def status(ctx: click.Context, kubeconfig: Optional[str]):
    """
    Display the status of LLMBoost cluster deployments.

    Shows the status of all model deployments, their endpoints,
    and the management/monitoring UI access information.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    show_secrets = ctx.obj.get("SHOW_SECRETS", False)
    display_secrets = verbose or show_secrets

    result = do_status(
        kubeconfig=kubeconfig,
        show_secrets=display_secrets,
        verbose=verbose,
    )

    if result["status"] == "error":
        raise click.ClickException(result["error"])

    # Extract data
    model_deployments = result["model_deployments"]
    management_pods = result["management_pods"]
    services = result["services"]

    # Calculate stats
    model_pods = []
    for pods_list in model_deployments.values():
        model_pods.extend(pods_list)

    model_ready = sum(1 for p in model_pods if p.get("ready"))
    model_total = len(model_pods)

    mgmt_ready = sum(1 for p in management_pods if p.get("ready"))
    mgmt_total = len(management_pods)

    # Display header with stats
    num_deployments = len(model_deployments)
    num_ready_deployments = sum(
        1
        for deployment_pods in model_deployments.values()
        if all(p.get("ready") for p in deployment_pods)
    )

    model_color = "green" if num_ready_deployments == num_deployments else "red"
    mgmt_color = "green" if mgmt_ready == mgmt_total else "red"

    click.echo(
        f"\nModels: {click.style(str(num_ready_deployments), fg=model_color)}/{num_deployments}\t\t"
        f"Mgmt.: {click.style(str(mgmt_ready), fg=mgmt_color)}/{mgmt_total}\n"
    )

    # Display model deployments table (grouped by deployment)
    if model_deployments:
        table_data = []
        for deployment_name, deployment_pods in sorted(model_deployments.items()):
            # Calculate pods ready for this deployment
            ready_count = sum(1 for p in deployment_pods if p.get("ready"))
            total_count = len(deployment_pods)

            # Determine deployment status
            if ready_count == total_count:
                status_str = "Ready"
                status_color = "green"
                message = "Running"
            else:
                status_str = "Not Ready"
                status_color = "red"
                # Get message from first non-ready pod
                for pod in deployment_pods:
                    if not pod.get("ready"):
                        message = get_pod_message(pod, verbose, kubeconfig)
                        break
                else:
                    message = "Pending"

            table_data.append(
                [
                    deployment_name,
                    click.style(status_str, fg=status_color),
                    f"{ready_count}/{total_count}",
                    message,
                ]
            )

        headers = ["Model", "Status", "Pods Ready (/Total)", "Message"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple", stralign="left"))
        click.echo()
    else:
        click.secho("No model deployments found.", fg="yellow")
        click.echo()

    # Display management/monitoring table (only in verbose mode)
    if verbose and management_pods:
        click.echo(click.style("Management & Monitoring Pods:", fg="cyan", bold=True))

        table_data = []
        for pod in management_pods:
            pod_name = pod.get("name", "")
            status_str = "Ready" if pod.get("ready") else "Not Ready"
            status_color = "green" if pod.get("ready") else "red"
            restarts = get_pod_restarts(pod)
            message = get_pod_message(pod, verbose, kubeconfig)

            table_data.append(
                [
                    pod_name,
                    click.style(status_str, fg=status_color),
                    restarts,
                    message,
                ]
            )

        headers = ["Pod", "Status", "Restarts", "Message"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple", stralign="left"))
        click.echo()

    # Display management services with URLs
    management_info = []
    seen_entries = set()

    # Get control node IP/hostname
    control_node = socket.getfqdn()

    # Look for ingress controller to get the base URL
    ingress_port = None
    for svc_name, svc_info in services.items():
        if "ingress-controller" in svc_name.lower():
            svc_type = svc_info.get("type", "ClusterIP")
            ports = svc_info.get("ports", [])

            if svc_type == "LoadBalancer":
                external_ips = svc_info.get("external_ips", [])
                if external_ips and ports:
                    control_node = external_ips[0]
                    ingress_port = ports[0].get("port", 80)
                    break
            elif svc_type == "NodePort" and ports:
                node_port = ports[0].get("node_port")
                if node_port:
                    ingress_port = node_port
                    break

    # Use default port 30080 if not found
    if ingress_port is None:
        ingress_port = 30080

    # Add monitoring and management URLs
    base_url = f"http://{control_node}:{ingress_port}"
    management_info.append(["Monitoring", f"{base_url}/monitor/"])
    management_info.append(["Management", f"{base_url}/manage/"])

    if management_info:
        click.echo(click.style("Service URLs:", fg="cyan", bold=True))
        click.echo(tabulate(management_info, headers=["Service", "URL"], tablefmt="simple"))
        click.echo()

    # Display secrets if requested
    if display_secrets and result["secrets"]:
        print_cluster_secrets(result["secrets"], verbose=verbose)
