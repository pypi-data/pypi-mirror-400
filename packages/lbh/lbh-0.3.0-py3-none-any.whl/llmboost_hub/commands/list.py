import click
import subprocess
from typing import List
import re
import pandas as pd
import tabulate

from llmboost_hub.commands.fetch import do_fetch
from llmboost_hub.utils.config import config
from llmboost_hub.utils import gpu_info
from llmboost_hub.utils.container_utils import (
    container_name_for_model,
    is_container_running,
    is_model_initializing,
    is_model_ready2serve,
    is_model_tuning,
)
from llmboost_hub.utils.model_utils import is_model_downloaded
import os


def _get_local_images() -> List[str]:
    """
    Return a list of local docker images in the format 'repository:tag'.

    Notes:
        Best-effort; falls back to an empty list on errors.
    """
    try:
        out = subprocess.check_output(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"], text=True
        )
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        return lines
    except Exception:
        return []


def _get_installed_models(models_dir: str) -> List[str]:
    """
    Return list of installed model names (normalized).
    Equivalent to `grep -LrE '^  "(_name_or_path|architectures)": ' "{config.LBH_MODELS}/**/*.json" | xargs dirname | sort | uniq`.

    Staging dir (config.LBH_MODELS_STAGING) is ignored.
    """
    models: List[str] = []
    try:
        staging_dir_basename = os.path.basename(config.LBH_MODELS_STAGING)

        for repo in os.listdir(models_dir):
            repo_path = os.path.join(models_dir, repo)
            if not os.path.isdir(repo_path):
                continue
            # skip staging directory entirely
            if repo == staging_dir_basename:
                continue

            # collect second-level model directories under each repo
            subdirs = [
                d for d in os.listdir(repo_path) if os.path.isdir(os.path.join(repo_path, d))
            ]
            if subdirs:
                models.extend(subdirs)
            else:
                # fallback: treat top-level dir as model (legacy layouts)
                models.append(repo)
    except Exception:
        pass
    # deduplicate while preserving order
    seen = set()
    uniq_models = []
    for m in models:
        if m not in seen:
            seen.add(m)
            uniq_models.append(m)
    return uniq_models


def _resolve_model_path(models_root: str, model_name: str) -> str:
    """
    Best-effort: resolve absolute path for a model_name under LBH_MODELS by scanning
    <repo>/<model> while ignoring the staging dir. Falls back to <models_root>/<model_name>.
    """
    try:
        staging_dir = getattr(config, "LBH_MODELS_STAGING", None)
        staging_dir = os.path.abspath(staging_dir) if staging_dir else None

        for repo in os.listdir(models_root):
            repo_path = os.path.join(models_root, repo)
            if not os.path.isdir(repo_path):
                continue
            # skip staging directory
            if staging_dir and os.path.abspath(repo_path) == staging_dir:
                continue

            candidate = os.path.join(repo_path, model_name)
            if os.path.isdir(candidate):
                return candidate
    except Exception:
        pass
    # fallback
    return os.path.join(models_root, model_name)


