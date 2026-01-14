"""Child decorator to convert a string to a datetime."""

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils import humanize_iterable
from click_extended.utils.time import normalize_datetime_format


class ToDatetime(ChildNode):
    """Child decorator to convert a string to a datetime."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> datetime:
        formats = kwargs["formats"] or (
            "%Y-%m-%d",
            "%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        )
        tz = kwargs.get("tz")

        for fmt in formats:
            try:
                normalized_fmt = normalize_datetime_format(fmt)
                dt = datetime.strptime(value, normalized_fmt)
                if tz:
                    dt = dt.replace(tzinfo=ZoneInfo(tz))
                return dt
            except ValueError:
                continue

        fmt = "either of the formats" if len(formats) != 1 else "in the format"
        raise ValueError(
            f"Invalid datetime '{value}', must be in "
            f"{fmt} {humanize_iterable(formats, sep='or')}"
        )


def to_datetime(
    *formats: str,
    tz: str | None = None,
) -> Decorator:
    """
    Convert a string to a datetime by trying multiple formats.

    Type: `ChildNode`

    Supports: `str`

    Args:
        *formats (str):
            One or more datetime format strings to try. Supports both Python
            strptime format (e.g., "%Y-%m-%d", "%d/%m/%Y") and simplified format
            (e.g., "YYYY-MM-DD", "DD/MM/YYYY"). The decorator will attempt each
            format in order until one succeeds. Defaults to `"%Y-%m-%d"`,
            `"%H:%M:%S"` and `"%Y-%m-%d %H:%M:%S"`,

        tz (str | None, optional):
            Timezone name (e.g., "UTC", "America/New_York", "Europe/Stockholm")
            to apply to the parsed datetime. Uses zoneinfo.ZoneInfo for timezone
            handling. Defaults to `None` (naive datetime).

    Returns:
        Decorator:
            The decorated function.

    Example:
        @to_datetime("YYYY-MM-DD", "DD/MM/YYYY", tz="America/New_York")
        # Or using Python strptime format:
        @to_datetime("%Y-%m-%d", "%d/%m/%Y", tz="America/New_York")
        def process_date(date: datetime):
            print(date)
    """
    return ToDatetime.as_decorator(formats=formats, tz=tz)
