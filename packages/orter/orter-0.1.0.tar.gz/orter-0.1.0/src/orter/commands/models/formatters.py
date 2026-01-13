"""Formatting utilities for models commands."""

from decimal import Decimal, InvalidOperation

from orter.types import JSONValue


def as_decimal(value: str | int | float | None) -> Decimal | None:
    """Convert value to Decimal if possible.

    Args:
        value: Value to convert

    Returns:
        Decimal if conversion successful, None otherwise
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    # At this point, value is guaranteed to be str (pyright strict)
    if value.strip():
        try:
            return Decimal(value)
        except InvalidOperation:
            return None
    return None


def format_per_million(value: str | int | float | None) -> str:
    """Format price value as per million tokens.

    Args:
        value: Price value to format

    Returns:
        Formatted string like "0.1234/M" or "-" if None
    """
    d = as_decimal(value)
    if d is None:
        return "-"
    per_m = d * Decimal(1_000_000)
    # Keep it concise: use scientific notation for values less than 0.0001
    if per_m != 0 and abs(per_m) < Decimal("0.0001"):
        return f"{per_m:.2E}/M"
    s = f"{per_m:.4f}".rstrip("0").rstrip(".")
    return f"{s}/M"


def format_field_value(
    value: JSONValue, *, indent: int = 0, max_depth: int = 10, show_all: bool = True
) -> str:
    """Format a JSON value for display in table with proper nesting.

    Args:
        value: JSON value to format
        indent: Current indentation level
        max_depth: Maximum nesting depth (only used if show_all=False)
        show_all: If True, show all items/keys without truncation

    Returns:
        Formatted string representation
    """
    indent_str = "  " * indent

    if value is None:
        return "-"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Don't truncate strings in get command - show full value
        return value
    if isinstance(value, list):
        if len(value) == 0:
            return "[]"
        if not show_all and indent >= max_depth:
            return f"[... ({len(value)} items)]"
        # Format list items with indentation - show ALL items if show_all=True
        items: list[str] = []
        items_to_show = value if show_all else value[:5]
        for v in items_to_show:
            item_str = format_field_value(
                v, indent=indent + 1, max_depth=max_depth, show_all=show_all
            )
            items.append(f"{indent_str}  {item_str}")
        if not show_all and len(value) > 5:
            items.append(f"{indent_str}  ... (+{len(value) - 5} more)")
        return "[\n" + "\n".join(items) + f"\n{indent_str}]"
    # Type narrowing: JSONValue can be dict[str, JSONValue]
    # Check at runtime for safety, but type checker knows it's always true for dict
    if isinstance(value, dict):  # type: ignore[unnecessary-isinstance]
        if len(value) == 0:
            return "{}"
        if not show_all and indent >= max_depth:
            keys = list(value.keys())
            return f"{{... ({len(keys)} keys)}}"
        # Format nested objects with indentation - show ALL keys if show_all=True
        lines: list[str] = []
        sorted_keys = sorted(value.keys())
        keys_to_show = sorted_keys if show_all else sorted_keys[:10]
        for key in keys_to_show:
            v = value[key]
            formatted_val = format_field_value(
                v, indent=indent + 1, max_depth=max_depth, show_all=show_all
            )
            lines.append(f"{indent_str}  {key}: {formatted_val}")
        if not show_all and len(sorted_keys) > 10:
            lines.append(f"{indent_str}  ... (+{len(sorted_keys) - 10} more keys)")
        return "{\n" + "\n".join(lines) + f"\n{indent_str}}}"
    return str(value)
