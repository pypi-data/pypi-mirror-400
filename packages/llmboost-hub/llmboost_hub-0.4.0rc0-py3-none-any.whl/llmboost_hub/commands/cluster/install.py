"""
Install LLMBoost Helm chart and cluster resources.
"""

import base64
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
    run_kubectl,
    get_cluster_secrets,
    print_cluster_secrets,
)

log = logging.getLogger("CLUSTER_INSTALL")


def do_install(
    kubeconfig: Optional[str] = None,
    docker_username: Optional[str] = None,
    docker_pat: Optional[str] = None,
    docker_email: Optional[str] = None,
    extra_helm_args: tuple = (),
    verbose: bool = False,
) -> dict:
    """
    Install LLMBoost Helm chart and cluster infrastructure.

    Args:
        kubeconfig: Optional path to kubeconfig file.
        docker_username: Docker Hub username for pulling LLMBoost images.
        docker_pat: Docker Hub Personal Access Token.
        docker_email: Docker Hub email (can be any valid email format).
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

    # Create namespace if it doesn't exist (needed for Docker secret creation)
    from llmboost_hub.utils.kube_utils import namespace_exists

    if not namespace_exists(config.LBH_KUBE_NAMESPACE, kubeconfig):
        if verbose:
            click.echo(f"\nCreating namespace: {config.LBH_KUBE_NAMESPACE}")
        try:
            run_kubectl(
                ["create", "namespace", config.LBH_KUBE_NAMESPACE],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            if verbose:
                click.secho(f"  Namespace {config.LBH_KUBE_NAMESPACE} created", fg="green")
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": f"Failed to create namespace: {e.stderr if hasattr(e, 'stderr') else str(e)}",
            }

    # Create Docker registry secret from flags or config file
    values_yaml_path = None
    docker_config_used = None

    # Determine Docker credentials source
    if docker_username and docker_pat and docker_email:
        # Use provided flags
        if verbose:
            click.echo("\nCreating Docker registry secret from provided credentials...")
        docker_config_used = "flags"
    else:
        # Fallback to ~/.docker/config.json
        docker_config_path = config.LBH_DOCKER_CONFIG
        if not os.path.exists(docker_config_path):
            click.secho(
                f"\nWarning: Docker config file not found at {docker_config_path}",
                fg="yellow",
            )
            click.echo("  No Docker credentials provided. You can either:")
            click.echo("    1. Run 'docker login' to create the config file, then reinstall")
            click.echo("    2. Provide credentials: --docker-username --docker-pat --docker-email")
            click.echo("  Continuing without Docker registry credentials...\n")
        else:
            # Parse Docker config file to extract credentials
            try:
                if verbose:
                    click.echo(f"\nReading Docker credentials from {docker_config_path}...")

                with open(docker_config_path, "r") as f:
                    docker_config_data = json.load(f)

                # Look for Docker Hub credentials in auths section
                auths = docker_config_data.get("auths", {})
                docker_hub_key = None
                for key in [config.KUBE_DOCKER_SERVER, "index.docker.io"]:
                    if key in auths:
                        docker_hub_key = key
                        break

                if docker_hub_key and "auth" in auths[docker_hub_key]:
                    # Decode base64 auth string
                    try:
                        auth_decoded = base64.b64decode(auths[docker_hub_key]["auth"]).decode(
                            "utf-8"
                        )
                    except Exception as e:
                        click.secho(
                            "  Warning: Failed to decode Docker auth string from config file.",
                            fg="yellow",
                        )
                        log.debug(
                            "Error decoding Docker auth string in config file %s for key %s: %s",
                            docker_config_path,
                            docker_hub_key,
                            str(e),
                        )
                        auth_decoded = ""
                    if ":" not in auth_decoded:
                        click.secho(
                            "  Warning: Invalid Docker auth format in config file; expected 'username:password' in auth field.",
                            fg="yellow",
                        )
                        log.debug(
                            "Invalid Docker auth format in config file %s for key %s: %r",
                            docker_config_path,
                            docker_hub_key,
                            auth_decoded,
                        )
                    else:
                        username, password = auth_decoded.split(":", 1)
                        docker_username = username
                        docker_pat = password
                        docker_email = auths[docker_hub_key].get("email", "unused@example.com")
                        docker_config_used = "config_file"

                        if verbose:
                            click.secho("  Found Docker Hub credentials", fg="green")
                else:
                    click.secho(
                        f"  Warning: No Docker Hub credentials found in {docker_config_path}",
                        fg="yellow",
                    )
                    click.echo("  Run 'docker login' to authenticate with Docker Hub")
            except Exception as e:
                click.secho(
                    f"  Warning: Failed to read Docker config: {e}",
                    fg="yellow",
                )
                log.debug(f"Error reading Docker config: {e}")

    # Create the Docker registry secret if credentials are available
    if docker_username and docker_pat and docker_email:
        try:
            # Check if secret already exists and delete it
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
            if result.returncode == 0:
                if verbose:
                    click.echo("  Deleting existing secret...")
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

        # Create the Docker registry secret
        try:
            run_kubectl(
                [
                    "create",
                    "secret",
                    "docker-registry",
                    config.KUBE_DOCKER_REGISTRY_SECRET_NAME,
                    "-n",
                    config.LBH_KUBE_NAMESPACE,
                    f"--docker-server={config.KUBE_DOCKER_SERVER}",
                    f"--docker-username={docker_username}",
                    f"--docker-password={docker_pat}",
                    f"--docker-email={docker_email}",
                ],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            if verbose:
                click.secho("  Docker registry secret created successfully", fg="green")
                if docker_config_used == "config_file":
                    click.echo(f"  Using credentials from {config.LBH_DOCKER_CONFIG}")

            # Create temporary values.yaml with imagePullSecrets
            import tempfile

            values_yaml_content = (
                "imagePullSecrets:\n" f"  - name: {config.KUBE_DOCKER_REGISTRY_SECRET_NAME}\n"
            )
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(values_yaml_content)
                values_yaml_path = f.name

            if verbose:
                click.echo(f"  Created values.yaml with imagePullSecrets")

        except subprocess.CalledProcessError as e:
            if values_yaml_path and os.path.exists(values_yaml_path):
                os.unlink(values_yaml_path)
            return {
                "status": "error",
                "error": f"Failed to create Docker registry secret: {e.stderr if hasattr(e, 'stderr') else str(e)}",
            }

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
    ]

    # Add values.yaml if Docker credentials were provided
    if values_yaml_path:
        helm_install_cmd.extend(["-f", values_yaml_path])
        if verbose:
            click.echo(f"  Using values.yaml with imagePullSecrets")

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
    finally:
        # Clean up temporary values.yaml file
        if values_yaml_path and os.path.exists(values_yaml_path):
            os.unlink(values_yaml_path)

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
@click.option(
    "--docker-username",
    type=str,
    help="Docker Hub username for pulling LLMBoost images",
)
@click.option(
    "--docker-pat",
    type=str,
    help="Docker Hub Personal Access Token",
)
@click.option(
    "--docker-email",
    type=str,
    help="Docker Hub email (can be any valid email format)",
)
@click.argument("extra_helm_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def install(
    ctx: click.Context,
    kubeconfig: Optional[str],
    docker_username: Optional[str],
    docker_pat: Optional[str],
    docker_email: Optional[str],
    extra_helm_args,
):
    """
    Install LLMBoost Helm chart and cluster infrastructure.

    This command sets up the necessary Kubernetes resources for multi-node
    LLMBoost deployments including the operator, monitoring UI, and ingress.

    Pass additional Helm arguments after -- (e.g., lbh cluster install -- --set foo=bar)

    \b
    Docker Registry Authentication:
    Docker Hub credentials are required for pulling private LLMBoost images.

    Option 1 (Recommended): Use flags to provide credentials directly
        lbh cluster install --docker-username myuser --docker-pat mytoken --docker-email user@example.com

    Option 2: Authenticate with Docker CLI and let lbh read from ~/.docker/config.json
        docker login
        lbh cluster install

    Note: All three flags (--docker-username, --docker-pat, --docker-email) must be provided together.

    \b
    Prerequisites:
    - Kubernetes cluster must be running and accessible
    - kubectl, helm, and docker must be installed
    - Docker Hub credentials (via flags or 'docker login')
    """
    verbose = ctx.obj.get("VERBOSE", False)

    # Validate Docker registry flags - if any are provided, all three must be provided
    docker_flags_provided = [docker_username, docker_pat, docker_email]
    docker_flags_count = sum(1 for flag in docker_flags_provided if flag is not None)

    if docker_flags_count > 0 and docker_flags_count < 3:
        raise click.ClickException(
            "All three Docker registry flags must be provided together: \n"
            "  --docker-username, --docker-pat, and --docker-email\n"
            "Or omit all three to use credentials from ~/.docker/config.json"
        )

    result = do_install(
        kubeconfig=kubeconfig,
        docker_username=docker_username,
        docker_pat=docker_pat,
        docker_email=docker_email,
        extra_helm_args=extra_helm_args,
        verbose=verbose,
    )

    if result["status"] == "error":
        raise click.ClickException(result["error"])

    # Print access credentials
    click.echo()
    print_cluster_secrets(result["secrets"], verbose=True)

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
