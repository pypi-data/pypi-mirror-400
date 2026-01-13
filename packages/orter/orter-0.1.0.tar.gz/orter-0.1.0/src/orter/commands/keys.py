"""API Keys management commands."""

import typer
from rich.table import Table

from orter.context import make_client_from_ctx
from orter.types import JSONObject
from orter.utils import console, print_json

app = typer.Typer(name="keys", help="API Keys API", no_args_is_help=True)


@app.command("list")
def keys_list(
    ctx: typer.Context,
    include_disabled: bool = typer.Option(
        False, "--include-disabled", help="Include disabled keys"
    ),
    offset: int | None = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """List API keys."""
    with make_client_from_ctx(ctx) as client:
        data = client.list_api_keys(
            include_disabled=include_disabled if include_disabled else None,
            offset=offset,
        )
    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable table output
    if isinstance(data, dict) and "data" in data:
        items = data["data"]
        if isinstance(items, list) and len(items) > 0:
            table = Table(title="API Keys", show_lines=False)
            table.add_column("Hash")
            table.add_column("Name")
            table.add_column("Label")
            table.add_column("Disabled")
            table.add_column("Usage ($)", justify="right")
            table.add_column("Limit ($)", justify="right")
            table.add_column("Created At")

            for item in items:
                if isinstance(item, dict):
                    table.add_row(
                        str(item.get("hash", "-"))[:16] + "...",
                        str(item.get("name", "-")),
                        str(item.get("label", "-")),
                        "Yes" if item.get("disabled", False) else "No",
                        f"{item.get('usage', 0):.2f}",
                        (
                            f"{item.get('limit', 0):.2f}"
                            if item.get("limit") is not None
                            else "Unlimited"
                        ),
                        str(item.get("created_at", "-")),
                    )
            console.print(table)
        else:
            console.print("No API keys found.")
    else:
        print_json(data, pretty=True)


@app.command("create")
def keys_create(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", help="Key name"),
    label: str | None = typer.Option(None, "--label", help="Key label"),
    limit: float | None = typer.Option(None, "--limit", help="Spending limit in USD"),
    limit_reset: str | None = typer.Option(
        None, "--limit-reset", help="Limit reset type"
    ),
    include_byok_in_limit: bool = typer.Option(
        False, "--include-byok-in-limit", help="Include BYOK usage in limit"
    ),
    expires_at: str | None = typer.Option(
        None, "--expires-at", help="Expiration date (ISO 8601)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Create API key."""
    payload: JSONObject = {"name": name}
    if label:
        payload["label"] = label
    if limit is not None:
        payload["limit"] = limit
    if limit_reset:
        payload["limit_reset"] = limit_reset
    if include_byok_in_limit:
        payload["include_byok_in_limit"] = include_byok_in_limit
    if expires_at:
        payload["expires_at"] = expires_at

    with make_client_from_ctx(ctx) as client:
        data = client.create_api_key(payload=payload)
    print_json(data, pretty=json_output)


@app.command("get")
def keys_get(
    ctx: typer.Context,
    key_id: str = typer.Argument(..., help="Key ID (hash)"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get API key by ID."""
    with make_client_from_ctx(ctx) as client:
        data = client.get_api_key(key_id=key_id)
    print_json(data, pretty=json_output)


@app.command("update")
def keys_update(
    ctx: typer.Context,
    key_id: str = typer.Argument(..., help="Key ID (hash)"),
    name: str | None = typer.Option(None, "--name", help="Key name"),
    label: str | None = typer.Option(None, "--label", help="Key label"),
    disabled: bool | None = typer.Option(
        None, "--disabled/--enabled", help="Disable/enable key"
    ),
    limit: float | None = typer.Option(None, "--limit", help="Spending limit in USD"),
    limit_reset: str | None = typer.Option(
        None, "--limit-reset", help="Limit reset type"
    ),
    include_byok_in_limit: bool | None = typer.Option(
        None,
        "--include-byok-in-limit/--no-include-byok-in-limit",
        help="Include BYOK usage in limit",
    ),
    expires_at: str | None = typer.Option(
        None, "--expires-at", help="Expiration date (ISO 8601)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Update API key."""
    payload: JSONObject = {}
    if name:
        payload["name"] = name
    if label:
        payload["label"] = label
    if disabled is not None:
        payload["disabled"] = disabled
    if limit is not None:
        payload["limit"] = limit
    if limit_reset:
        payload["limit_reset"] = limit_reset
    if include_byok_in_limit is not None:
        payload["include_byok_in_limit"] = include_byok_in_limit
    if expires_at:
        payload["expires_at"] = expires_at

    with make_client_from_ctx(ctx) as client:
        data = client.update_api_key(key_id=key_id, payload=payload)
    print_json(data, pretty=json_output)


@app.command("delete")
def keys_delete(
    ctx: typer.Context,
    key_id: str = typer.Argument(..., help="Key ID (hash)"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Delete API key."""
    with make_client_from_ctx(ctx) as client:
        data = client.delete_api_key(key_id=key_id)
    print_json(data, pretty=json_output)


@app.command("current")
def keys_current(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get current API key."""
    with make_client_from_ctx(ctx) as client:
        data = client.get_current_api_key()
    print_json(data, pretty=json_output)
