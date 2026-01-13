import sys
from typing import Annotated

import typer

from orter.commands.analytics import app as analytics_app
from orter.commands.chat import app as chat_app
from orter.commands.completions import app as completions_app
from orter.commands.credits import app as credits_app
from orter.commands.embeddings import app as embeddings_app
from orter.commands.endpoints import app as endpoints_app
from orter.commands.generation import app as generation_app
from orter.commands.keys import app as keys_app
from orter.commands.models import app as models_app
from orter.commands.oauth import app as oauth_app
from orter.commands.parameters import app as parameters_app
from orter.commands.providers import app as providers_app
from orter.commands.raw import app as raw_app
from orter.context import set_global_options

app = typer.Typer(
    name="orter",
    help="OpenRouter API CLI",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def root(
    ctx: typer.Context,
    api_key: Annotated[
        str | None, typer.Option(help="Override OPENROUTER_API_KEY")
    ] = None,
    base_url: Annotated[
        str, typer.Option(help="Base URL (default: https://openrouter.ai)")
    ] = "https://openrouter.ai",
    referer: Annotated[
        str | None, typer.Option(help="HTTP-Referer header (optional)")
    ] = None,
    title: Annotated[str | None, typer.Option(help="X-Title header (optional)")] = None,
    timeout_s: Annotated[float, typer.Option(help="Timeout seconds")] = 60.0,
) -> None:
    set_global_options(
        ctx,
        api_key=api_key,
        base_url=base_url,
        referer=referer,
        title=title,
        timeout_s=timeout_s,
    )


app.add_typer(models_app, name="models")
app.add_typer(chat_app, name="chat")
app.add_typer(generation_app, name="generation")
app.add_typer(raw_app, name="raw")
app.add_typer(analytics_app, name="analytics")
app.add_typer(credits_app, name="credits")
app.add_typer(embeddings_app, name="embeddings")
app.add_typer(endpoints_app, name="endpoints")
app.add_typer(parameters_app, name="parameters")
app.add_typer(providers_app, name="providers")
app.add_typer(keys_app, name="keys")
app.add_typer(oauth_app, name="oauth")
app.add_typer(completions_app, name="completions")


def main() -> None:
    try:
        app()
    except BrokenPipeError:
        # Exit quietly if pipe destination closes first (e.g., head)
        sys.exit(0)
