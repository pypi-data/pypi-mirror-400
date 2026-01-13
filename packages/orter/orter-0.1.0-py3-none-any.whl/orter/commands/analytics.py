"""Analytics API commands."""

import typer
from rich.table import Table

from orter.context import make_client_from_ctx
from orter.utils import console, print_json

app = typer.Typer(name="analytics", help="Analytics API", no_args_is_help=True)


@app.command("activity")
def analytics_activity(
    ctx: typer.Context,
    date: str | None = typer.Option(
        None, "--date", help="Filter by UTC date (YYYY-MM-DD format)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get user activity grouped by endpoint."""
    with make_client_from_ctx(ctx) as client:
        data = client.get_user_activity(date=date)
    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable table output
    if isinstance(data, dict) and "data" in data:
        items = data["data"]
        if isinstance(items, list) and len(items) > 0:
            table = Table(title="User Activity", show_lines=False)
            table.add_column("Date")
            table.add_column("Model")
            table.add_column("Endpoint ID")
            table.add_column("Provider")
            table.add_column("Usage ($)", justify="right")
            table.add_column("Requests", justify="right")
            table.add_column("Prompt Tokens", justify="right")
            table.add_column("Completion Tokens", justify="right")

            for item in items[:50]:  # Limit to 50 rows for readability
                if isinstance(item, dict):
                    table.add_row(
                        str(item.get("date", "-")),
                        str(item.get("model", "-")),
                        str(item.get("endpoint_id", "-")),
                        str(item.get("provider_name", "-")),
                        f"{item.get('usage', 0):.4f}",
                        str(item.get("requests", 0)),
                        str(item.get("prompt_tokens", 0)),
                        str(item.get("completion_tokens", 0)),
                    )
            console.print(table)
            if len(items) > 50:
                console.print(
                    f"\nShowing first 50 of {len(items)} items. Use --json for full data."
                )
        else:
            console.print("No activity data found.")
    else:
        print_json(data, pretty=True)
