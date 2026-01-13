"""Parameters API commands."""

import typer
from rich.table import Table

from orter.context import make_client_from_ctx
from orter.utils import console, print_json

app = typer.Typer(name="parameters", help="Parameters API", no_args_is_help=True)


@app.command("get")
def parameters_get(
    ctx: typer.Context,
    author: str = typer.Argument(..., help="Model author (e.g., 'openai')"),
    slug: str = typer.Argument(..., help="Model slug (e.g., 'gpt-4o')"),
    provider: str | None = typer.Option(None, "--provider", help="Provider name (optional)"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get parameters for a specific model."""
    with make_client_from_ctx(ctx) as client:
        data = client.get_parameters(author=author, slug=slug, provider=provider)
    if json_output:
        print_json(data, pretty=True)
        return

    # Human-readable table output
    if isinstance(data, dict) and "data" in data:
        params_data = data["data"]
        if isinstance(params_data, dict):
            model = params_data.get("model", f"{author}/{slug}")
            supported_params = params_data.get("supported_parameters", [])
            if isinstance(supported_params, list):
                table = Table(
                    title=f"Supported Parameters for {model}",
                    show_lines=False,
                    show_header=True,
                )
                table.add_column("Parameter", style="cyan")

                if len(supported_params) > 0:
                    for param in supported_params:
                        if isinstance(param, str):
                            table.add_row(param)
                    console.print(table)
                else:
                    console.print(f"No supported parameters found for {model}.")
            else:
                print_json(data, pretty=True)
        else:
            print_json(data, pretty=True)
    else:
        print_json(data, pretty=True)
