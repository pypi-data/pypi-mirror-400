"""Child decorator to convert a string to a date."""

from datetime import date, datetime
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils import humanize_iterable
from click_extended.utils.time import normalize_datetime_format


class ToDate(ChildNode):
    """Child decorator to convert a string to a date."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> date:
        formats = kwargs["formats"] or (
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
        )

        for fmt in formats:
            try:
                normalized_fmt = normalize_datetime_format(fmt)
                dt = datetime.strptime(value, normalized_fmt)
                return dt.date()
            except ValueError:
                continue

        fmt_text = (
            "either of the formats" if len(formats) != 1 else "in the format"
        )
        raise ValueError(
            f"Invalid date '{value}', must be in "
            f"{fmt_text} {humanize_iterable(formats, sep='or')}"
        )


def to_date(
    *formats: str,
) -> Decorator:
    """
    Convert a string to a date by trying multiple formats.

    Type: `ChildNode`

    Supports: `str`

    Args:
        *formats (str):
            One or more date format strings to try. Supports both Python
            strptime format (e.g., "%Y-%m-%d", "%d/%m/%Y") and simplified format
            (e.g., "YYYY-MM-DD", "DD/MM/YYYY"). The decorator will attempt each
            format in order until one succeeds. Defaults to `"%Y-%m-%d"`,
            `"%d/%m/%Y"`, and `"%m/%d/%Y"`.

    Returns:
        Decorator:
            The decorated function.

    Example:
        @to_date("YYYY-MM-DD", "DD/MM/YYYY")
        # Or using Python strptime format:
        @to_date("%Y-%m-%d", "%d/%m/%Y")
        def process_date(date_val: date):
            print(date_val)
    """
    return ToDate.as_decorator(formats=formats)
