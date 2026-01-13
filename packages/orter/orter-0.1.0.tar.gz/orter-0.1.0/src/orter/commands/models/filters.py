"""Filter and sort utilities for models commands."""

from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any

import typer

from orter.utils import (
    FilterOperator,
    SortOrder,
    apply_float_filter,
    apply_int_filter,
    parse_filter,
)


class SortField(str, Enum):
    """Sortable fields."""

    ID = "id"
    NAME = "name"
    CONTEXT_LENGTH = "context_length"
    PROMPT_PRICE = "prompt_price"
    COMPLETION_PRICE = "completion_price"


def parse_sort(sort_str: str) -> tuple[SortField, SortOrder]:
    """Parse sort string in format 'field:order' or 'field'.

    Example: 'prompt_price:desc' or 'prompt_price' (defaults to asc)

    Args:
        sort_str: Sort string in format 'field:order' or 'field'

    Returns:
        Tuple of (sort_field, sort_order)

    Raises:
        typer.BadParameter: If sort format is invalid
    """
    from orter.utils import parse_sort as parse_sort_generic

    valid_fields = [field.value for field in SortField]
    field, order = parse_sort_generic(sort_str, valid_fields)
    try:
        sort_field = SortField(field)
    except ValueError:
        raise typer.BadParameter(
            f"Invalid sort field: {field}. Valid fields: {', '.join(valid_fields)}"
        )
    try:
        sort_order = SortOrder(order)
    except ValueError:
        raise typer.BadParameter(
            f"Invalid sort order: {order}. Valid orders: asc, desc"
        )
    return (sort_field, sort_order)


def apply_model_filter(
    rows: list[Any],
    field: str,
    operator: FilterOperator,
    value: str,
    get_field_value: Callable[[str, Any], Any],
) -> list[Any]:
    """Apply a single filter to model rows.

    Args:
        rows: Rows to filter
        field: Field name to filter on
        operator: Filter operator
        value: Filter value
        get_field_value: Function to get field value from row (field_name, row) -> value

    Returns:
        Filtered rows

    Raises:
        typer.BadParameter: If field or value is invalid
    """
    filtered: list[Any] = []

    for row in rows:
        if field == "context_length":
            try:
                filter_value = int(value)
            except ValueError:
                raise typer.BadParameter(f"Invalid context_length value: {value}")
            row_value = get_field_value(field, row)
            if isinstance(row_value, int):
                if apply_int_filter(row_value, filter_value, operator):
                    filtered.append(row)

        elif field in ("prompt_price", "completion_price"):
            try:
                filter_value = Decimal(str(value))
            except (ValueError, InvalidOperation):
                raise typer.BadParameter(f"Invalid {field} value: {value}")
            row_value = get_field_value(field, row)
            if row_value is not None:
                if isinstance(row_value, Decimal):
                    if apply_float_filter(
                        float(row_value), float(filter_value), operator
                    ):
                        filtered.append(row)

        else:
            raise typer.BadParameter(
                f"Invalid field: {field}. Valid fields: context_length, prompt_price, completion_price"
            )

    return filtered


def filter_model_rows(
    rows: list[Any],
    *,
    filters: list[str] | None = None,
    get_field_value: Callable[[str, Any], Any],
) -> list[Any]:
    """Filter rows based on criteria.

    Args:
        rows: Rows to filter
        filters: List of filter strings in format 'field:operator:value'
        get_field_value: Function to get field value from row (field_name, row) -> value

    Returns:
        Filtered rows
    """
    if not filters:
        return rows

    filtered = rows
    for filter_str in filters:
        field, operator, value = parse_filter(filter_str)
        filtered = apply_model_filter(filtered, field, operator, value, get_field_value)

    return filtered


def get_model_sort_key_func(
    sort_by: SortField,
) -> Callable[[Any], tuple[Any, ...]]:
    """Get sort key function for model rows.

    Args:
        sort_by: Field to sort by

    Returns:
        Function that takes a row and returns a sort key tuple
    """
    from decimal import Decimal

    def sort_key(row: Any) -> tuple[Any, ...]:
        if sort_by == SortField.ID:
            return (row.model_id.lower(),)
        elif sort_by == SortField.NAME:
            return (row.name.lower() if row.name else "",)
        elif sort_by == SortField.CONTEXT_LENGTH:
            return (row.context_length if row.context_length is not None else -1,)
        elif sort_by == SortField.PROMPT_PRICE:
            return (
                row.prompt_price_raw
                if row.prompt_price_raw is not None
                else Decimal(-1),
            )
        elif sort_by == SortField.COMPLETION_PRICE:
            return (
                row.completion_price_raw
                if row.completion_price_raw is not None
                else Decimal(-1),
            )
        else:
            return (row.model_id.lower(),)

    return sort_key


def sort_model_rows(
    rows: list[Any],
    *,
    sort_by: SortField | None = None,
    order: SortOrder | None = None,
) -> list[Any]:
    """Sort rows by field.

    Args:
        rows: Rows to sort
        sort_by: Field to sort by
        order: Sort order

    Returns:
        Sorted rows
    """
    if sort_by is None:
        return rows

    reverse = (order or SortOrder.ASC) == SortOrder.DESC
    get_key = get_model_sort_key_func(sort_by)
    return sorted(rows, key=get_key, reverse=reverse)
