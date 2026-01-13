"""Providers API commands."""

from dataclasses import dataclass

import typer
from rich.table import Table

from orter.context import make_client_from_ctx
from orter.types import JSONValue
from orter.utils import console, print_json

app = typer.Typer(name="providers", help="Providers API", no_args_is_help=True)


@dataclass(frozen=True, slots=True)
class _ProviderRow:
    """Provider row data."""

    name: str
    slug: str
    privacy_policy: str
    terms_of_service: str
    status_page: str


def _format_url(url: JSONValue | None) -> str:
    """Format URL for display - show domain only if URL exists."""
    if url is None:
        return "-"
    url_str = str(url)
    if not url_str or url_str == "-":
        return "-"
    # Extract domain from URL for cleaner display
    try:
        # Remove protocol
        if "://" in url_str:
            domain = url_str.split("://", 1)[1]
        else:
            domain = url_str
        # Get domain part (before first /)
        domain = domain.split("/", 1)[0]
        return domain
    except Exception:
        return url_str


def _extract_provider_rows(providers: list[JSONValue]) -> list[_ProviderRow]:
    """Extract provider data into structured rows."""
    rows: list[_ProviderRow] = []
    for provider in providers:
        if isinstance(provider, dict):
            name = str(provider.get("name", "-"))
            slug = str(provider.get("slug", "-"))
            privacy_policy_url = provider.get("privacy_policy_url")
            terms_of_service_url = provider.get("terms_of_service_url")
            status_page_url = provider.get("status_page_url")

            privacy_policy = _format_url(privacy_policy_url)
            terms_of_service = _format_url(terms_of_service_url)
            status_page = _format_url(status_page_url)

            rows.append(
                _ProviderRow(
                    name=name,
                    slug=slug,
                    privacy_policy=privacy_policy,
                    terms_of_service=terms_of_service,
                    status_page=status_page,
                )
            )
    return rows


def _render_table(rows: list[_ProviderRow]) -> None:
    """Render providers table."""
    table = Table(title="OpenRouter Providers", show_lines=False)
    table.add_column("name", overflow="fold")
    table.add_column("slug", overflow="fold")
    table.add_column("privacy policy", overflow="fold")
    table.add_column("terms of service", overflow="fold")
    table.add_column("status page", overflow="fold")

    for row in rows:
        table.add_row(
            row.name,
            row.slug,
            row.privacy_policy,
            row.terms_of_service,
            row.status_page,
        )

    console.print(table)


@app.command("list")
def providers_list(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print raw JSON"),
) -> None:
    """List providers."""
    with make_client_from_ctx(ctx) as client:
        data = client.list_providers()

    if json_output:
        print_json(data, pretty=True)
        return

    # Extract providers from response
    if isinstance(data, dict) and "data" in data:
        providers_data = data["data"]
        if isinstance(providers_data, list):
            rows = _extract_provider_rows(providers_data)
            _render_table(rows)
            console.print(
                f"\nShowing {len(rows)} providers. Use `--json` for full payload."
            )
            return

    # Fallback to JSON if structure is unexpected
    print_json(data, pretty=True)
