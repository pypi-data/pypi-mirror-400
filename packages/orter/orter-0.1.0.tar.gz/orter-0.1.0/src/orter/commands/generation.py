import typer

from orter.types import GenerationResponse
from orter.context import make_client_from_ctx
from orter.utils import print_json

app = typer.Typer(name="generation", help="Generation stats API", no_args_is_help=True)


@app.command("get")
def generation_get(
    ctx: typer.Context,
    generation_id: str = typer.Argument(..., help="e.g. gen-xxxxxxxxxxxxxx"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Get generation stats by id."""
    with make_client_from_ctx(ctx) as client:
        data = client.get_generation(generation_id=generation_id)
    if json_output:
        print_json(data, pretty=True)
        return
    # Output only human-readable summary
    parsed = GenerationResponse.model_validate(data)
    typer.echo(f"id: {parsed.id}")
    typer.echo(f"model: {parsed.model}")
    typer.echo(f"cost: {parsed.cost}")
    typer.echo(
        f"usage: prompt={parsed.usage.prompt_tokens if parsed.usage else None}, "
        f"completion={parsed.usage.completion_tokens if parsed.usage else None}, "
        f"total={parsed.usage.total_tokens if parsed.usage else None}"
    )
