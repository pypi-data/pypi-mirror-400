"""Embeddings API commands."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import typer
from rich.table import Table

from orter.utils import apply_int_filter, parse_filter, parse_sort
from orter.context import make_client_from_ctx
from orter.types import JSONObject, JSONValue
from orter.utils import FilterOperator, SortOrder, console, print_json

app = typer.Typer(name="embeddings", help="Embeddings API", no_args_is_help=True)


class SortField(str, Enum):
    """Sortable fields for embeddings models."""

    ID = "id"
    NAME = "name"
    CONTEXT_LENGTH = "context_length"


@dataclass(frozen=True, slots=True)
class _EmbeddingModelRow:
    model_id: str
    name: str
    context_length: int | None


def _extract_embedding_rows(items: Iterable[JSONValue]) -> list[_EmbeddingModelRow]:
    rows: list[_EmbeddingModelRow] = []
    for item in items:
        if isinstance(item, dict):
            model_id = str(item.get("id", ""))
            name = str(item.get("name", ""))
            context_length = item.get("context_length")
            if isinstance(context_length, int):
                ctx_i: int | None = context_length
            else:
                ctx_i = None
            rows.append(
                _EmbeddingModelRow(
                    model_id=model_id,
                    name=name,
                    context_length=ctx_i,
                )
            )
    return rows


def _parse_sort_for_embeddings(sort_str: str) -> tuple[SortField, SortOrder]:
    """Parse sort string for embeddings models."""
    valid_fields = [field.value for field in SortField]
    field, order = parse_sort(sort_str, valid_fields)
    try:
        sort_field = SortField(field)
    except ValueError:
        raise typer.BadParameter(
            f"Invalid sort field: {field}. Valid fields: {', '.join(valid_fields)}"
        )
    try:
        sort_order = SortOrder(order)
    except ValueError:
        raise typer.BadParameter(
            f"Invalid sort order: {order}. Valid orders: asc, desc"
        )
    return (sort_field, sort_order)


def _apply_embedding_filter(
    rows: list[_EmbeddingModelRow], field: str, operator: FilterOperator, value: str
) -> list[_EmbeddingModelRow]:
    """Apply a single filter to embedding model rows."""
    filtered: list[_EmbeddingModelRow] = []

    for row in rows:
        if field == "context_length":
            try:
                filter_value = int(value)
            except ValueError:
                raise typer.BadParameter(f"Invalid context_length value: {value}")
            row_value = row.context_length
            if apply_int_filter(row_value, filter_value, operator):
                filtered.append(row)
        else:
            raise typer.BadParameter(
                f"Invalid field: {field}. Valid fields: context_length"
            )

    return filtered


def _filter_embedding_rows(
    rows: list[_EmbeddingModelRow],
    *,
    filters: list[str] | None = None,
) -> list[_EmbeddingModelRow]:
    """Filter rows based on criteria.

    Args:
        rows: Rows to filter
        filters: List of filter strings in format 'field:operator:value'
    """
    if not filters:
        return rows

    filtered = rows
    for filter_str in filters:
        field, operator, value = parse_filter(filter_str)
        filtered = _apply_embedding_filter(filtered, field, operator, value)

    return filtered


def _sort_embedding_rows(
    rows: list[_EmbeddingModelRow],
    *,
    sort_by: SortField | None = None,
    order: SortOrder | None = None,
) -> list[_EmbeddingModelRow]:
    """Sort rows by field."""
    if sort_by is None:
        return rows

    reverse = (order or SortOrder.ASC) == SortOrder.DESC

    def get_sort_key(row: _EmbeddingModelRow) -> tuple[Any, ...]:
        if sort_by == SortField.ID:
            return (row.model_id.lower(),)
        elif sort_by == SortField.NAME:
            return (row.name.lower() if row.name else "",)
        elif sort_by == SortField.CONTEXT_LENGTH:
            return (row.context_length if row.context_length is not None else -1,)
        else:
            return (row.model_id.lower(),)

    return sorted(rows, key=get_sort_key, reverse=reverse)


def _render_embedding_table(rows: list[_EmbeddingModelRow]) -> None:
    table = Table(title="Embeddings Models", show_lines=False)
    table.add_column("id", overflow="fold")
    table.add_column("name", overflow="fold")
    table.add_column("ctx", justify="right")
    for r in rows:
        table.add_row(
            r.model_id,
            r.name,
            str(r.context_length) if r.context_length is not None else "-",
        )
    console.print(table)


@app.command("create")
def embeddings_create(
    ctx: typer.Context,
    input_text: str = typer.Option(..., "--input", "-i", help="Input text to embed"),
    model: str = typer.Option(
        "text-embedding-3-large", "--model", help="Embedding model"
    ),
    encoding_format: str | None = typer.Option(
        None, "--encoding-format", help="Encoding format (float or base64)"
    ),
    dimensions: int | None = typer.Option(None, "--dimensions", help="Dimensions"),
    user: str | None = typer.Option(None, "--user", help="User identifier"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Create embeddings."""
    payload: JSONObject = {"input": input_text, "model": model}
    if encoding_format:
        payload["encoding_format"] = encoding_format
    if dimensions is not None:
        payload["dimensions"] = dimensions
    if user:
        payload["user"] = user

    with make_client_from_ctx(ctx) as client:
        data = client.create_embeddings(payload=payload)
    print_json(data, pretty=json_output)


