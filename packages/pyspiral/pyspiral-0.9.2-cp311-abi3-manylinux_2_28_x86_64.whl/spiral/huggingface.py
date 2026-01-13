"""
This module provides utilities for bidirectional HuggingFace <-> Spiral conversion.

Ingesting HuggingFace datasets into Spiral:
    from spiral.huggingface import ingest_dataset
    from spiral import Spiral

    sp = Spiral()
    project = sp.project("my-project")

    # Ingest a HuggingFace dataset
    from datasets import load_dataset
    hf_dataset = load_dataset("squad", split="train")

    table = ingest_dataset(hf_dataset, project, "squad_train", key_columns="id")

Converting Spiral scans to HuggingFace IterableDataset:
    # This is typically accessed via scan.to_iterable_dataset()
    from spiral.huggingface import to_iterable_dataset

Requires the [huggingface] extra: pip install pyspiral[huggingface]
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import TYPE_CHECKING

import pyarrow as pa

if TYPE_CHECKING:
    from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict
    from datasets.features import Features

    from spiral import Project, Table

__all__ = ["ingest_dataset", "to_iterable_dataset"]

DEFAULT_ROW_INDEX_COLUMN = "__row_idx__"
DEFAULT_BATCH_SIZE = 100_000
DEFAULT_COMMIT_EVERY = 25


def _check_huggingface_installed() -> None:
    """Raise ImportError with helpful message if datasets not installed."""
    try:
        import datasets  # noqa: F401
    except ImportError:
        raise ImportError(
            "The 'datasets' package is required for HuggingFace integration. "
            "Install it with: pip install 'pyspiral[huggingface]'"
        ) from None


def _add_row_index_column(table: pa.Table, offset: int = 0) -> pa.Table:
    """Add a __row_idx__ column as the first column."""
    row_count = len(table)
    row_idx = pa.array(range(offset, offset + row_count), type=pa.uint64())
    return table.add_column(0, DEFAULT_ROW_INDEX_COLUMN, row_idx)


def _validate_key_columns(schema: pa.Schema, key_columns: str | Sequence[str]) -> list[str]:
    """Validate that key columns exist in the schema and return as list."""
    if isinstance(key_columns, str):
        key_columns = [key_columns]
    else:
        key_columns = list(key_columns)

    schema_names = set(schema.names)
    for col in key_columns:
        if col not in schema_names:
            raise ValueError(f"Key column '{col}' not found in dataset schema. Available columns: {schema.names}")

    return key_columns


def _extract_key_schema(schema: pa.Schema, key_columns: list[str]) -> pa.Schema:
    """Extract key schema from existing columns."""
    key_fields = [schema.field(col) for col in key_columns]
    return pa.schema(key_fields)


def _reorder_columns_keys_first(table: pa.Table, key_columns: list[str]) -> pa.Table:
    """Reorder table columns so key columns come first."""
    non_key_columns = [name for name in table.column_names if name not in key_columns]
    new_order = key_columns + non_key_columns
    return table.select(new_order)


def _features_to_arrow_schema(features: Features) -> pa.Schema:
    """Convert HuggingFace Features to Arrow schema."""
    return features.arrow_schema


def _ingest_in_memory_dataset(
    dataset: Dataset,
    project: Project,
    table_name: str,
    key_columns: str | Sequence[str] | None,
    push_down_nulls: bool,
    exist_ok: bool,
) -> Table:
    """Ingest an in-memory HuggingFace Dataset."""
    # Get Arrow table directly from HuggingFace
    arrow_table = dataset.data.table

    # Handle key columns
    if key_columns is None:
        # Auto-generate row index
        arrow_table = _add_row_index_column(arrow_table)
        key_schema = pa.schema([(DEFAULT_ROW_INDEX_COLUMN, pa.uint64())])
    else:
        key_cols = _validate_key_columns(arrow_table.schema, key_columns)
        key_schema = _extract_key_schema(arrow_table.schema, key_cols)
        arrow_table = _reorder_columns_keys_first(arrow_table, key_cols)

    # Create table and write
    table = project.create_table(table_name, key_schema=key_schema, exist_ok=exist_ok)
    table.write(arrow_table, push_down_nulls=push_down_nulls)

    return table


def _ingest_iterable_dataset(
    dataset: IterableDataset,
    project: Project,
    table_name: str,
    key_columns: str | Sequence[str] | None,
    batch_size: int,
    commit_every: int,
    push_down_nulls: bool,
    exist_ok: bool,
) -> Table:
    """Ingest a streaming HuggingFace IterableDataset."""
    # Infer key schema from features
    features = dataset.features
    if features is None:
        raise ValueError(
            "Cannot infer schema from IterableDataset without features. "
            "Consider materializing the dataset first with dataset.take(n) or provide features."
        )

    arrow_schema = _features_to_arrow_schema(features)

    # Determine key schema
    if key_columns is None:
        key_schema = pa.schema([(DEFAULT_ROW_INDEX_COLUMN, pa.uint64())])
    else:
        key_cols = _validate_key_columns(arrow_schema, key_columns)
        key_schema = _extract_key_schema(arrow_schema, key_cols)

    # Create table
    table = project.create_table(table_name, key_schema=key_schema, exist_ok=exist_ok)

    # Iterate with batching and transactions
    row_offset = 0
    tx = table.txn()
    tx_ops = 0
    batch_buffer: list[dict] = []

    for row in dataset:
        batch_buffer.append(row)

        if len(batch_buffer) >= batch_size:
            arrow_batch = _rows_to_arrow_table(batch_buffer, features, row_offset, key_columns)
            tx.write(arrow_batch, push_down_nulls=push_down_nulls)
            tx_ops += 1
            row_offset += len(batch_buffer)
            batch_buffer = []

            if tx_ops >= commit_every:
                tx.commit()
                tx = table.txn()
                tx_ops = 0

    # Handle remaining rows
    if batch_buffer:
        arrow_batch = _rows_to_arrow_table(batch_buffer, features, row_offset, key_columns)
        tx.write(arrow_batch, push_down_nulls=push_down_nulls)
        tx_ops += 1

    if tx_ops > 0:
        tx.commit()

    return table


def _rows_to_arrow_table(
    rows: list[dict],
    features: Features,
    offset: int,
    key_columns: str | Sequence[str] | None,
) -> pa.Table:
    """Convert a list of row dicts to an Arrow table with proper schema."""
    from datasets import Dataset

    # Create a temporary Dataset to leverage HF's Arrow conversion
    temp_dataset = Dataset.from_list(rows, features=features)
    arrow_table = temp_dataset.data.table

    # Handle key columns
    if key_columns is None:
        arrow_table = _add_row_index_column(arrow_table, offset)
    else:
        key_cols = _validate_key_columns(arrow_table.schema, key_columns)
        arrow_table = _reorder_columns_keys_first(arrow_table, key_cols)

    return arrow_table


def _ingest_dataset_dict(
    dataset_dict: DatasetDict,
    project: Project,
    table_name: str,
    key_columns: str | Sequence[str] | None,
    push_down_nulls: bool,
    exist_ok: bool,
) -> dict[str, Table]:
    """Ingest a HuggingFace DatasetDict, creating one table per split."""
    tables = {}
    for split_name, dataset in dataset_dict.items():
        split_table_name = f"{table_name}.{split_name}"
        tables[split_name] = _ingest_in_memory_dataset(
            dataset,
            project,
            split_table_name,
            key_columns,
            push_down_nulls,
            exist_ok,
        )
    return tables


def _ingest_iterable_dataset_dict(
    dataset_dict: IterableDatasetDict,
    project: Project,
    table_name: str,
    key_columns: str | Sequence[str] | None,
    batch_size: int,
    commit_every: int,
    push_down_nulls: bool,
    exist_ok: bool,
) -> dict[str, Table]:
    """Ingest a HuggingFace IterableDatasetDict, creating one table per split."""
    tables = {}
    for split_name, dataset in dataset_dict.items():
        split_table_name = f"{table_name}.{split_name}"
        tables[split_name] = _ingest_iterable_dataset(
            dataset,
            project,
            split_table_name,
            key_columns,
            batch_size,
            commit_every,
            push_down_nulls,
            exist_ok,
        )
    return tables


def ingest_dataset(
    dataset: Dataset | IterableDataset | DatasetDict | IterableDatasetDict,
    project: Project,
    table_name: str,
    *,
    key_columns: str | Sequence[str] | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    commit_every: int = DEFAULT_COMMIT_EVERY,
    push_down_nulls: bool = True,
    exist_ok: bool = False,
) -> Table | dict[str, Table]:
    """
    Ingest a HuggingFace dataset into Spiral.

    Args:
        dataset: A HuggingFace Dataset, IterableDataset, DatasetDict, or IterableDatasetDict.
        project: The Spiral project to create the table(s) in.
        table_name: Base name for the table. For DatasetDict, tables are created as
                    `{table_name}.{split}` (e.g., `my_dataset.train`, `my_dataset.test`).
        key_columns: Column(s) to use as the primary key. If None, a `__row_idx__`
                     column is auto-generated as a uint64 key.
        batch_size: Number of rows to buffer before writing (for streaming datasets).
                    Default is 100,000 (matching fineweb.py pattern).
        commit_every: Number of write operations before committing a transaction.
                      Default is 25 (matching fineweb.py pattern).
        push_down_nulls: Whether to push down nullable structs to children.
        exist_ok: If True, allow writing to existing tables.

    Returns:
        A single Table for Dataset/IterableDataset, or a dict mapping split names
        to Tables for DatasetDict/IterableDatasetDict.

    Raises:
        ImportError: If `datasets` package is not installed.
        ValueError: If key_columns don't exist in the dataset schema.
        TypeError: If dataset is not a supported HuggingFace type.

    Examples:
        Basic ingestion with auto-generated key:

        >>> from datasets import load_dataset
        >>> from spiral import Spiral
        >>> from spiral.huggingface import ingest_dataset
        >>> sp = Spiral()
        >>> project = sp.project("my-project")
        >>> hf_ds = load_dataset("squad", split="train")
        >>> table = ingest_dataset(hf_ds, project, "squad_train")

        With custom key column:

        >>> table = ingest_dataset(hf_ds, project, "squad_train", key_columns="id")

        DatasetDict creates multiple tables:

        >>> hf_dict = load_dataset("squad")  # Returns DatasetDict
        >>> tables = ingest_dataset(hf_dict, project, "squad")
        >>> tables["train"]  # squad.train table
        >>> tables["validation"]  # squad.validation table
    """
    _check_huggingface_installed()

    from datasets import Dataset, DatasetDict, IterableDataset, IterableDatasetDict

    if isinstance(dataset, DatasetDict):
        return _ingest_dataset_dict(
            dataset,
            project,
            table_name,
            key_columns,
            push_down_nulls,
            exist_ok,
        )
    elif isinstance(dataset, IterableDatasetDict):
        return _ingest_iterable_dataset_dict(
            dataset,
            project,
            table_name,
            key_columns,
            batch_size,
            commit_every,
            push_down_nulls,
            exist_ok,
        )
    elif isinstance(dataset, Dataset):
        return _ingest_in_memory_dataset(
            dataset,
            project,
            table_name,
            key_columns,
            push_down_nulls,
            exist_ok,
        )
    elif isinstance(dataset, IterableDataset):
        return _ingest_iterable_dataset(
            dataset,
            project,
            table_name,
            key_columns,
            batch_size,
            commit_every,
            push_down_nulls,
            exist_ok,
        )
    else:
        raise TypeError(
            f"Unsupported dataset type: {type(dataset).__name__}. "
            "Expected Dataset, IterableDataset, DatasetDict, or IterableDatasetDict."
        )


# =============================================================================
# Spiral -> HuggingFace conversion
# =============================================================================


def to_iterable_dataset(stream: pa.RecordBatchReader) -> IterableDataset:
    """
    Convert a PyArrow RecordBatchReader to a HuggingFace IterableDataset.

    This is typically accessed via scan.to_iterable_dataset() rather than directly.

    Args:
        stream: A PyArrow RecordBatchReader, typically from a Spiral scan.

    Returns:
        A HuggingFace IterableDataset that yields rows from the stream.

    Example:
        >>> from spiral import Spiral
        >>> sp = Spiral()
        >>> table = sp.project("my-project").table("my-table")
        >>> scan = sp.scan(table)
        >>> hf_dataset = scan.to_iterable_dataset()  # Uses this function internally
    """
    _check_huggingface_installed()

    from datasets import DatasetInfo, Features
    from datasets.builder import ArrowExamplesIterable
    from datasets.iterable_dataset import IterableDataset as HFIterableDataset

    def _generate_tables(**kwargs) -> Iterator[tuple[int, pa.Table]]:
        # This key is unused when training with IterableDataset.
        # Default implementation returns shard id, e.g. parquet row group id.
        for i, rb in enumerate(stream):
            yield i, pa.Table.from_batches([rb], stream.schema)

    # TODO(marko): This is temporary until we stop returning IterableDataset from this function.
    class _IterableDataset(HFIterableDataset):
        # Diff with datasets.iterable_dataset.IterableDataset:
        # - Removes torch handling which attempts to handle worker processes.
        # - Assumes arrow iterator.
        def __iter__(self):
            from datasets.formatting import get_formatter

            prepared_ex_iterable = self._prepare_ex_iterable_for_iteration()
            if self._formatting and (prepared_ex_iterable.iter_arrow or self._formatting.is_table):
                formatter = get_formatter(self._formatting.format_type, features=self.features)
                iterator = prepared_ex_iterable.iter_arrow()
                for key, pa_table in iterator:
                    yield formatter.format_row(pa_table)
                return

            for key, example in prepared_ex_iterable:
                # no need to format thanks to FormattedExamplesIterable
                yield example

        def map(self, *args, **kwargs):
            # Map constructs a new IterableDataset, so we need to "patch" it
            base = super().map(*args, **kwargs)
            if isinstance(base, HFIterableDataset):
                # Patch __iter__ to avoid torch handling
                base.__class__ = _IterableDataset  # type: ignore
            return base

    class _ArrowExamplesIterable(ArrowExamplesIterable):
        def __init__(
            self,
            generate_tables_fn: Callable[..., Iterator[tuple[int, pa.Table]]],
            features: Features,
        ):
            # NOTE: generate_tables_fn type annotations are wrong, return type must be an iterable of tuples.
            super().__init__(generate_tables_fn, kwargs={})  # type: ignore
            self._features = features

        @property
        def is_typed(self) -> bool:
            return True

        @property
        def features(self) -> Features:
            return self._features

    target_features = Features.from_arrow_schema(stream.schema)
    ex_iterable = _ArrowExamplesIterable(_generate_tables, target_features)
    info = DatasetInfo(features=target_features)
    return _IterableDataset(ex_iterable=ex_iterable, info=info)
