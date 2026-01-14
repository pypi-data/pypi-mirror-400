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


@click.group(name="cluster", invoke_without_command=True)
@click.option(
    "--show-secrets",
    is_flag=True,
    help="Display secrets for accessing management and monitoring endpoints",
)
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def cluster(ctx: click.Context, show_secrets: bool, kubeconfig: str):
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
        else:
            # Show help if no subcommand or flags provided
            click.echo(ctx.get_help())


# Register subcommands
cluster.add_command(install.install)
cluster.add_command(deploy.deploy)
cluster.add_command(remove.remove)
cluster.add_command(uninstall.uninstall)
cluster.add_command(status.status)
cluster.add_command(logs.logs)
