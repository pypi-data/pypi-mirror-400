import click
import subprocess
from typing import List, Optional, Dict, Tuple, Any

from llmboost_hub.commands.list import do_list
from llmboost_hub.utils.config import config
from llmboost_hub.utils import gpu_info
import pandas as pd
import os
import tabulate
import time
import math
import docker
from huggingface_hub import HfApi, snapshot_download, errors as hf_errors
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TextColumn
import threading
import hashlib
from huggingface_hub.utils.tqdm import disable_progress_bars, enable_progress_bars
import shutil
from llmboost_hub.utils.fs_utils import path_has_files, dir_size_bytes, sha256_file
from llmboost_hub.utils.model_utils import set_model_path
import docker.errors
from llmboost_hub.commands.completions import complete_model_names


def do_prep(
    model: str, verbose: bool = False, only_verify: bool = False, fresh: bool = False
) -> dict:
    """
    Prepare (pull) the Docker image and Hugging Face model assets for a model.

    Steps:
      1. Validate exactly one local GPU family (avoid ambiguous matches).
      2. Resolve an exact match for the model via `do_list` (local images first, then lookup).
      3. Pull the docker image (Docker SDK); compact or verbose progress.
      4. Manage HF assets under `config.LBH_MODELS/<model>` using `snapshot_download` (resumable) via staging:
            - Staging path: `config.LBH_MODELS/.tmp/<model>`
            - Move to final on success.
      5. Modes:
            - `only_verify=True`: verify docker image digest and HF files (size/hash) and return.
            - `fresh=True`: remove local image and HF directories before re-downloading.

    Args:
        model: Target model identifier.
        verbose: If True, stream detailed logs and progress.
        only_verify: Verify artifacts without default re-download behavior.
        fresh: Forcefully remove local image and HF dirs before re-preparing.

    Returns:
        Dict:
            status: 'pulled' or 'error'
            image: Chosen docker image (if resolved)
            model_path: Final HF model directory (if prepared)
            error: Error message if any
            lookup_df: Lookup dataframe (for diagnostics)
    """
    # Check GPU families to avoid ambiguity
    local_families = {gpu_info.gpu_name2family(g) for g in gpu_info.get_gpus() if g}
    list_data = do_list(query=model, local_only=False, verbose=verbose)
    images_df: pd.DataFrame = list_data.get("images_df", pd.DataFrame())
    lookup_df: pd.DataFrame = list_data.get("lookup_df", pd.DataFrame())
    # Branch: reject when multiple or zero families (ambiguous environment)
    if len(local_families) != 1:
        return {
            "status": "error",
            "image": None,
            "model_path": None,
            "error": "No exact match found (ambiguous GPU families detected on this system).",
            "lookup_df": lookup_df,
        }

    # Use list to get filtered lookup_df and find exact model match
    exact_df = images_df[images_df["model"] == model] if not images_df.empty else pd.DataFrame()
    if exact_df.empty:
        exact_df = lookup_df[lookup_df["model"] == model] if not lookup_df.empty else pd.DataFrame()
    # Branch: no exact mapping for the given model name
    if exact_df.empty:
        return {
            "status": "error",
            "image": None,
            "model_path": None,
            "error": f"No exact match found for model '{model}'.",
            "lookup_df": lookup_df,
        }

    docker_image = exact_df["docker_image"].dropna().astype(str).iloc[0]

    # Fresh mode: remove local image and local HF model directories
    if fresh:
        try:
            click.echo(f"Fresh mode: removing docker image {docker_image}")
            client_tmp = docker.from_env()
            client_tmp.images.remove(docker_image, force=True, noprune=False)
        except docker.errors.ImageNotFound:
            # Acceptable: image wasn't present locally
            pass
        except Exception as e:
            click.echo(f"Warning: failed to remove docker image {docker_image} in fresh mode.\n{e}")
            return {
                "status": "error",
                "image": docker_image,
                "model_path": None,
                "error": f"Failed to remove docker image {docker_image} in fresh mode: {e}",
                "lookup_df": lookup_df,
            }
    # Ensure HF paths prepared before we might remove
    model_prefix = os.path.join(config.LBH_MODELS, model)  # final path
    staging_prefix = os.path.join(config.LBH_MODELS_STAGING, model)  # staging path
    os.makedirs(os.path.dirname(staging_prefix), exist_ok=True)
    if fresh:
        click.echo(
            f"Fresh mode: removing local model directories at {model_prefix} and {staging_prefix}"
        )
        try:
            shutil.rmtree(model_prefix, ignore_errors=False)
            shutil.rmtree(staging_prefix, ignore_errors=False)
        except FileNotFoundError:
            pass
        except Exception as e:
            click.echo(f"Warning: failed to remove local model directories in fresh mode.\n{e}")
            return {
                "status": "error",
                "image": docker_image,
                "model_path": None,
                "error": f"Failed to remove local model directories ({model_prefix}, {staging_prefix}) in fresh mode: {e}",
                "lookup_df": lookup_df,
            }

    # Pull the docker image using Docker SDK
    try:
        client = docker.from_env()
        if verbose:
            click.echo(f"Pulling Docker image: {docker_image}")
            # Stream verbose logs
            for evt in client.api.pull(docker_image, stream=True, decode=True):
                status = evt.get("status") or ""
                eid = evt.get("id") or ""
                prog = evt.get("progress") or ""
                if eid:
                    click.echo(f"[{eid}] {status} {prog}")
                else:
                    click.echo(status)
        else:
            # Non-verbose: show a compact progress bar based on layer completions
            seen_layers = set()
            done_layers = set()
            progress = Progress(
                TextColumn("Docker pull"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total} layers"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                # Keep the bar visible after completion
            )
            with progress:
                task = progress.add_task("pull", total=0)
                for evt in client.api.pull(docker_image, stream=True, decode=True):
                    eid = evt.get("id")
                    if not eid:
                        continue
                    if eid not in seen_layers:
                        seen_layers.add(eid)
                        progress.update(task, total=len(seen_layers))
                    status = (evt.get("status") or "").lower()
                    if any(
                        k in status
                        for k in ["already exists", "download complete", "pull complete"]
                    ):
                        done_layers.add(eid)
                        progress.update(task, completed=len(done_layers))
    except Exception as e:
        # Image pull failure: surface and exit
        return {
            "status": "error",
            "image": docker_image,
            "model_path": None,
            "error": f"Failed to pull image {docker_image}: {e}",
            "lookup_df": lookup_df,
        }

    # Optional: verify docker image digest vs remote only when requested
    def _verify_image_digest(client_obj, image_ref: str) -> Tuple[bool, str]:
        """
        Verify local image digest against the registry digest.

        Returns:
            (True, 'image verified') on success; otherwise (False, reason).
        """
        try:
            dist = client_obj.api.inspect_distribution(image_ref)
            desc = dist.get("Descriptor") or {}
            remote_digest = desc.get("digest") or desc.get("Digest")  # tolerate casing
            if not remote_digest:
                return False, "Remote digest unavailable from registry."
            try:
                img = client_obj.images.get(image_ref)
            except Exception:
                return False, "Local image not found after pull."
            repo_digests = img.attrs.get("RepoDigests") or []
            local_digests = set()
            for rd in repo_digests:
                if "@" in rd:
                    local_digests.add(rd.split("@", 1)[1])
            if remote_digest in local_digests:
                return True, "image verified"
            return (
                False,
                f"Digest mismatch. Remote={remote_digest}, Local={list(local_digests)[:1] or 'none'}",
            )
        except Exception as e:
            return False, f"Failed to verify image digest: {e}"

    if only_verify:
        ok_img, msg_img = _verify_image_digest(client, docker_image)
        if not ok_img:
            return {
                "status": "error",
                "image": docker_image,
                "model_path": None,
                "error": f"Docker image verification failed: {msg_img}",
                "lookup_df": lookup_df,
            }

    # Helpers for HF model verify/download (unchanged, gated by only_verify below)
    def _verify_repo(
        repo_id: str, repo_type: str, target_dir: str, show_progress: bool = True
    ) -> Tuple[bool, str]:
        """
        Verify local HF files against HF metadata:
        - All listed files exist.
        - Sizes match; and if sha256 is present in LFS metadata, hashes match.

        Returns:
            (True, 'verified') on success; otherwise (False, reason).
        """
        api = HfApi()
        try:
            info = (
                api.dataset_info(repo_id=repo_id, files_metadata=True)
                if repo_type == "dataset"
                else api.model_info(repo_id=repo_id, files_metadata=True)
            )
        except Exception as e:
            return False, f"Failed to fetch {repo_type} metadata for verification: {e}"

        siblings = list(info.siblings or [])
        missing = []
        wrong_size = []
        wrong_hash = []
        total = len(siblings)

        def _verify_one(sib) -> None:
            rel = getattr(sib, "rfilename", None)
            if not rel:
                return
            expected_size = int(getattr(sib, "size", 0) or 0)
            expected_sha = None
            lfs = getattr(sib, "lfs", None) or {}
            if isinstance(lfs, dict):
                expected_sha = lfs.get("sha256") or lfs.get("sha")
            expected_sha = expected_sha or getattr(sib, "sha256", None)

            local_path = os.path.join(target_dir, rel)
            if not os.path.exists(local_path):
                missing.append(rel)
                return
            try:
                stat_size = os.path.getsize(local_path)
            except Exception:
                missing.append(rel)
                return
            if expected_size and stat_size != expected_size:
                wrong_size.append(rel)
                if expected_sha:
                    try:
                        actual_sha = sha256_file(local_path)
                        if actual_sha != expected_sha:
                            wrong_hash.append(rel)
                    except Exception:
                        pass
                return
            if expected_sha:
                try:
                    actual_sha = sha256_file(local_path)
                    if actual_sha != expected_sha:
                        wrong_hash.append(rel)
                except Exception:
                    pass

        if show_progress and total > 0:
            with Progress(
                TextColumn("Verifying model"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total} files"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("verify", total=total)
                for s in siblings:
                    _verify_one(s)
                    progress.update(task, advance=1)
        else:
            for s in siblings:
                _verify_one(s)

        if missing or wrong_size or wrong_hash:
            parts = []
            if missing:
                parts.append(f"missing={len(missing)}")
            if wrong_size:
                parts.append(f"size_mismatch={len(wrong_size)}")
            if wrong_hash:
                parts.append(f"hash_mismatch={len(wrong_hash)}")
            detail = ", ".join(parts)
            return False, f"Verification failed for {repo_type} ({detail})."
        return True, "verified"

    def _download_repo(repo_id: str, repo_type: str, target_dir: str) -> Tuple[bool, str]:
        """
        Download the Hugging Face repo snapshot to 'target_dir' with an aggregate progress bar.

        Returns:
            (True, 'ok') on success; otherwise (False, reason).
        """
        os.makedirs(target_dir, exist_ok=True)
        api = HfApi()
        total_size = 0
        try:
            if repo_type == "dataset":
                info = api.dataset_info(repo_id=repo_id, files_metadata=True)
            else:
                info = api.model_info(repo_id=repo_id, files_metadata=True)
            siblings = list(info.siblings or [])
            total_size = sum(int(getattr(s, "size", 0) or 0) for s in siblings)
        except hf_errors.HfHubHTTPError:
            msg = f"Warning: No {repo_type} repo found for {repo_id}; skipping."
            click.echo(msg)
            return False, msg
        except Exception:
            msg = f"Warning: Failed to access {repo_type} repo for {repo_id}; skipping."
            click.echo(msg)
            return False, msg

        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")

        # Background thread for snapshot_download to allow progress polling
        exc_holder: Dict[str, Any] = {"err": None}

        def _bg_download():
            try:
                # Suppress HF internal tqdm bars; we render our own Rich progress
                disable_progress_bars()
                snapshot_download(
                    repo_id=repo_id,
                    repo_type=repo_type if repo_type in ("dataset", "model") else "model",
                    local_dir=target_dir,
                    token=token,
                )
            except Exception as e:
                exc_holder["err"] = e
            finally:
                # Restore default behavior for any later operations
                try:
                    enable_progress_bars()
                except Exception:
                    pass

        t = threading.Thread(target=_bg_download, daemon=True)
        t.start()

        def _current_bytes() -> int:
            return dir_size_bytes(target_dir)

        # Initial status snapshot for progress computation
        start_bytes = _current_bytes()
        if verbose:
            click.echo(
                f"Preparing download ({repo_type}): {start_bytes / (1024*1024):.2f} / "
                f"{(total_size or 0) / (1024*1024):.2f} MiB"
            )

        # Aggregate progress bar (non-verbose) or periodic logs (verbose/unknown total)
        if not verbose and total_size > 0:
            with Progress(
                TextColumn(f"Downloading {repo_type}"),
                BarColumn(),
                TextColumn("{task.percentage:>5.1f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                # Keep the bar visible after completion
            ) as progress:
                task = progress.add_task("download", total=total_size)
                progress.update(task, completed=min(start_bytes, total_size))
                while t.is_alive():
                    time.sleep(0.5)
                    done = _current_bytes()
                    progress.update(task, completed=min(done, total_size))
                done = _current_bytes()
                progress.update(task, completed=min(done, total_size))
        else:
            while t.is_alive():
                time.sleep(1.0)
                done = _current_bytes()
                if verbose and total_size > 0:
                    pct = (done / max(total_size, 1)) * 100.0
                    click.echo(
                        f"Downloading {repo_type}: {done / (1024*1024):.2f} / "
                        f"{total_size / (1024*1024):.2f} MiB ({pct:.2f}%)"
                    )
                elif verbose:
                    click.echo(f"Downloading {repo_type}: {done / (1024*1024):.2f} MiB")
            if verbose and total_size > 0:
                done = _current_bytes()
                pct = (done / max(total_size, 1)) * 100.0
                click.echo(
                    f"Completed {repo_type}: {done / (1024*1024):.2f} / "
                    f"{total_size / (1024*1024):.2f} MiB ({pct:.2f}%)"
                )

        # Propagate exceptions from the background thread
        if exc_holder["err"] is not None:
            return False, f"Hugging Face download error: {exc_holder['err']}"

        # Sanity: if we know total size and downloaded too little, likely gated/unauthorized
        done = _current_bytes()
        if total_size > 0 and done < max(int(total_size * 0.5), 100 * 1024 * 1024):
            msg = (
                f"Incomplete {repo_type} download for {repo_id}. "
                "This model likely requires access/acceptance. "
                "Please run `huggingface-cli login` and ensure you have accepted the model's license/terms "
                f"at https://huggingface.co/{repo_id} (or set HF_TOKEN)."
            )
            return False, msg

        return True, "ok"

    # If a model already exists at the final path:
    # - if --only-verify: verify; if verified, return success; if not, re-download to staging
    if path_has_files(model_prefix) and not fresh:
        if only_verify:
            # Branch: verify existing local copy first
            ok_existing, msg_exist = _verify_repo(model, "model", model_prefix, show_progress=True)
            if ok_existing:
                # Save model path to mapping file
                try:
                    set_model_path(model, model_prefix)
                except Exception as e:
                    if verbose:
                        click.echo(f"Warning: Failed to save model path to mapping file: {e}")
                return {
                    "status": "pulled",
                    "image": docker_image,
                    "model_path": model_prefix,
                    "error": None,
                    "lookup_df": lookup_df,
                }
            if verbose:
                click.echo("Existing model failed verification; re-downloading to staging...")
        else:
            # Branch: model exists and no verification requested
            # Save model path to mapping file
            try:
                set_model_path(model, model_prefix)
            except Exception as e:
                if verbose:
                    click.echo(f"Warning: Failed to save model path to mapping file: {e}")
            return {
                "status": "pulled",
                "image": docker_image,
                "model_path": model_prefix,
                "error": None,
                "lookup_df": lookup_df,
            }

    # Download to staging (resumable)
    os.makedirs(staging_prefix, exist_ok=True)
    ok_m, msg_m = _download_repo(model, "model", staging_prefix)
    if not ok_m:
        return {
            "status": "error",
            "image": docker_image,
            "model_path": model_prefix,
            "error": msg_m,
            "lookup_df": lookup_df,
        }

    # Verify staging only if requested
    if only_verify:
        ok_m, msg_m = _verify_repo(model, "model", staging_prefix, show_progress=True)
        if not ok_m:
            return {
                "status": "error",
                "image": docker_image,
                "model_path": model_prefix,
                "error": msg_m,
                "lookup_df": lookup_df,
            }

    # Move staging -> final atomically (replace if exists)
    try:
        os.makedirs(os.path.dirname(model_prefix), exist_ok=True)
        if os.path.exists(model_prefix):
            shutil.rmtree(model_prefix, ignore_errors=True)
        shutil.move(staging_prefix, model_prefix)
    except Exception as e:
        return {
            "status": "error",
            "image": docker_image,
            "model_path": model_prefix,
            "error": f"Failed to finalize model directory: {e}",
            "lookup_df": lookup_df,
        }

    # Save model path to the mapping file after successful preparation
    try:
        set_model_path(model, model_prefix)
    except Exception as e:
        # Non-fatal: log but don't fail the prep operation
        if verbose:
            click.echo(f"Warning: Failed to save model path to mapping file: {e}")

    return {
        "status": "pulled",
        "image": docker_image,
        "model_path": model_prefix,
        "error": None,
        "lookup_df": lookup_df,
    }


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("model", required=True, shell_complete=complete_model_names)
@click.option(
    "--only-verify",
    is_flag=True,
    help="Only verify docker image digest and HF model files; skip verification otherwise.",
)
@click.option(
    "-f",
    "--fresh",
    is_flag=True,
    help="Remove local docker image and HF model and re-download everything fresh.",
)
@click.pass_context
def prep(ctx: click.Context, model, only_verify, fresh):
    """
    Prepare the Docker image and local model assets for a given model.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    result = do_prep(model, verbose=verbose, only_verify=only_verify, fresh=fresh)

    if result["status"] == "pulled":
        click.echo(f"Successfully pulled {result['image']}")
        if result.get("model_path"):
            click.echo(f"Model assets available at: {result['model_path']}")
        return

    # On error: return the error string; tabulate only for "No exact match" cases
    err = result["error"] or "Unknown prep error"
    click.echo(err)

    lookup_df = result.get("lookup_df")
    if (
        isinstance(lookup_df, pd.DataFrame)
        and not lookup_df.empty
        and err.startswith("No exact match")
    ):
        df = lookup_df.copy().reset_index(drop=True)
        df.index += 1
        click.echo(
            tabulate.tabulate(
                df.values.tolist(),
                headers=list(df.columns),
                showindex=list(df.index),
                tablefmt="psql",
            )
        )

    # Return the error string (no exception)
    return err
