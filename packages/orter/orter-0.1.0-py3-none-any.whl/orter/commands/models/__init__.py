from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

import typer
from rich.table import Table

from orter.commands.models.filters import (
    filter_model_rows,
    parse_sort,
    sort_model_rows,
)
from orter.commands.models.formatters import (
    as_decimal,
    format_field_value,
    format_per_million,
)
from orter.commands.models.types import ModelInfo, ModelsResponse
from orter.context import make_client_from_ctx
from orter.types import JSONObject, JSONValue
from orter.utils import console, print_json


app = typer.Typer(name="models", help="Models API", no_args_is_help=True)


@dataclass(frozen=True, slots=True)
class _ModelRow:
    model_id: str
    name: str
    context_length: int | None
    prompt_price: str
    completion_price: str
    # Raw values for sorting/filtering
    prompt_price_raw: Decimal | None
    completion_price_raw: Decimal | None


def _extract_rows(models: Iterable[ModelInfo]) -> list[_ModelRow]:
    rows: list[_ModelRow] = []
    for m in models:
        model_id = m.id
        name = m.name or ""
        ctx_i = m.context_length
        prompt_price_raw = (
            as_decimal(m.pricing.prompt) if m.pricing and m.pricing.prompt else None
        )
        completion_price_raw = (
            as_decimal(m.pricing.completion)
            if m.pricing and m.pricing.completion
            else None
        )
        rows.append(
            _ModelRow(
                model_id=model_id,
                name=name,
                context_length=ctx_i,
                prompt_price=format_per_million(
                    m.pricing.prompt if m.pricing else None
                ),
                completion_price=format_per_million(
                    m.pricing.completion if m.pricing else None
                ),
                prompt_price_raw=prompt_price_raw,
                completion_price_raw=completion_price_raw,
            )
        )
    return rows


def _get_field_value(field: str, row: _ModelRow) -> Decimal | int | None:
    """Get field value from model row for filtering."""
    if field == "context_length":
        return row.context_length
    elif field == "prompt_price":
        return row.prompt_price_raw
    elif field == "completion_price":
        return row.completion_price_raw
    return None


def _render_table(rows: list[_ModelRow]) -> None:
    table = Table(title="OpenRouter Models", show_lines=False)
    table.add_column("id", overflow="fold")
    table.add_column("name", overflow="fold")
    table.add_column("ctx", justify="right")
    table.add_column("prompt $/M", justify="right")
    table.add_column("completion $/M", justify="right")
    for r in rows:
        table.add_row(
            r.model_id,
            r.name,
            str(r.context_length) if r.context_length is not None else "-",
            r.prompt_price,
            r.completion_price,
        )
    console.print(table)


@app.command("list")
def models_list(
    ctx: typer.Context,
    user: bool = typer.Option(
        False,
        "--user",
        help="List only user models (uses /api/v1/models/user endpoint)",
    ),
    search: str | None = typer.Option(
        None, "--search", "-s", help="Filter by id/name contains"
    ),
    limit: int = typer.Option(20, "--limit", "-n", min=1, max=500),
    sort: str | None = typer.Option(
        None,
        "--sort",
        metavar="FIELD:ORDER",
        help="Sort by field:order (e.g., 'prompt_price:desc' or 'context_length:asc').\n\n- Fields: id, name, context_length, prompt_price, completion_price\n\n- Orders: asc (ascending), desc (descending)",
    ),
    filter: list[str] | None = typer.Option(
        None,
        "--filter",
        "-f",
        metavar="FIELD:OPERATOR:VALUE",
        help="Filter by field:operator:value (e.g., 'context_length:ge:100000'). Can be used multiple times.\n\n- Operators: ge (≥), le (≤), gt (>), lt (<), eq (=). \n\n- Fields: context_length, prompt_price, completion_price",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """List models."""
    with make_client_from_ctx(ctx) as client:
        if user:
            payload = client.list_models_user()
        else:
            payload = client.list_models()
    if json_output:
        print_json(payload, pretty=True)
        return

    parsed = ModelsResponse.model_validate(payload)
    rows = _extract_rows(parsed.data)
    total_count = len(rows)

    # Apply search filter
    if search:
        s = search.lower()
        rows = [r for r in rows if s in r.model_id.lower() or s in r.name.lower()]

    # Apply filters
    rows = filter_model_rows(rows, filters=filter, get_field_value=_get_field_value)

    filtered_count = len(rows)

    # Apply sorting
    if sort:
        sort_by, sort_order = parse_sort(sort)
        rows = sort_model_rows(rows, sort_by=sort_by, order=sort_order)

    # Apply limit
    displayed_count = len(rows)
    rows = rows[:limit]
    _render_table(rows)

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


@app.command("get")
def models_get(
    ctx: typer.Context,
    model_id: str = typer.Argument(..., help="Model id, e.g. openai/gpt-4o-mini"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Show a single model with all fields."""
    with make_client_from_ctx(ctx) as client:
        payload = client.list_models()

    # Find the model in raw JSON data to get all fields
    raw_model: JSONObject | None = None
    if isinstance(payload, dict) and "data" in payload:
        data = payload["data"]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("id") == model_id:
                    raw_model = item
                    break

    if raw_model is None:
        console.print(f"Not found: {model_id}")
        raise typer.Exit(2)

    if json_output:
        print_json(raw_model, pretty=True)
        return

    # Display all fields in a table
    table = Table(title=f"Model: {model_id}", show_lines=False)
    table.add_column("field", style="cyan")
    table.add_column("value", overflow="fold")

    # Sort fields for consistent display
    sorted_fields = sorted(raw_model.keys())

    for field in sorted_fields:
        value = raw_model[field]

        # Special formatting for pricing fields
        if field == "pricing":
            # Type narrowing: value is JSONValue, check if it's a dict
            if isinstance(value, dict):
                pricing_dict: dict[str, JSONValue] = value
                if "prompt" in pricing_dict or "completion" in pricing_dict:
                    prompt_val = pricing_dict.get("prompt")
                    completion_val = pricing_dict.get("completion")
                    prompt_str = (
                        format_per_million(prompt_val)
                        if prompt_val is not None
                        and isinstance(prompt_val, (str, int, float))
                        else "-"
                    )
                    completion_str = (
                        format_per_million(completion_val)
                        if completion_val is not None
                        and isinstance(completion_val, (str, int, float))
                        else "-"
                    )
                    formatted_value = (
                        f"prompt: {prompt_str}, completion: {completion_str}"
                    )
                else:
                    # If pricing doesn't have prompt/completion, format as nested dict
                    formatted_value = format_field_value(
                        value, indent=0, max_depth=10, show_all=True
                    )
            else:
                formatted_value = format_field_value(
                    value, indent=0, max_depth=10, show_all=True
                )
        else:
            formatted_value = format_field_value(
                value, indent=0, max_depth=10, show_all=True
            )

        table.add_row(field, formatted_value)

    console.print(table)


@app.command("count")
def models_count(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get models count."""
    with make_client_from_ctx(ctx) as client:
        data = client.list_models_count()
    print_json(data, pretty=json_output)
