from rich.console import Console
from rich.table import Table

from spiral import datetime_
from spiral.core._tools import pretty_key
from spiral.core.table import Scan
from spiral.core.table.manifests import FragmentManifest
from spiral.core.table.spec import ColumnGroup, Schema
from spiral.debug.metrics import _format_bytes


def display_scan_manifests(scan: Scan):
    """Display all manifests in a scan."""
    if len(scan.table_ids()) != 1:
        raise NotImplementedError("Multiple table scans are not supported.")
    table_id = scan.table_ids()[0]
    key_space_manifest = scan.key_space_manifest(table_id)
    column_group_manifests = [
        (column_group, scan.column_group_manifest(column_group)) for column_group in scan.column_groups()
    ]

    display_manifests(key_space_manifest, column_group_manifests, scan.key_schema(), None)


def display_manifests(
    key_space_manifest: FragmentManifest,
    column_group_manifests: list[tuple[ColumnGroup, FragmentManifest]],
    key_schema: Schema,
    max_rows: int | None,
):
    _table_of_fragments(key_space_manifest, title="Key Space manifest", key_schema=key_schema, max_rows=max_rows)

    for column_group, column_group_manifest in column_group_manifests:
        _table_of_fragments(
            column_group_manifest,
            title=f"Column Group manifest for {str(column_group)}",
            key_schema=key_schema,
            max_rows=max_rows,
        )


def _table_of_fragments(manifest: FragmentManifest, title: str, key_schema: Schema, max_rows: int | None):
    """Display fragments in a formatted table."""
    # Calculate summary statistics
    total_size = sum(fragment.size_bytes for fragment in manifest)
    total_metadata_size = sum(len(fragment.format_metadata or b"") for fragment in manifest)
    fragment_count = len(manifest)
    avg_size = total_size / fragment_count if fragment_count > 0 else 0

    # Print title and summary
    console = Console()
    console.print(f"\n\n{title}")
    console.print(
        f"{fragment_count} fragments, "
        f"total: {_format_bytes(total_size)}, "
        f"avg: {_format_bytes(int(avg_size))}, "
        f"metadata: {_format_bytes(total_metadata_size)}, "
        f"max rows shown: {max_rows}"
    )

    # Create rich table
    table = Table(title=None, show_header=True, header_style="bold")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Data", justify="right")
    table.add_column("Metadata", justify="right")
    table.add_column("Format", justify="center")
    table.add_column("Key Space", justify="center")
    table.add_column("Key Span", justify="center")
    table.add_column("Key Range", justify="center")
    table.add_column("Level", justify="center")
    table.add_column("Committed At", justify="center")
    table.add_column("Compacted At", justify="center")

    # Add each fragment as a row
    for i, fragment in enumerate(manifest):
        if max_rows is not None and i >= max_rows:
            break

        committed_str = (
            datetime_.from_timestamp_micros(fragment.committed_at).strftime("%Y-%m-%d %H:%M:%S")
            if fragment.committed_at
            else "N/A"
        )
        compacted_str = (
            datetime_.from_timestamp_micros(fragment.compacted_at).strftime("%Y-%m-%d %H:%M:%S")
            if fragment.compacted_at
            else "N/A"
        )

        data_size = _format_bytes(fragment.size_bytes)
        metadata_size = _format_bytes(len(fragment.format_metadata or b""))
        key_space = fragment.ks_id
        key_span = f"{fragment.key_span.begin}..{fragment.key_span.end}"
        min_key = pretty_key(bytes(fragment.key_extent.min), key_schema)
        max_key = pretty_key(bytes(fragment.key_extent.max), key_schema)
        single_line = f"{min_key}..{max_key}"
        if len(single_line) <= 50:
            key_range = single_line
        else:
            key_range = f"{min_key}\n..{max_key}"

        table.add_row(
            fragment.id,
            data_size,
            metadata_size,
            str(fragment.format),
            key_space,
            key_span,
            key_range,
            str(fragment.level),
            committed_str,
            compacted_str,
        )

    console.print(table)
