"""Credits API commands."""

import typer
from rich.table import Table

from orter.context import make_client_from_ctx
from orter.types import JSONObject
from orter.utils import console, print_json

app = typer.Typer(name="credits", help="Credits API", no_args_is_help=True)


@app.command("get")
def credits_get(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get remaining credits."""
    with make_client_from_ctx(ctx) as client:
        data = client.get_credits()
    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable output
    if isinstance(data, dict) and "data" in data:
        credits_data = data["data"]
        if isinstance(credits_data, dict):
            table = Table(title="Credits", show_lines=False)
            table.add_column("Field")
            table.add_column("Value", justify="right")
            table.add_row(
                "Total Credits",
                f"${credits_data.get('total_credits', 0):.2f}",
            )
            table.add_row(
                "Total Usage",
                f"${credits_data.get('total_usage', 0):.2f}",
            )
            total_credits = credits_data.get("total_credits", 0)
            total_usage = credits_data.get("total_usage", 0)
            if isinstance(total_credits, (int, float)) and isinstance(
                total_usage, (int, float)
            ):
                remaining = total_credits - total_usage
                table.add_row("Remaining", f"${remaining:.2f}")
            else:
                table.add_row("Remaining", "-")
            console.print(table)
        else:
            print_json(data, pretty=True)
    else:
        print_json(data, pretty=True)


@app.command("coinbase")
def credits_coinbase(
    ctx: typer.Context,
    amount: float = typer.Option(..., "--amount", help="Charge amount in USD"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Create Coinbase charge."""
    payload: JSONObject = {"amount": amount}
    with make_client_from_ctx(ctx) as client:
        data = client.create_coinbase_charge(payload=payload)
    print_json(data, pretty=json_output)
