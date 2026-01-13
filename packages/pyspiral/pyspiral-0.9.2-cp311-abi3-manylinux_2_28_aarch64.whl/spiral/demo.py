"""Demo data to play with SpiralDB"""

import functools
import hashlib
import os
import time
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datasets import load_dataset

from spiral import Project, Spiral, Table


# Cache configuration
def _get_cache_dir() -> Path | None:
    """Get cache directory from environment variable, or None if caching is disabled."""
    cache_dir = os.environ.get("SPIRAL_DEMO_CACHE_DIR")
    if cache_dir:
        path = Path(cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    return None


def _cache_key(*parts: str) -> str:
    """Generate a cache key from components."""
    return "-".join(str(p).replace("-", "_") for p in parts)


def _get_cached_table(cache_key: str) -> pa.Table | None:
    """Load Arrow table from cache if available."""
    cache_dir = _get_cache_dir()
    if not cache_dir:
        return None

    cache_file = cache_dir / f"{cache_key}.parquet"
    if not cache_file.exists():
        return None

    try:
        return pq.read_table(cache_file)
    except Exception as e:
        # On any error (corruption, etc.), return None to trigger re-download
        print(f"Warning: Failed to load cache {cache_file}: {e}")
        return None


def _save_to_cache(cache_key: str, table: pa.Table) -> None:
    """Save Arrow table to cache."""
    cache_dir = _get_cache_dir()
    if not cache_dir:
        return

    cache_file = cache_dir / f"{cache_key}.parquet"
    try:
        pq.write_table(table, cache_file, compression="zstd")
        print(f"Cached data to {cache_file}")
    except Exception as e:
        print(f"Warning: Failed to save cache {cache_file}: {e}")


def _install_duckdb_extension(name: str, max_retries: int = 3) -> None:
    """Install and load a DuckDB extension with retry logic for flaky CI environments."""
    for attempt in range(max_retries):
        try:
            duckdb.execute(f"INSTALL {name}; LOAD {name};")
            return
        except duckdb.IOException:
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
            else:
                raise


@functools.lru_cache(maxsize=1)
def demo_project(sp: Spiral) -> Project:
    return sp.create_project(id_prefix="demo")


@functools.lru_cache(maxsize=1)
def images(sp: Spiral, limit=10) -> Table:
    table = demo_project(sp).create_table(
        "openimages.images-v1", key_schema=pa.schema([("idx", pa.int64())]), exist_ok=False
    )

    # Try to load from cache first
    # Use a hash of the URL to create a stable cache key
    url = "https://storage.googleapis.com/cvdf-datasets/oid/open-images-dataset-validation.tsv"
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    cache_key = _cache_key("images", "v1", f"url-{url_hash}", f"limit-{limit}")
    df = _get_cached_table(cache_key)

    if df is None:
        # Cache miss - download from Google Cloud Storage
        print(f"Cache miss for {cache_key}, downloading from GCS...")
        # Load URLs from a TSV file
        df_pandas = pd.read_csv(
            url,
            names=["url", "size", "etag"],
            skiprows=1,
            sep="\t",
            header=None,
        )
        # For this example, we load just a few rows, but Spiral can handle many more.
        df = pa.Table.from_pandas(df_pandas[:limit])
        df = df.append_column("idx", pa.array(range(len(df))))

        # Save to cache for future runs
        _save_to_cache(cache_key, df)
    else:
        print(f"Cache hit for {cache_key}")

    # Write just the metadata - lightweight and fast
    table.write(df)
    return table


@functools.lru_cache(maxsize=1)
def gharchive(sp: Spiral, limit=100, period=None) -> Table:
    if period is None:
        period = pd.Period("2023-01-01T00:00:00Z", freq="h")

    # Try to load from cache first
    period_str = f"{period.strftime('%Y-%m-%d')}-{str(period.hour)}"
    cache_key = _cache_key("gharchive", "v1", f"period-{period_str}", f"limit-{limit}")
    cached_events = _get_cached_table(cache_key)

    if cached_events is None:
        # Cache miss - download from gharchive
        print(f"Cache miss for {cache_key}, downloading from gharchive.org...")
        _install_duckdb_extension("httpfs")

        json_gz_url = f"https://data.gharchive.org/{period_str}.json.gz"
        arrow_table = (
            duckdb.read_json(json_gz_url, union_by_name=True)
            .limit(limit)
            .select("""
            * REPLACE (
                cast(created_at AS TIMESTAMP_MS) AS created_at,
            )
            """)
            .to_arrow_table()
        )

        events = duckdb.from_arrow(arrow_table).order("created_at, id").distinct().to_arrow_table()
        events = (
            events.drop_columns("id")
            .add_column(0, "id", events["id"].cast(pa.large_string()))
            .drop_columns("created_at")
            .add_column(0, "created_at", events["created_at"].cast(pa.timestamp("ms")))
            .drop_columns("org")
        )

        # Save to cache for future runs
        _save_to_cache(cache_key, events)
    else:
        print(f"Cache hit for {cache_key}")
        events = cached_events

    key_schema = pa.schema([("created_at", pa.timestamp("ms")), ("id", pa.string_view())])
    table = demo_project(sp).create_table("gharchive.events", key_schema=key_schema, exist_ok=False)
    table.write(events, push_down_nulls=True)
    return table


@functools.lru_cache(maxsize=1)
def fineweb(sp: Spiral, limit=100) -> Table:
    table = demo_project(sp).create_table(
        "fineweb.v1", key_schema=pa.schema([("id", pa.string_view())]), exist_ok=False
    )

    # Try to load from cache first
    cache_key = _cache_key("fineweb", "v1", f"limit-{limit}")
    arrow_table = _get_cached_table(cache_key)

    if arrow_table is None:
        # Cache miss - download from HuggingFace
        print(f"Cache miss for {cache_key}, downloading from HuggingFace...")
        ds = load_dataset("HuggingFaceFW/fineweb", "sample-10BT", streaming=True)
        data = ds["train"].take(limit)
        arrow_table = pa.Table.from_pylist(data.to_list())

        # Save to cache for future runs
        _save_to_cache(cache_key, arrow_table)
    else:
        print(f"Cache hit for {cache_key}")

    table.write(arrow_table, push_down_nulls=True)
    return table
