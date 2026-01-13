"""Endpoints API commands."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import typer
from rich.table import Table

from orter.utils import (
    apply_float_filter,
    apply_int_filter,
    parse_filter,
    parse_sort,
)
from orter.context import make_client_from_ctx
from orter.types import JSONValue
from orter.utils import FilterOperator, SortOrder, console, print_json

app = typer.Typer(name="endpoints", help="Endpoints API", no_args_is_help=True)

# Status code mapping for endpoints
STATUS_MAP: dict[str, str] = {
    "0": "Active",
    "-1": "Degraded",
    "-2": "Down",
    "-3": "Unknown",
    "-5": "Maintenance",
    "-10": "Disabled",
}


class SortField(str, Enum):
    """Sortable fields for endpoints."""

    NAME = "name"
    PROVIDER = "provider"
    TAG = "tag"
    CONTEXT_LENGTH = "context_length"
    STATUS = "status"
    UPTIME = "uptime"


@dataclass(frozen=True, slots=True)
class _EndpointRow:
    name: str
    provider: str
    tag: str
    context_length: int | None
    status: int
    status_display: str
    uptime: float | None
    # For ZDR endpoints
    model_name: str | None = None


def _format_status(status: JSONValue | None) -> tuple[int, str]:
    """Format status code to display string.

    Returns:
        Tuple of (status_code, status_display)
    """
    if status is None:
        return (-3, STATUS_MAP.get("-3", "Unknown"))

    # Handle both int and str status codes
    if isinstance(status, int):
        status_str = str(status)
        status_display = STATUS_MAP.get(status_str, f"Unknown ({status_str})")
        return (status, status_display)
    elif isinstance(status, str):
        status_int = int(status) if status.lstrip("-").isdigit() else -3
        status_display = STATUS_MAP.get(status, f"Unknown ({status})")
        return (status_int, status_display)

    # Fallback for other types
    status_str = str(status)
    return (-3, STATUS_MAP.get("-3", f"Unknown ({status_str})"))


def _format_uptime(uptime: JSONValue | None) -> tuple[float | None, str]:
    """Format uptime value to display string.

    Returns:
        Tuple of (uptime_raw, uptime_display)
    """
    if uptime is None:
        return (None, "-")
    if isinstance(uptime, (int, float)):
        return (float(uptime), f"{uptime:.1f}%")
    return (None, "-")


def _extract_endpoint_rows(endpoints: Iterable[JSONValue]) -> list[_EndpointRow]:
    """Extract endpoint data into structured rows."""
    rows: list[_EndpointRow] = []
    for endpoint in endpoints:
        if isinstance(endpoint, dict):
            name = str(endpoint.get("name", "-"))
            provider = str(endpoint.get("provider_name", "-"))
            tag = str(endpoint.get("tag", "-"))
            context_length = endpoint.get("context_length")
            if isinstance(context_length, int):
                ctx_i: int | None = context_length
            elif isinstance(context_length, str) and context_length.isdigit():
                ctx_i = int(context_length)
            else:
                ctx_i = None

            status_raw = endpoint.get("status")
            status_code, status_display = _format_status(status_raw)

            uptime_raw = endpoint.get("uptime_last_30m")
            uptime_value, _ = _format_uptime(uptime_raw)

            rows.append(
                _EndpointRow(
                    name=name,
                    provider=provider,
                    tag=tag,
                    context_length=ctx_i,
                    status=status_code,
                    status_display=status_display,
                    uptime=uptime_value,
                )
            )
    return rows


def _apply_filter(
    rows: list[_EndpointRow], field: str, operator: FilterOperator, value: str
) -> list[_EndpointRow]:
    """Apply a single filter to endpoint rows."""
    filtered: list[_EndpointRow] = []

    for row in rows:
        if field == "context_length":
            try:
                filter_value = int(value)
            except ValueError:
                raise typer.BadParameter(f"Invalid context_length value: {value}")
            if apply_int_filter(row.context_length, filter_value, operator):
                filtered.append(row)
        elif field == "status":
            try:
                filter_value = int(value)
            except ValueError:
                raise typer.BadParameter(f"Invalid status value: {value}")
            if apply_int_filter(row.status, filter_value, operator):
                filtered.append(row)
        elif field == "uptime":
            try:
                filter_value = float(value)
            except ValueError:
                raise typer.BadParameter(f"Invalid uptime value: {value}")
            if apply_float_filter(row.uptime, filter_value, operator):
                filtered.append(row)
        else:
            raise typer.BadParameter(
                f"Invalid field: {field}. Valid fields: context_length, status, uptime"
            )

        filtered.append(row)
    return filtered


def _parse_sort_for_endpoints(sort_str: str) -> tuple[SortField, SortOrder]:
    """Parse sort string for endpoints."""
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


def _filter_rows(
    rows: list[_EndpointRow],
    *,
    filters: list[str] | None = None,
) -> list[_EndpointRow]:
    """Filter rows based on criteria."""
    if not filters:
        return rows

    filtered = rows
    for filter_str in filters:
        field, operator, value = parse_filter(filter_str)
        filtered = _apply_filter(filtered, field, operator, value)

    return filtered


def _sort_rows(
    rows: list[_EndpointRow],
    *,
    sort_by: SortField | None = None,
    order: SortOrder | None = None,
) -> list[_EndpointRow]:
    """Sort rows by field."""
    if sort_by is None:
        return rows

    reverse = (order or SortOrder.ASC) == SortOrder.DESC

    def get_sort_key(row: _EndpointRow) -> tuple[Any, ...]:
        if sort_by == SortField.NAME:
            return (row.name.lower(),)
        elif sort_by == SortField.PROVIDER:
            return (row.provider.lower(),)
        elif sort_by == SortField.TAG:
            return (row.tag.lower(),)
        elif sort_by == SortField.CONTEXT_LENGTH:
            return (row.context_length if row.context_length is not None else -1,)
        elif sort_by == SortField.STATUS:
            return (row.status,)
        elif sort_by == SortField.UPTIME:
            return (row.uptime if row.uptime is not None else -1.0,)
        else:
            return (row.name.lower(),)

    return sorted(rows, key=get_sort_key, reverse=reverse)


def _render_table(rows: list[_EndpointRow], title: str) -> None:
    """Render endpoint table."""
    table = Table(title=title, show_lines=False, show_header=True)
    table.add_column("Name")
    table.add_column("Provider")
    table.add_column("Tag")
    table.add_column("Context Length", justify="right")
    table.add_column("Status")
    table.add_column("Uptime (30m)", justify="right")

    for row in rows:
        uptime_str = f"{row.uptime:.1f}%" if row.uptime is not None else "-"
        table.add_row(
            row.name,
            row.provider,
            row.tag,
            str(row.context_length) if row.context_length is not None else "-",
            row.status_display,
            uptime_str,
        )
    console.print(table)


@app.command("list")
def endpoints_list(
    ctx: typer.Context,
    author: str = typer.Argument(..., help="Model author (e.g., 'openai')"),
    slug: str = typer.Argument(..., help="Model slug (e.g., 'gpt-4o')"),
    search: str | None = typer.Option(
        None, "--search", "-s", help="Filter by name/provider/tag contains"
    ),
    limit: int = typer.Option(100, "--limit", "-n", min=1, max=500),
    sort: str | None = typer.Option(
        None,
        "--sort",
        metavar="FIELD:ORDER",
        help="Sort by field:order (e.g., 'uptime:desc' or 'status:asc').\n\n- Fields: name, provider, tag, context_length, status, uptime\n\n- Orders: asc (ascending), desc (descending)",
    ),
    filter: list[str] | None = typer.Option(
        None,
        "--filter",
        "-f",
        metavar="FIELD:OPERATOR:VALUE",
        help="Filter by field:operator:value (e.g., 'status:eq:0' or 'uptime:ge:95.0'). Can be used multiple times.\n\n- Operators: ge (≥), le (≤), gt (>), lt (<), eq (=). \n\n- Fields: context_length, status, uptime",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """List endpoints for a specific model."""
    with make_client_from_ctx(ctx) as client:
        data = client.list_endpoints(author=author, slug=slug)
    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable table output
    if isinstance(data, dict) and "data" in data:
        model_data = data["data"]
        if isinstance(model_data, dict):
            model_id = model_data.get("id", f"{author}/{slug}")
            endpoints = model_data.get("endpoints", [])
            if isinstance(endpoints, list) and len(endpoints) > 0:
                rows = _extract_endpoint_rows(endpoints)
                total_count = len(rows)

                # Apply search filter
                if search:
                    s = search.lower()
                    rows = [
                        r
                        for r in rows
                        if s in r.name.lower()
                        or s in r.provider.lower()
                        or s in r.tag.lower()
                    ]

                # Apply filters
                rows = _filter_rows(rows, filters=filter)
                filtered_count = len(rows)

                # Apply sorting
                if sort:
                    sort_by, sort_order = _parse_sort_for_endpoints(sort)
                    rows = _sort_rows(rows, sort_by=sort_by, order=sort_order)

                # Apply limit
                displayed_count = len(rows)
                rows = rows[:limit]
                _render_table(rows, title=f"Endpoints for {model_id}")

                # Show count message
                if displayed_count > limit:
                    console.print(
                        f"\nShowing first {limit} of {displayed_count} endpoints"
                        + (
                            f" (filtered from {total_count} total)"
                            if filtered_count < total_count
                            else ""
                        )
                        + ". Use --json for full payload, or --limit to see more."
                    )
                elif filtered_count < total_count:
                    console.print(
                        f"\nShowing {displayed_count} endpoints (filtered from {total_count} total)."
                        + " Use --json for full payload, or adjust filters to see more."
                    )
            else:
                console.print(f"No endpoints found for {model_id}.")
        else:
            print_json(data, pretty=True)
    else:
        print_json(data, pretty=True)


def _extract_zdr_endpoint_rows(endpoints: Iterable[JSONValue]) -> list[_EndpointRow]:
    """Extract ZDR endpoint data into structured rows."""
    rows: list[_EndpointRow] = []
    for endpoint in endpoints:
        if isinstance(endpoint, dict):
            name = str(endpoint.get("name", "-"))
            provider = str(endpoint.get("provider_name", "-"))
            tag = str(endpoint.get("tag", "-"))
            model_name = str(endpoint.get("model_name", "-"))
            context_length = endpoint.get("context_length")
            if isinstance(context_length, int):
                ctx_i: int | None = context_length
            elif isinstance(context_length, str) and context_length.isdigit():
                ctx_i = int(context_length)
            else:
                ctx_i = None

            status_raw = endpoint.get("status")
            status_code, status_display = _format_status(status_raw)

            uptime_raw = endpoint.get("uptime_last_30m")
            uptime_value, _ = _format_uptime(uptime_raw)

            rows.append(
                _EndpointRow(
                    name=name,
                    provider=provider,
                    tag=tag,
                    context_length=ctx_i,
                    status=status_code,
                    status_display=status_display,
                    uptime=uptime_value,
                    model_name=model_name,
                )
            )
    return rows


def _render_zdr_table(rows: list[_EndpointRow]) -> None:
    """Render ZDR endpoint table."""
    table = Table(
        title="ZDR (Zero Data Retention) Endpoints",
        show_lines=False,
        show_header=True,
    )
    table.add_column("Name")
    table.add_column("Model")
    table.add_column("Provider")
    table.add_column("Tag")
    table.add_column("Context Length", justify="right")
    table.add_column("Status")
    table.add_column("Uptime (30m)", justify="right")

    for row in rows:
        uptime_str = f"{row.uptime:.1f}%" if row.uptime is not None else "-"
        table.add_row(
            row.name,
            row.model_name or "-",
            row.provider,
            row.tag,
            str(row.context_length) if row.context_length is not None else "-",
            row.status_display,
            uptime_str,
        )
    console.print(table)


@app.command("zdr")
def endpoints_zdr(
    ctx: typer.Context,
    search: str | None = typer.Option(
        None, "--search", "-s", help="Filter by name/model/provider/tag contains"
    ),
    limit: int = typer.Option(100, "--limit", "-n", min=1, max=500),
    sort: str | None = typer.Option(
        None,
        "--sort",
        metavar="FIELD:ORDER",
        help="Sort by field:order (e.g., 'uptime:desc' or 'status:asc').\n\n- Fields: name, provider, tag, context_length, status, uptime\n\n- Orders: asc (ascending), desc (descending)",
    ),
    filter: list[str] | None = typer.Option(
        None,
        "--filter",
        "-f",
        metavar="FIELD:OPERATOR:VALUE",
        help="Filter by field:operator:value (e.g., 'status:eq:0' or 'uptime:ge:95.0'). Can be used multiple times.\n\n- Operators: ge (≥), le (≤), gt (>), lt (<), eq (=). \n\n- Fields: context_length, status, uptime",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """List ZDR (Zero Data Retention) endpoints."""
    with make_client_from_ctx(ctx) as client:
        data = client.list_endpoints_zdr()
    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable table output
    if isinstance(data, dict) and "data" in data:
        endpoints = data["data"]
        if isinstance(endpoints, list) and len(endpoints) > 0:
            rows = _extract_zdr_endpoint_rows(endpoints)
            total_count = len(rows)

            # Apply search filter
            if search:
                s = search.lower()
                rows = [
                    r
                    for r in rows
                    if s in r.name.lower()
                    or (r.model_name and s in r.model_name.lower())
                    or s in r.provider.lower()
                    or s in r.tag.lower()
                ]

            # Apply filters
            rows = _filter_rows(rows, filters=filter)
            filtered_count = len(rows)

            # Apply sorting
            if sort:
                sort_by, sort_order = _parse_sort_for_endpoints(sort)
                rows = _sort_rows(rows, sort_by=sort_by, order=sort_order)

            # Apply limit
            displayed_count = len(rows)
            rows = rows[:limit]
            _render_zdr_table(rows)

            # Show count message
            if displayed_count > limit:
                console.print(
                    f"\nShowing first {limit} of {displayed_count} endpoints"
                    + (
                        f" (filtered from {total_count} total)"
                        if filtered_count < total_count
                        else ""
                    )
                    + ". Use --json for full payload, or --limit to see more."
                )
            elif filtered_count < total_count:
                console.print(
                    f"\nShowing {displayed_count} endpoints (filtered from {total_count} total)."
                    + " Use --json for full payload, or adjust filters to see more."
                )
        else:
            console.print("No ZDR endpoints found.")
    else:
        print_json(data, pretty=True)
