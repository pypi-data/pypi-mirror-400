"""
Deploy models to Kubernetes cluster based on cluster configuration.
"""

import json
import logging
import os
import sys
from typing import Optional, Dict, Any, List

import click
import yaml

from llmboost_hub.utils.config import config
from llmboost_hub.utils.kube_utils import (
    verify_prerequisites,
    verify_cluster_running,
    namespace_exists,
    detect_gpu_types,
    run_kubectl,
    sanitize_model_name,
)
from llmboost_hub.utils.lookup_cache import load_lookup_df

log = logging.getLogger("CLUSTER_DEPLOY")


def validate_cluster_config(cfg: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate cluster configuration schema.

    Args:
        cfg: Parsed cluster configuration.

    Returns:
        Tuple of (is_valid, error_message).
    """
    # Check schema version
    if "schema_version" not in cfg:
        return False, "Missing 'schema_version' field"

    # Check cluster section
    if "cluster" not in cfg:
        return False, "Missing 'cluster' section"

    cluster = cfg["cluster"]
    if "name" not in cluster:
        return False, "Missing 'cluster.name' field"

    # Check model_deployments
    if "model_deployments" not in cfg:
        return False, "Missing 'model_deployments' field"

    model_deployments = cfg["model_deployments"]
    if not isinstance(model_deployments, list):
        return False, "'model_deployments' must be a list"

    if len(model_deployments) == 0:
        return False, "'model_deployments' cannot be empty"

    # Validate each deployment
    for idx, deployment in enumerate(model_deployments):
        if "model" not in deployment:
            return False, f"Deployment {idx}: missing 'model' field"

        # Check mutually exclusive fields
        has_resource_selector = "resource_selector" in deployment
        has_node_replicas = "node_replicas" in deployment

        if has_resource_selector and has_node_replicas:
            return (
                False,
                f"Deployment {idx}: 'resource_selector' and 'node_replicas' are mutually exclusive",
            )

        if not has_resource_selector and not has_node_replicas:
            return (
                False,
                f"Deployment {idx}: must specify either 'resource_selector' or 'node_replicas'",
            )

        # Validate resource_selector if present
        if has_resource_selector:
            resource_selector = deployment["resource_selector"]
            if not isinstance(resource_selector, list):
                return (
                    False,
                    f"Deployment {idx}: 'resource_selector' must be a list",
                )

            for res_idx, resource in enumerate(resource_selector):
                if "id" not in resource:
                    return (
                        False,
                        f"Deployment {idx}, resource {res_idx}: missing 'id' field",
                    )

        # Validate node_replicas if present
        if has_node_replicas:
            node_replicas = deployment["node_replicas"]
            if not isinstance(node_replicas, int) or node_replicas <= 0:
                return (
                    False,
                    f"Deployment {idx}: 'node_replicas' must be a positive integer",
                )

    return True, None


def get_model_image_from_lookup(model: str, gpu_type: str) -> Optional[str]:
    """
    Get Docker image for a model from the lookup cache.

    Args:
        model: Full model name (e.g., "meta-llama/Llama-3.2-1B-Instruct").
        gpu_type: GPU type ("nvidia" or "amd").

    Returns:
        Docker image string or None if not found.
    """
    try:
        # Load lookup data
        df = load_lookup_df(
            config.LBH_LOOKUP_URL,
            query="",
            verbose=False,
            local_only=True,  # Use cached data only
        )

        if df.empty:
            return None

        # Search for model with matching GPU type
        model_lower = model.lower()
        for _, row in df.iterrows():
            row_model = str(row.get("model", "")).strip()
            row_gpu = str(row.get("gpu", "")).strip().lower()
            row_image = str(row.get("docker_image", "")).strip()

            if row_model.lower() == model_lower and row_gpu == gpu_type.lower():
                return row_image

        # Fallback: return any match for the model
        for _, row in df.iterrows():
            row_model = str(row.get("model", "")).strip()
            row_image = str(row.get("docker_image", "")).strip()

            if row_model.lower() == model_lower:
                return row_image

        return None
    except Exception as e:
        log.warning(f"Failed to lookup model image: {e}")
        return None


def generate_crd_yaml(
    model: str,
    deployment_config: Dict[str, Any],
    cluster_config: Dict[str, Any],
    gpu_types: List[str],
) -> str:
    """
    Generate Kubernetes CRD YAML for a model deployment.

    Args:
        model: Full model name.
        deployment_config: Single deployment configuration from cluster config.
        cluster_config: Full cluster configuration.
        gpu_types: List of detected GPU types.

    Returns:
        YAML string for the CRD.
    """
    hf_token = cluster_config.get("cluster", {}).get("huggingfaceToken", "")
    custom_image = deployment_config.get("docker_image")
    custom_model_path = deployment_config.get("model_path")

    # Build CRD structure
    crd = {
        "apiVersion": config.KUBE_CRD_API_VERSION,
        "kind": config.KUBE_CRD_KIND,
        "metadata": {
            "name": sanitize_model_name(model),
            "namespace": config.LBH_KUBE_NAMESPACE,
        },
        "spec": {
            "apiEndpoint": "/api",
            "deployments": {},
            # TODO: uncomment when imagePullSecrets supported in CRD
            # "imagePullSecrets": [{"name": config.KUBE_DOCKER_REGISTRY_SECRET_NAME}],
        },
    }

    # Handle resource_selector (explicit node placement)
    if "resource_selector" in deployment_config:
        resource_selector = deployment_config["resource_selector"]

        # For each GPU type, create a deployment configuration
        for gpu_type in gpu_types:
            # Determine image
            if custom_image:
                image = custom_image
            else:
                image = get_model_image_from_lookup(model, gpu_type)
                if not image:
                    # Fallback to default based on GPU type
                    if gpu_type == "nvidia":
                        image = "mangollm/mb-llmboost-cuda:latest"
                    else:
                        image = "mangollm/mb-llmboost-rocm:latest"

            gpu_deployment = {
                "mode": "serve",
                "gpu": {
                    "type": gpu_type,
                    # "count": 1,  # Default, can be overridden per resource
                },
                "image": image,
                "modelName": model,
            }

            # Add HF token if provided
            if hf_token:
                gpu_deployment["huggingfaceToken"] = hf_token

            # Add custom model path if specified
            if custom_model_path:
                gpu_deployment["env"] = [
                    {
                        "name": "MODEL_PATH",
                        "value": custom_model_path,
                    }
                ]

            # Add nodes from resource_selector
            nodes = []
            for resource in resource_selector:
                node_id = resource["id"]
                nodes.append(node_id)

                # Handle per-resource GPU count override
                # This would require separate deployments per node with different GPU counts
                # For now, we'll use the first resource's GPU count if specified
                if "gpu_count" in resource and not nodes[:-1]:  # Only first resource
                    gpu_deployment["gpu"]["count"] = resource["gpu_count"]

            gpu_deployment["nodes"] = nodes

            # Add to deployments
            crd["spec"]["deployments"][gpu_type] = gpu_deployment

    # Handle node_replicas (automatic node allocation)
    elif "node_replicas" in deployment_config:
        node_replicas = deployment_config["node_replicas"]

        # For each GPU type, create a deployment configuration
        for gpu_type in gpu_types:
            # Determine image
            if custom_image:
                image = custom_image
            else:
                image = get_model_image_from_lookup(model, gpu_type)
                if not image:
                    raise click.ClickException(
                        f"No Docker image found for model '{model}' with GPU type '{gpu_type}'. "
                        "Please specify 'docker_image' in the deployment configuration."
                    )

            gpu_deployment = {
                "mode": "serve",
                "gpu": {
                    "type": gpu_type,
                    "count": 1,
                },
                "image": image,
                "modelName": model,
                "numInstances": node_replicas,
            }

            # Add HF token if provided
            if hf_token:
                gpu_deployment["huggingfaceToken"] = hf_token

            # Add custom model path if specified
            if custom_model_path:
                gpu_deployment["env"] = [
                    {
                        "name": "MODEL_PATH",
                        "value": custom_model_path,
                    }
                ]

            # Add to deployments
            crd["spec"]["deployments"][gpu_type] = gpu_deployment

    return yaml.dump(crd, sort_keys=False, default_flow_style=False)


def do_deploy(
    config_file: Optional[str] = None,
    kubeconfig: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """
    Deploy models to Kubernetes cluster based on configuration.

    Args:
        config_file: Path to cluster configuration file.
        kubeconfig: Optional path to kubeconfig file.
        verbose: If True, show detailed output.

    Returns:
        Dict with status, error, applied_count, failed_count, and deployments keys.
    """
    # Determine config file path
    if config_file is None:
        config_file = config.LBH_CLUSTER_CONFIG_PATH

    if not os.path.exists(config_file):
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "utils", "template_cluster_config.jsonc"
        )
        template_info = (
            template_path
            if os.path.exists(template_path)
            else "<llmboost_hub_install>/utils/template_cluster_config.jsonc"
        )
        return {
            "status": "error",
            "error": f"Configuration file not found: {config_file}",
            "template_path": template_info,
        }

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

    # Load and parse configuration
    try:
        with open(config_file, "r") as f:
            # Remove comments for JSON parsing (JSONC support)
            import re

            content = f.read()
            # Remove single-line comments
            content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
            # Remove multi-line comments
            content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

            cluster_cfg = json.loads(content)
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON in configuration file: {e}"}
    except Exception as e:
        return {"status": "error", "error": f"Failed to load configuration: {e}"}

    # Validate configuration
    is_valid, error_msg = validate_cluster_config(cluster_cfg)
    if not is_valid:
        return {"status": "error", "error": f"Configuration validation failed: {error_msg}"}

    # Detect GPU types in cluster
    gpu_types = detect_gpu_types(kubeconfig)
    if not gpu_types:
        gpu_types = ["nvidia"]

    # Create deployment directory
    deploy_dir = config.LBH_KUBE_MODEL_DEPLOYMENTS_PATH
    os.makedirs(deploy_dir, exist_ok=True)

    # Generate and apply CRDs for each model
    model_deployments = cluster_cfg["model_deployments"]
    applied_count = 0
    failed_count = 0
    deployment_results = []

    for deployment in model_deployments:
        model = deployment["model"]
        safe_model_name = model.replace("/", "_")
        manifest_path = os.path.join(deploy_dir, f"{safe_model_name}_deployment.yaml")

        result = {"model": model, "status": "pending"}

        # Generate CRD YAML
        try:
            crd_yaml = generate_crd_yaml(model, deployment, cluster_cfg, gpu_types)

            # Write to file
            with open(manifest_path, "w") as f:
                f.write(crd_yaml)

            result["manifest_path"] = manifest_path

        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"Failed to generate manifest: {e}"
            failed_count += 1
            deployment_results.append(result)
            continue

        # Apply manifest
        try:
            run_kubectl(
                ["apply", "-f", manifest_path],
                kubeconfig=kubeconfig,
                check=True,
                verbose=verbose,
            )
            result["status"] = "deployed"
            applied_count += 1
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"Failed to apply manifest: {e}"
            failed_count += 1

        deployment_results.append(result)

    return {
        "status": "success" if applied_count > 0 else "error",
        "error": (
            f"No models were deployed successfully. Reason: {', '.join([d.get('error', 'Unknown error') for d in deployment_results if d['status'] == 'failed'])}"
            if applied_count == 0
            else None
        ),
        "applied_count": applied_count,
        "failed_count": failed_count,
        "deployments": deployment_results,
        "gpu_types": gpu_types,
        "config_file": config_file,
    }


@click.command(name="deploy")
@click.option(
    "-f",
    "--config-file",
    type=click.Path(exists=True),
    default=None,
    help=f"Path to cluster configuration file (default: {config.LBH_CLUSTER_CONFIG_PATH})",
)
@click.option(
    "--kubeconfig",
    type=click.Path(exists=True),
    help="Path to kubeconfig file",
)
@click.pass_context
def deploy(ctx: click.Context, config_file: Optional[str], kubeconfig: Optional[str]):
    """
    Deploy models to Kubernetes cluster based on configuration.

    Parses the cluster configuration, generates Kubernetes CRD manifests,
    and applies them to deploy models across the cluster.

    The configuration file should follow the template at:
    $LBH_HOME/utils/template_cluster_config.jsonc
    """
    verbose = ctx.obj.get("VERBOSE", False)

    result = do_deploy(
        config_file=config_file,
        kubeconfig=kubeconfig,
        verbose=verbose,
    )

    if result["status"] == "error" and "template_path" in result:
        click.secho(f"{result['error']}", fg="red", bold=True)
        click.echo(f"\nCreate a cluster configuration file following the template at:")
        click.echo(f"  {result['template_path']}")
        raise click.ClickException("Configuration file not found")

    if result["status"] == "error" and result.get("error"):
        raise click.ClickException(result["error"])

    # Display progress
    click.echo(f"\nLoading configuration: {result['config_file']}")
    click.secho("Configuration loaded and validated", fg="green")

    click.echo("\nDetecting GPU types in cluster")
    if result["gpu_types"] == ["nvidia"] and len(result["gpu_types"]) == 1:
        click.secho("Warning: No GPU types detected. Using default (nvidia).", fg="yellow")
    else:
        click.secho(f"Detected GPU types: {', '.join(result['gpu_types'])}", fg="green")

    click.echo(f"\nGenerating deployment manifests for {len(result['deployments'])} models")

    # Display per-model results
    for deploy_result in result["deployments"]:
        model = deploy_result["model"]
        click.echo(f"\n  Processing: {model}")

        if deploy_result["status"] == "deployed":
            if verbose and "manifest_path" in deploy_result:
                click.echo(f"    Generated manifest: {deploy_result['manifest_path']}")
            click.secho(f"    Deployed successfully", fg="green")
        else:
            click.secho(f"    {deploy_result.get('error', 'Failed')}", fg="red")

    # Summary
    click.echo(f"\n{click.style('Deployment Summary:', fg='cyan', bold=True)}")
    click.echo(f"  Successfully deployed: {click.style(str(result['applied_count']), fg='green')}")
    if result["failed_count"] > 0:
        click.echo(f"  Failed: {click.style(str(result['failed_count']), fg='red')}")

    if result["applied_count"] > 0:
        click.echo(f"\n{click.style('Model deployments applied!', fg='green', bold=True)}")
        click.echo(f"\nCheck deployment status:")
        click.echo(f"  lbh cluster status")
    else:
        raise click.ClickException("No models were deployed successfully")
