import os
import time
import json
import io
import pandas as pd
import requests
import click

from llmboost_hub.utils.config import config


def _cache_is_fresh(path: str, ttl_seconds: int = 60) -> bool:
    try:
        mtime = os.path.getmtime(path)
        return (time.time() - mtime) < ttl_seconds
    except Exception:
        return False


def _write_cache_from_df(cache_path: str, df: pd.DataFrame, verbose: bool = False) -> None:
    try:
        if cache_path.lower().endswith(".json"):
            df.to_json(cache_path, orient="records")
        else:
            df.to_csv(cache_path, index=False)
    except Exception:
        # best-effort cache
        pass
    if verbose:
        click.echo(f"Refreshed cache at {cache_path}")


def _load_df_from_cache(cache_path: str, verbose: bool = False) -> pd.DataFrame:
    try:
        if cache_path.lower().endswith(".json"):
            with open(cache_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return pd.DataFrame(data)
        else:
            return pd.read_csv(cache_path)
    except Exception:
        if verbose:
            click.echo(f"Failed to load cache from {cache_path}")
        return pd.DataFrame()


def _fetch_csv(endpoint: str, params: dict, verbose: bool = False) -> pd.DataFrame:
    # if verbose:
    #     click.echo(f"Downloading CSV from {endpoint} with params {params}")
    resp = requests.get(endpoint, params=params, timeout=10)
    if resp.status_code != 200:
        raise click.ClickException(f"Lookup failed ({resp.status_code}): {resp.text}")
    try:
        return pd.read_csv(io.StringIO(resp.text))
    except Exception:
        raise click.ClickException("Lookup returned invalid CSV")


def load_lookup_df(
    endpoint: str,
    query: str,
    verbose: bool = False,
    local_only: bool = False,
    skip_cache_update: bool = False,
) -> pd.DataFrame:
    """
    Use the local cache (`config.LBH_LOOKUP_CACHE`) if fresh (age < `config.LBH_LOOKUP_CACHE_TTL`);
    otherwise fetch from `endpoint`.

    On fetch success:
        - Return DataFrame.

    On fetch failure:
        - Fall back to the cache (even if stale)

    On cache failure:
        - Return empty DataFrame.

    Args:
        endpoint: CSV endpoint URL.
        query: Optional query string to pass to the endpoint (e.g., `q`).
        verbose: If True, log cache and fetch behavior.
        local_only: If True, skip remote fetch and use only local cache.
        skip_cache_update: If True, do not update cache after successful fetch. (Only applies if `local_only=False`.)

    Returns:
        A pandas DataFrame with columns normalized to lower-case (may be empty).
    """
    cache_path = config.LBH_LOOKUP_CACHE

    # Fresh cache
    if os.path.exists(cache_path) and _cache_is_fresh(
        cache_path, ttl_seconds=config.LBH_LOOKUP_CACHE_TTL
    ):
        if verbose:
            click.echo(f"Using fresh cache at {cache_path}")
        return _load_df_from_cache(cache_path, verbose=verbose)

    # Skip fetch remote if local_only
    if not local_only:
        try:
            df = _fetch_csv(endpoint, params={"q": query}, verbose=verbose)
            df.columns = [str(c).strip().lower() for c in df.columns]
            if not skip_cache_update:
                _write_cache_from_df(cache_path, df, verbose=verbose)
            return df
        except click.ClickException as e:
            if verbose:
                click.echo(f"Remote lookup failed: {e}. Falling back to cache/sample.")
        except Exception as e:
            if verbose:
                click.echo(f"Remote error: {e}. Falling back to cache/sample.")

    # Fallback to cache (even if stale)
    if os.path.exists(cache_path):
        if verbose:
            click.echo(f"Using cached data from {cache_path}")
        return _load_df_from_cache(cache_path, verbose=verbose)

    # Last resort: generate empty DataFrame
    if verbose:
        click.echo(f"No cache found at {cache_path}.")
    return pd.DataFrame()
