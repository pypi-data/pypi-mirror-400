"""Child decorator to convert a string to a time."""

from datetime import datetime, time
from typing import Any

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils import humanize_iterable
from click_extended.utils.time import normalize_datetime_format


class ToTime(ChildNode):
    """Child decorator to convert a string to a time."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> time:
        formats = kwargs["formats"] or (
            "%H:%M:%S",
            "%H:%M",
            "%I:%M:%S %p",
            "%I:%M %p",
        )

        for fmt in formats:
            try:
                normalized_fmt = normalize_datetime_format(fmt)

                dt = datetime.strptime(value, normalized_fmt)
                return dt.time()
            except ValueError:
                continue

        fmt_text = (
            "either of the formats" if len(formats) != 1 else "in the format"
        )
        raise ValueError(
            f"Invalid time '{value}', must be in "
            f"{fmt_text} {humanize_iterable(formats, sep='or')}"
        )


def to_time(
    *formats: str,
) -> Decorator:
    """
    Convert a string to a time by trying multiple formats.

    Type: `ChildNode`

    Supports: `str`

    Args:
        *formats (str):
            One or more time format strings to try. Supports both Python
            strptime format (e.g., "%H:%M:%S", "%I:%M %p") and simplified format
            (e.g., "HH:mm:SS", "HH:mm"). The decorator will attempt each
            format in order until one succeeds. Defaults to `"%H:%M:%S"`,
            `"%H:%M"`, `"%I:%M:%S %p"`, and `"%I:%M %p"`.

    Returns:
        Decorator:
            The decorated function.

    Example:
        @to_time("HH:mm:SS", "HH:mm")
        # Or using Python strptime format:
        @to_time("%H:%M:%S", "%H:%M")
        def process_time(time_val: time):
            print(time_val)
    """
    return ToTime.as_decorator(formats=formats)
