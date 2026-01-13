import json
from typing import Literal

import typer

from orter.context import make_client_from_ctx
from orter.types import JSONObject, JSONTypeError, ensure_json_object
from orter.utils import print_json

app = typer.Typer(name="raw", help="Call any OpenRouter endpoint", no_args_is_help=True)


def _normalize_path(path: str) -> str:
    # Git Bash/MSYS may convert arguments like "/api/..." to Windows paths (e.g., C:/Program Files/Git/api/...)
    # In such cases, extract and restore the part after "/api/".
    idx = path.find("/api/")
    if idx != -1:
        path = path[idx:]
    if not path.startswith("/"):
        path = "/" + path
    return path


@app.command("request")
def raw_request(
    ctx: typer.Context,
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = typer.Argument(...),
    path: str = typer.Argument(..., help="e.g. /api/v1/chat/completions"),
    params: str | None = typer.Option(None, "--params", help="JSON object string"),
    body: str | None = typer.Option(None, "--body", help="JSON object string"),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty"),
) -> None:
    """Raw request (JSON in/out)."""
    try:
        params_raw: object | None = json.loads(params) if params else None
        body_raw: object | None = json.loads(body) if body else None
    except json.JSONDecodeError as e:
        typer.echo(f"JSON parse error: {e}", err=True)
        raise typer.Exit(2) from e

    params_obj: dict[str, str] | None = None
    if params_raw is not None:
        try:
            obj = ensure_json_object(params_raw)
        except JSONTypeError as e:
            typer.echo(f"--params must be a JSON object: {e}", err=True)
            raise typer.Exit(2) from e
        # Send query params only as strings (users must encode complex types themselves)
        params_obj = {
            k: json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
            for k, v in obj.items()
        }

    body_obj: JSONObject | None = None
    if body_raw is not None:
        try:
            body_obj = ensure_json_object(body_raw)
        except JSONTypeError as e:
            typer.echo(f"--body must be a JSON object: {e}", err=True)
            raise typer.Exit(2) from e

    with make_client_from_ctx(ctx) as client:
        data = client.request_json(
            method,
            _normalize_path(path),
            params=params_obj,
            body=body_obj,
        )
    print_json(data, pretty=pretty)
