from collections.abc import Callable
from typing import Annotated

import questionary
import rich
import rich.table
import typer
from questionary import Choice
from typer import Argument, Option

from spiral import Spiral
from spiral.api.projects import TableResource
from spiral.cli import CONSOLE, ERR_CONSOLE, AsyncTyper, state
from spiral.cli.types import ProjectArg
from spiral.debug.manifests import display_manifests, display_scan_manifests
from spiral.table import Table

app = AsyncTyper(short_help="Spiral Tables.")


def ask_table(project_id: str, title: str = "Select a table") -> str:
    tables: list[TableResource] = list(state.spiral.project(project_id).list_tables())

    if not tables:
        ERR_CONSOLE.print("No tables found")
        raise typer.Exit(1)

    return questionary.select(  # pyright: ignore[reportAny]
        title,
        choices=[
            Choice(title=f"{table.dataset}.{table.table}", value=f"{table.dataset}.{table.table}")
            for table in sorted(tables, key=lambda t: (t.dataset, t.table))
        ],
    ).ask()


def get_table(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
) -> tuple[str, Table]:
    if table is None:
        identifier = ask_table(project)
    else:
        identifier = table
        if dataset is not None:
            identifier = f"{dataset}.{table}"
    return identifier, state.spiral.project(project).table(identifier)


@app.command(help="List tables.")
def ls(
    project: ProjectArg,
):
    tables = Spiral().project(project).list_tables()

    rich_table = rich.table.Table("id", "dataset", "name", title="Spiral tables")
    for table in tables:
        rich_table.add_row(table.id, table.dataset, table.table)
    CONSOLE.print(rich_table)


@app.command(help="Show the leading rows of the table.")
def head(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    n: Annotated[int, Option("-n", help="Maximum number of rows to show. Defaults to 10.")] = 10,
):
    try:
        import polars as pl
    except ImportError:
        # The escape is for rich which elides teh entire [polars] otherwise.
        CONSOLE.print("""Polars is required for this command, please execute:
    pip install 'pyspiral\\[polars]'""")
        raise typer.Exit(1)

    _, t = get_table(project, table, dataset)

    with pl.Config(tbl_rows=-1):
        CONSOLE.print(t.to_polars_lazy_frame().limit(n).collect())


def validate_non_empty_str(text: str) -> bool | str:
    if len(text) > 0:
        return True

    return "Must provide at least one character."


def get_string(message: str, validate: Callable[[str], bool | str] = validate_non_empty_str) -> str:
    return questionary.text(message, validate=validate).ask()


@app.command(help="Move table to a different dataset.")
def move(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    new_dataset: Annotated[str | None, Option(help="New dataset name.")] = None,
):
    identifier, _ = get_table(project, table, dataset)
    if new_dataset is None:
        new_dataset = get_string("Provide a new dataset name")

    state.spiral.project(project).move_table(identifier, new_dataset)
    CONSOLE.print("Success.")


@app.command(help="Rename table.")
def rename(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    new_table: Annotated[str | None, Option(help="New table name.")] = None,
):
    identifier, _ = get_table(project, table, dataset)
    if new_table is None:
        new_table = get_string("Provide a new table name")

    state.spiral.project(project).rename_table(identifier, new_table)
    CONSOLE.print("Success.")


@app.command(help="Drop table.")
def drop(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    identifier, _ = get_table(project, table, dataset)

    confirm = questionary.confirm(f"Are you sure you want to drop table '{identifier}'?").ask()
    if not confirm:
        CONSOLE.print("Aborted.")
        raise typer.Exit(0)

    state.spiral.project(project).drop_table(identifier)
    CONSOLE.print("Success.")


@app.command(help="Show the table key schema.")
def key_schema(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, t = get_table(project, table, dataset)
    CONSOLE.print(t.key_schema)


@app.command(help="Compute the full table schema.")
def schema(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, t = get_table(project, table, dataset)
    CONSOLE.print(t.schema())


@app.command(help="Fetch Write-Ahead-Log.")
def wal(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, t = get_table(project, table, dataset)
    wal_ = t.core.get_wal(asof=None)
    # Don't use CONSOLE.print here so that it can be piped.
    print(wal_)


@app.command(help="Flush Write-Ahead-Log.")
def flush(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    identifier, t = get_table(project, table, dataset)
    state.spiral.internal.flush_wal(t.core)  # pyright: ignore[reportPrivateUsage]
    CONSOLE.print(f"Flushed WAL for table {identifier} in project {project}.")


@app.command(help="Truncate column group metadata.")
def truncate(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    identifier, t = get_table(project, table, dataset)

    # Ask for confirmation
    confirm = questionary.confirm(
        f"Are you sure you want to truncate metadata for table '{identifier}'? This will break as-of queries."
    ).ask()
    if not confirm:
        CONSOLE.print("Aborted.")
        raise typer.Exit(0)

    state.spiral.internal.truncate_metadata(t.core)
    CONSOLE.print(f"Truncated metadata for table {identifier} in project {project}.")


@app.command(help="Display all fragments from metadata.", deprecated="Use 'fragments' instead.")
def manifests(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    max_rows: Annotated[int | None, Option(help="Maximum number of rows to show per manifest.")] = None,
):
    fragments(project, table, dataset, max_rows)


@app.command(help="Display all fragments from metadata.")
def fragments(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    max_rows: Annotated[int | None, Option(help="Maximum number of fragments to show per manifest.")] = None,
):
    _, t = get_table(project, table, dataset)
    s = t.snapshot()
    cgs = s.core.column_groups()
    key_space_manifest = state.spiral.internal.key_space_manifest(s.core)
    column_group_manifests = [(cg, state.spiral.internal.column_group_manifest(s.core, cg)) for cg in cgs]
    display_manifests(key_space_manifest, column_group_manifests, t.key_schema, max_rows)


@app.command(help="Display the fragments used in a scan of a given column group.")
def fragments_scan(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    column_group: Annotated[str, Argument(help="Dot-separated column group path.")] = ".",
):
    _, t = get_table(project, table, dataset)
    scan = state.spiral.scan(t[column_group] if column_group != "." else t)
    display_scan_manifests(scan.core)


@app.command(help="Visualize the scan of a given column group.")
def debug_scan(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    column_group: Annotated[str, Argument(help="Dot-separated column group path.")] = ".",
):
    _, t = get_table(project, table, dataset)
    scan = state.spiral.scan(t[column_group] if column_group != "." else t)
    scan._debug()  # pyright: ignore[reportPrivateUsage]
