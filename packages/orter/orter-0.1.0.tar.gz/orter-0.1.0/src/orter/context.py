from dataclasses import dataclass

import typer

from orter.client import OpenRouterClient, load_config


@dataclass(frozen=True, slots=True)
class GlobalOptions:
    api_key: str | None
    base_url: str
    referer: str | None
    title: str | None
    timeout_s: float


def set_global_options(
    ctx: typer.Context,
    *,
    api_key: str | None,
    base_url: str,
    referer: str | None,
    title: str | None,
    timeout_s: float,
) -> None:
    ctx.obj = GlobalOptions(
        api_key=api_key,
        base_url=base_url,
        referer=referer,
        title=title,
        timeout_s=timeout_s,
    )


def get_global_options(ctx: typer.Context) -> GlobalOptions:
    obj = ctx.find_object(GlobalOptions)
    if isinstance(obj, GlobalOptions):
        return obj
    return GlobalOptions(
        api_key=None,
        base_url="https://openrouter.ai",
        referer=None,
        title=None,
        timeout_s=60.0,
    )


def make_client_from_ctx(ctx: typer.Context) -> OpenRouterClient:
    opt = get_global_options(ctx)
    config = load_config(
        api_key=opt.api_key,
        base_url=opt.base_url,
        referer=opt.referer,
        title=opt.title,
        timeout_s=opt.timeout_s,
    )
    return OpenRouterClient(config)
