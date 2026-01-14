import click
import re
import requests
from typing import List, Dict
from llmboost_hub.commands.login import do_login
from llmboost_hub.utils.config import config
from llmboost_hub.utils import gpu_info
import tabulate
import pandas as pd
from llmboost_hub.utils.lookup_cache import load_lookup_df


def do_fetch(
    query: str = r".*",
    verbose: bool = False,
    local_only: bool = False,
    skip_cache_update: bool = False,
    names_only: bool = False,
) -> pd.DataFrame:
    """
    Fetch remote/locally-cached lookup and filter by query and local GPU families.

    Behavior:
        - local_only=True: skip license check and network; load only from local cache file.
        - otherwise: attempt login/validation and fetch with cache fallback.
        - Perform case-insensitive LIKE on 'model'.
        - Filter rows to those matching detected GPU families.

    Args:
        query: Regex pattern to filter 'model' column (case-insensitive).
        verbose: If True, echo key steps.
        local_only: Skip license check and remote fetch; read from local cache only.
        skip_cache_update: Reserved for future use (cache policy is handled in loader).
        names_only: If True, return only the 'model' column.

    Returns:
        DataFrame with columns: model, gpu, docker_image (possibly empty).
    """
    if not local_only:
        # Best-effort: try to ensure license; even on failure, loader may still use cache
        do_login(license_file=None, verbose=verbose)
    lookup_df = load_lookup_df(
        config.LBH_LOOKUP_URL,
        query,
        verbose=verbose,
        local_only=local_only,
        skip_cache_update=skip_cache_update,
    )

    # Filter by query (case-insensitive LIKE on 'model' field)
    filtered_df = lookup_df[
        lookup_df["model"].astype(str).str.contains(pat=query, regex=True, flags=re.IGNORECASE)
    ].reset_index(drop=True)
    filtered_df.index += 1  # user-friendly display index

    # GPU family filter
    available_gpus = gpu_info.get_gpus()
    local_families = {gpu_info.gpu_name2family(g) for g in available_gpus if g}
    filtered_df = (
        filtered_df.assign(_gpu_family=filtered_df["gpu"].apply(gpu_info.gpu_name2family))
        .loc[lambda df: df["_gpu_family"].isin(local_families)]
        .drop(columns=["_gpu_family"])
    ).reset_index(drop=True)
    filtered_df.index += 1  # user-friendly display index

    # Short-circuit: names only
    if names_only:
        return filtered_df[["model"]]

    return filtered_df


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query", type=str, default=r".*", required=False)
@click.option(
    "--local-only",
    is_flag=True,
    help="Use only the local lookup cache (skip online fetch and license validation).",
)
@click.option(
    "--skip-cache-update",
    is_flag=True,
    help="Fetch, but skip updating local cache. (not applicable with --local-only).",
)
@click.option(
    "--names-only",
    is_flag=True,
    help="Return model names only.",
)
@click.pass_context
def fetch(ctx: click.Context, query, local_only, skip_cache_update, names_only):
    """
    Fetch for models in the LLMBoost registry.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    results_df = do_fetch(
        query,
        verbose=verbose,
        local_only=local_only,
        skip_cache_update=skip_cache_update,
        names_only=names_only,
    )

    click.echo(f"Found {len(results_df)} relevant images")
    if results_df.empty:
        return

    # Present results via tabulate
    click.echo(
        tabulate.tabulate(
            results_df.values.tolist(),
            headers=list(results_df.columns),
            showindex=list(results_df.index),
            tablefmt="psql",
        )
    )
    return results_df
