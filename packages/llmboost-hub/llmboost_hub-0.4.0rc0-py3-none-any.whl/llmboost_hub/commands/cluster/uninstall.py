"""
Uninstall LLMBoost Helm chart and cluster resources.
"""

import logging
import subprocess
import sys
from typing import Optional

import click

from llmboost_hub.commands.cluster.remove import do_remove
from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    run_helm,
    namespace_exists,
)

log = logging.getLogger("CLUSTER_UNINSTALL")


def do_uninstall(
    kubeconfig: Optional[str] = None,
    force: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Uninstall LLMBoost Helm chart and remove all cluster resources.

    Args:
        kubeconfig: Optional path to kubeconfig file.
        force: If True, skip confirmation prompt.
        verbose: If True, show detailed output.

    Returns:
        Dict with status, error, message, and cancelled keys.
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
            "status": "success",
            "message": f"Namespace '{config.LBH_KUBE_NAMESPACE}' does not exist. Nothing to uninstall.",
        }

    # Remove all model deployments
    remove_result = do_remove(
        models=[],
        all_models=True,
        force=force,
        kubeconfig=kubeconfig,
        verbose=verbose,
    )
    if remove_result["status"] == "error":
        return remove_result

    # Uninstall Helm chart
    try:
        result = run_helm(
            [
                "uninstall",
                config.LBH_HELM_RELEASE_NAME,
                "-n",
                config.LBH_KUBE_NAMESPACE,
            ],
            kubeconfig=kubeconfig,
            check=True,
            verbose=verbose,
        )

        # If force flag is set, forcefully delete any stuck pods
        if force:
            from llmboost_hub.utils.kube_utils import run_kubectl

            try:
                # Get all pods in the namespace
                pod_result = run_kubectl(
                    [
                        "get",
                        "pods",
                        "-n",
                        config.LBH_KUBE_NAMESPACE,
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
                            check=False,
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
                            check=False,
                            verbose=verbose,
                        )
                    except Exception as e:
                        if verbose:
                            log.warning(f"Failed to force delete pod {pod_name}: {e}")
            except Exception as e:
                if verbose:
                    log.warning(f"Failed to list pods for forced deletion: {e}")

        return {
            "status": "success",
            "message": "Helm chart uninstalled successfully",
            "output": result.stdout if verbose else None,
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "error": "Failed to uninstall Helm chart",
            "stderr": e.stderr if hasattr(e, "stderr") else None,
        }


@click.command(name="uninstall")
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Skip confirmation prompt and forcefully delete stuck pods",
)
@click.pass_context
def uninstall(ctx: click.Context, kubeconfig: Optional[str], force: bool):
    """
    Uninstall LLMBoost Helm chart and remove all cluster resources.

    This command removes the LLMBoost operator, all model deployments,
    monitoring UI, and related Kubernetes resources.

    Use --force to skip confirmation and forcefully delete any stuck pods
    by clearing finalizers and using zero grace period.

    Warning: This will delete all running model deployments!
    """
    verbose = ctx.obj.get("VERBOSE", False)

    # Confirmation prompt (only if not forced)
    if not force:
        click.echo(
            f"\n{click.style('Warning:', fg='yellow', bold=True)} This will uninstall the LLMBoost Helm chart and remove all resources in namespace '{config.LBH_KUBE_NAMESPACE}'."
        )
        if not click.confirm("Do you want to continue?", default=False):
            click.echo("Uninstall cancelled.")
            return

    result = do_uninstall(
        kubeconfig=kubeconfig,
        force=force,
        verbose=verbose,
    )

    if result["status"] == "error":
        if result.get("stderr"):
            click.echo(result["stderr"], err=True)
        raise click.ClickException(result["error"])

    # Display success message
    if "message" in result:
        if "Nothing to uninstall" in result["message"]:
            click.secho(result["message"], fg="yellow")
            return

        click.echo(
            f"\nUninstalling Helm release chart: {config.LBH_HELM_RELEASE_NAME} from namespace {config.LBH_KUBE_NAMESPACE}"
        )
        click.secho(result["message"], fg="green", bold=True)

        if verbose and result.get("output"):
            click.echo(result["output"])

        click.echo(
            f"\n{click.style('LLMBoost cluster uninstalled successfully!', fg='green', bold=True)}"
        )
        click.echo(
            f"\nNote: The namespace '{config.LBH_KUBE_NAMESPACE}' still exists. "
            f"To remove it completely, run:"
        )
        click.echo(f"  kubectl delete namespace {config.LBH_KUBE_NAMESPACE}")
