import json

import typer

from orter.context import make_client_from_ctx
from orter.types import (
    ChatCompletionResponse,
    JSONObject,
    JSONValue,
    NonStreamingChoice,
    StreamingChoice,
)
from orter.utils import print_json

app = typer.Typer(name="chat", help="Chat Completions API", no_args_is_help=True)


@app.command("completions")
def chat_completions(
    ctx: typer.Context,
    message: str = typer.Option(..., "--message", "-m", help="User message"),
    model: str = typer.Option(
        "openai/gpt-4o-mini", "--model", help="e.g. openai/gpt-4o-mini"
    ),
    system: str | None = typer.Option(None, "--system", help="System message"),
    max_tokens: int | None = typer.Option(None, "--max-tokens"),
    temperature: float | None = typer.Option(None, "--temperature"),
    stream: bool = typer.Option(False, "--stream", help="SSE streaming"),
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """Create a chat completion."""
    messages_json: list[JSONValue] = []
    if system:
        messages_json.append({"role": "system", "content": system})
    messages_json.append({"role": "user", "content": message})

    payload: JSONObject = {"model": model, "messages": messages_json}
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if temperature is not None:
        payload["temperature"] = temperature

    with make_client_from_ctx(ctx) as client:
        if stream:
            for chunk in client.stream_chat_completions(payload=payload):
                if json_output:
                    typer.echo(json.dumps(chunk, ensure_ascii=True))
                    continue
                parsed = ChatCompletionResponse.model_validate(chunk)
                for choice in parsed.choices:
                    if (
                        isinstance(choice, StreamingChoice)
                        and choice.delta
                        and choice.delta.content
                    ):
                        typer.echo(choice.delta.content, nl=False)
            if not json_output:
                typer.echo()
            return

        data = client.chat_completions(payload=payload)
        if json_output:
            print_json(data, pretty=True)
            return
        parsed = ChatCompletionResponse.model_validate(data)
        out: list[str] = []
        for choice in parsed.choices:
            if (
                isinstance(choice, NonStreamingChoice)
                and choice.message
                and choice.message.content
            ):
                out.append(choice.message.content)
        typer.echo("\n\n".join(out))