def do_list(query: str = r".*", local_only: bool = True, verbose: bool = False) -> dict:
    """
    Aggregate local docker images, installed model dirs, GPU info, and join with lookup.

    Args:
        query: Optional LIKE filter passed to fetch for narrowing models.
        local_only: If True, fetch only uses local cache (no network).
        verbose: If True, emit warnings about ambiguous GPUs.

    Returns:
        Dict:
            - images: List[str] local images after joining
            - installed_models: List[str] under `config.LBH_MODELS`
            - gpus: List[str] detected GPU names
            - images_df: pd.DataFrame joined on `docker_image` (may include status)
            - lookup_df: pd.DataFrame of filtered lookup rows (pre-join)
    """
    images = _get_local_images()
    models_dir = config.LBH_MODELS
    installed_models = _get_installed_models(models_dir)

    # Prepare local images DataFrame
    local_df = pd.DataFrame({"docker_image": [str(i) for i in images]})

    # Load lookup (filtered via do_fetch over the query and local GPUs)
    cache_df = pd.DataFrame()
    try:
        cache_df = do_fetch(query=query, verbose=verbose, local_only=local_only)
        # Normalize column names
        cache_df.columns = [str(c).strip().lower() for c in cache_df.columns]
    except Exception:
        cache_df = pd.DataFrame(columns=["model", "gpu", "docker_image"])

    # Inner join on docker_image to keep only known images and get model,gpu columns
    if "docker_image" in cache_df.columns:
        merged_df = (
            local_df.merge(
                cache_df[["model", "gpu", "docker_image"]], on="docker_image", how="inner"
            )
            # NOTE: do not drop duplicates per docker_image; show all models
            .reset_index(drop=True)
        )
    else:
        merged_df = pd.DataFrame(columns=["model", "gpu", "docker_image"])

    # Add GPU match indicator column based on local GPU families
    local_gpus = gpu_info.get_gpus()
    local_families = {gpu_info.gpu_name2family(g) for g in local_gpus if g}
    if not merged_df.empty:
        merged_df = merged_df.assign(
            _gpu_family=merged_df["gpu"].apply(gpu_info.gpu_name2family),
            matches_local_gpu=lambda df: df["_gpu_family"].isin(local_families),
        ).drop(columns=["_gpu_family"])

    # Derive status column based on local presence and container/process state
    if not merged_df.empty:
        statuses: List[str] = []
        for _, row in merged_df.iterrows():
            model_id = str(row.get("model", "") or "")
            downloaded = is_model_downloaded(models_dir, model_id)
            cname = container_name_for_model(model_id) if model_id else ""
            if not downloaded:
                statuses.append("pending")
                continue
            if cname and is_container_running(cname):
                # Priority: tuning > serving > initializing > running
                if is_model_tuning(cname):
                    statuses.append("tuning")
                elif is_model_ready2serve(cname):
                    statuses.append("serving")
                elif is_model_initializing(cname):
                    statuses.append("initializing")
                else:
                    statuses.append("running")
            else:
                statuses.append("stopped")
        merged_df = merged_df.assign(status=statuses)

    # Filter images list to those present in the joined frame
    images = merged_df["docker_image"].tolist()

    # GPUs via utility (standardized)
    gpus: List[str] = gpu_info.get_gpus()

    # Optional note about multiple GPUs (can affect matching)
    if len(set(gpus)) > 1 and verbose:
        click.echo("Warning: Multiple GPUs detected.")

    return {
        "images": images,
        "installed_models": installed_models,
        "gpus": gpus,
        "images_df": merged_df,
        "lookup_df": cache_df,  # include full filtered lookup for consumers like prep
    }


@click.command(name="list", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query", required=False, default="")
@click.pass_context
def list_models(ctx: click.Context, query):
    """
    List supported models, their docker images, and statuses.

    \b
    Statuses:
        - pending: Model not yet downloaded/installed locally.
        - stopped: Model downloaded but container not running.
        - initializing: Container starting up (model loading in progress).
        - running: Container running but not serving requests.
        - serving: Container running and ready to serve requests.
        - tuning: Container running and performing model tuning.
    """
    verbose = ctx.obj.get("VERBOSE", False)
    data = do_list(query=query, verbose=verbose)

    # Prefer joined DataFrame with model,gpu,docker_image (+ matches_local_gpu)
    df = data.get("images_df") if isinstance(data.get("images_df"), pd.DataFrame) else None
    if df is None or df.empty:
        # Fallback to docker_image-only display if join is empty
        df = pd.DataFrame({"docker_image": data["images"]}).reset_index(drop=True)

    click.echo(f"Found {len(df)} images")
    if df.empty:
        return

    # Ensure desired column ordering if available
    desired_cols = [
        c
        for c in ["status", "model", "gpu", "docker_image", "matches_local_gpu"]
        if c in df.columns
    ]
    if desired_cols:
        df = df[desired_cols]
    df.index += 1  # start index at 1

    click.echo(
        tabulate.tabulate(
            df.values.tolist(),
            headers=list(df.columns),
            showindex=list(df.index),
            tablefmt="psql",
        )
    )

    # Extra details in verbose mode
    if not verbose:
        return

    # Tabulate installed HF models with their absolute paths
    click.echo("\nInstalled HF models (LBH_MODELS):")
    if data["installed_models"]:
        models_dir = config.LBH_MODELS
        models_list = data["installed_models"]
        models_df = pd.DataFrame(
            {
                "model": models_list,  # model_name only
                "path": [_resolve_model_path(models_dir, m) for m in models_list],
            }
        )
        models_df = models_df.sort_values(by="model").reset_index(drop=True)
        models_df.index += 1
        click.echo(
            tabulate.tabulate(
                models_df.values.tolist(),
                headers=list(models_df.columns),
                showindex=list(models_df.index),
                tablefmt="psql",
            )
        )
    else:
        click.echo(" (no installed models found)")

    click.echo("\nDetected GPUs (best-effort):")
    if data["gpus"]:
        for g in set(data["gpus"]):
            click.echo(f" - {g} ({gpu_info.gpu_name2family(g)})")
    else:
        click.echo(" (unable to detect GPUs)")
