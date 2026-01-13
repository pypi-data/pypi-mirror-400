"""Completions API commands."""

import json

import typer

from orter.context import make_client_from_ctx
from orter.types import JSONObject
from orter.utils import print_json

app = typer.Typer(name="completions", help="Completions API", no_args_is_help=True)


@app.command("create")
def completions_create(
    ctx: typer.Context,
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt text"),
    model: str = typer.Option("openai/gpt-4o-mini", "--model", help="Model name"),
    max_tokens: int | None = typer.Option(None, "--max-tokens", help="Max tokens"),
    temperature: float | None = typer.Option(None, "--temperature", help="Temperature"),
    stream: bool = typer.Option(False, "--stream", help="SSE streaming"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Create a completion."""
    payload: JSONObject = {"prompt": prompt, "model": model}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature

    with make_client_from_ctx(ctx) as client:
        if stream:
            for chunk in client.stream_completions(payload=payload):
                if json_output:
                    typer.echo(json.dumps(chunk, ensure_ascii=True))
                    continue
                # Extract text from completion chunk
                if "choices" in chunk:
                    choices = chunk["choices"]
                    if isinstance(choices, list) and len(choices) > 0:
                        choice = choices[0]
                        if isinstance(choice, dict) and "text" in choice:
                            text_val = choice["text"]
                            if isinstance(text_val, str):
                                typer.echo(text_val, nl=False)
            if not json_output:
                typer.echo()
            return

        data = client.create_completions(payload=payload)
        if json_output:
            print_json(data, pretty=True)
            return

        # Human-readable output
        if isinstance(data, dict) and "choices" in data:
            choices = data["choices"]
            if isinstance(choices, list):
                texts: list[str] = []
                for choice in choices:
                    if isinstance(choice, dict) and "text" in choice:
                        text_val = choice["text"]
                        if isinstance(text_val, str):
                            texts.append(text_val)
                typer.echo("\n\n".join(texts))
        else:
            print_json(data, pretty=True)