@app.command("models")
def embeddings_models(
    ctx: typer.Context,
    search: str | None = typer.Option(
        None, "--search", "-s", help="Filter by id/name contains"
    ),
    limit: int = typer.Option(20, "--limit", "-n", min=1, max=500),
    sort: str | None = typer.Option(
        None,
        "--sort",
        metavar="FIELD:ORDER",
        help="Sort by field:order (e.g., 'context_length:desc' or 'name:asc').\n\n- Fields: id, name, context_length\n\n- Orders: asc (ascending), desc (descending)",
    ),
    filter: list[str] | None = typer.Option(
        None,
        "--filter",
        "-f",
        metavar="FIELD:OPERATOR:VALUE",
        help="Filter by field:operator:value (e.g., 'context_length:ge:100000'). Can be used multiple times.\n\n- Operators: ge (≥), le (≤), gt (>), lt (<), eq (=). \n\n- Fields: context_length",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """List embeddings models."""
    with make_client_from_ctx(ctx) as client:
        data = client.list_embeddings_models()

    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable table output
    if isinstance(data, dict) and "data" in data:
        items = data["data"]
        if isinstance(items, list) and len(items) > 0:
            rows = _extract_embedding_rows(items)
            total_count = len(rows)

            # Apply search filter
            if search:
                s = search.lower()
                rows = [
                    r for r in rows if s in r.model_id.lower() or s in r.name.lower()
                ]

            # Apply filters
            rows = _filter_embedding_rows(rows, filters=filter)

            filtered_count = len(rows)

            # Apply sorting
            if sort:
                sort_by, sort_order = _parse_sort_for_embeddings(sort)
                rows = _sort_embedding_rows(rows, sort_by=sort_by, order=sort_order)

            # Apply limit
            displayed_count = len(rows)
            rows = rows[:limit]
            _render_embedding_table(rows)

            # Show count message if there are more results
            if displayed_count > limit:
                console.print(
                    f"\nShowing first {limit} of {displayed_count} models"
                    + (
                        f" (filtered from {total_count} total)"
                        if filtered_count < total_count
                        else ""
                    )
                    + ". Use --json for full payload, or --limit to see more."
                )
            elif filtered_count < total_count:
                console.print(
                    f"\nShowing {displayed_count} models (filtered from {total_count} total)."
                    + " Use --json for full payload, or adjust filters to see more."
                )
            else:
                console.print(
                    "\nTip: use `--json` for full payload, or `--search`/`--limit`/`--sort`/`--filter` to narrow."
                )
        else:
            console.print("No embeddings models found.")
    else:
        print_json(data, pretty=True)
