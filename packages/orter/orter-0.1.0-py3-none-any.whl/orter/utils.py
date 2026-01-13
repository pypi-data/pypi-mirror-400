import json
import sys
from enum import Enum

import typer
from rich.console import Console

from orter.types import JSONValue


class FilterOperator(str, Enum):
    """Filter operators."""

    GE = "ge"  # >=
    LE = "le"  # <=
    GT = "gt"  # >
    LT = "lt"  # <
    EQ = "eq"  # ==


class SortOrder(str, Enum):
    """Sort order."""

    ASC = "asc"
    DESC = "desc"


console = Console()


def parse_filter(filter_str: str) -> tuple[str, FilterOperator, str]:
    """Parse filter string in format 'field:operator:value'.

    Example: 'context_length:ge:100000'

    Args:
        filter_str: Filter string in format 'field:operator:value'

    Returns:
        Tuple of (field, operator, value)

    Raises:
        typer.BadParameter: If filter format is invalid
    """
    parts = filter_str.split(":", 2)
    if len(parts) != 3:
        raise typer.BadParameter(
            f"Invalid filter format: {filter_str}. Expected format: 'field:operator:value'"
        )
    field, op_str, value = parts
    try:
        operator = FilterOperator(op_str.lower())
    except ValueError:
        raise typer.BadParameter(
            f"Invalid operator: {op_str}. Valid operators: ge, le, gt, lt, eq"
        )
    return (field, operator, value)


def parse_sort(sort_str: str, valid_fields: list[str]) -> tuple[str, SortOrder]:
    """Parse sort string in format 'field:order' or 'field'.

    Example: 'prompt_price:desc' or 'prompt_price' (defaults to asc)

    Args:
        sort_str: Sort string in format 'field:order' or 'field'
        valid_fields: List of valid field names for error messages

    Returns:
        Tuple of (field, order)

    Raises:
        typer.BadParameter: If sort format is invalid
    """
    parts = sort_str.split(":", 1)
    field_str = parts[0]
    order_str = parts[1].lower() if len(parts) > 1 else "asc"

    if field_str.lower() not in [f.lower() for f in valid_fields]:
        raise typer.BadParameter(
            f"Invalid sort field: {field_str}. Valid fields: {', '.join(valid_fields)}"
        )

    try:
        sort_order = SortOrder(order_str.lower())
    except ValueError:
        raise typer.BadParameter(
            f"Invalid sort order: {order_str}. Valid orders: asc, desc"
        )

    return (field_str.lower(), sort_order)


def apply_int_filter(
    row_value: int | None, filter_value: int, operator: FilterOperator
) -> bool:
    """Apply integer filter operator.

    Args:
        row_value: Value from row (can be None)
        filter_value: Filter value to compare against
        operator: Filter operator

    Returns:
        True if row should be included, False otherwise
    """
    if row_value is None:
        return False
    if operator == FilterOperator.GE:
        return row_value >= filter_value
    if operator == FilterOperator.LE:
        return row_value <= filter_value
    if operator == FilterOperator.GT:
        return row_value > filter_value
    if operator == FilterOperator.LT:
        return row_value < filter_value
    if operator == FilterOperator.EQ:
        return row_value == filter_value
    return False


def apply_float_filter(
    row_value: float | None, filter_value: float, operator: FilterOperator
) -> bool:
    """Apply float filter operator.

    Args:
        row_value: Value from row (can be None)
        filter_value: Filter value to compare against
        operator: Filter operator

    Returns:
        True if row should be included, False otherwise
    """
    if row_value is None:
        return False
    if operator == FilterOperator.GE:
        return row_value >= filter_value
    if operator == FilterOperator.LE:
        return row_value <= filter_value
    if operator == FilterOperator.GT:
        return row_value > filter_value
    if operator == FilterOperator.LT:
        return row_value < filter_value
    if operator == FilterOperator.EQ:
        return row_value == filter_value
    return False


def print_json(data: JSONValue, *, pretty: bool = True) -> None:
    # In pipe/redirection environments, Rich output may cause OSError (Errno 22) or broken output on Windows,
    # so output to plain stdout in such cases.
    if not sys.stdout.isatty():
        try:
            sys.stdout.write(
                json.dumps(data, ensure_ascii=True, indent=2 if pretty else None) + "\n"
            )
        except (BrokenPipeError, OSError):
            # Exit quietly if pipe destination is closed (e.g., head)
            return
        return

    # Rich's JSON rendering may break due to Unicode on Windows default codepages (cp949, etc.).
    # Rich can decode JSON escapes back to Unicode for output,
    # so if there's an issue, output the "ASCII-escaped original" to plain stdout.
    if not pretty:
        try:
            console.print(json.dumps(data, ensure_ascii=False))
            return
        except (UnicodeEncodeError, BrokenPipeError, OSError):
            sys.stdout.write(json.dumps(data, ensure_ascii=True) + "\n")
            return

    try:
        console.print_json(json.dumps(data, ensure_ascii=False))
    except (UnicodeEncodeError, BrokenPipeError, OSError):
        sys.stdout.write(json.dumps(data, ensure_ascii=True, indent=2) + "\n")
