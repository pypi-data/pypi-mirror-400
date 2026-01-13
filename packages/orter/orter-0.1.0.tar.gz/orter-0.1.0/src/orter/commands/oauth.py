"""OAuth API commands."""

import typer

from orter.context import make_client_from_ctx
from orter.types import JSONObject
from orter.utils import print_json

app = typer.Typer(name="oauth", help="OAuth API", no_args_is_help=True)


@app.command("exchange")
def oauth_exchange(
    ctx: typer.Context,
    code: str = typer.Option(..., "--code", help="Authorization code"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Exchange auth code for API key."""
    payload: JSONObject = {"code": code}
    with make_client_from_ctx(ctx) as client:
        data = client.exchange_auth_code_for_api_key(payload=payload)
    print_json(data, pretty=json_output)


@app.command("create-code")
def oauth_create_code(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Create auth keys code."""
    payload: JSONObject = {}
    with make_client_from_ctx(ctx) as client:
        data = client.create_auth_keys_code(payload=payload)
    print_json(data, pretty=json_output)
