"""Parent node for generating a random datetime."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import random
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from click_extended.core.nodes.parent_node import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomDateTime(ParentNode):
    """Parent node for generating a random datetime."""

    def _parse_datetime(self, value: str | datetime) -> datetime:
        """Parse a datetime string or return datetime as-is."""
        if isinstance(value, datetime):
            return value

        value_lower = value.lower()

        if value_lower == "now":
            return datetime.now()

        if value_lower == "today":
            return datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        if value_lower == "tomorrow":
            today = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return today + timedelta(days=1, hours=23, minutes=59, seconds=59)

        if value_lower == "yesterday":
            today = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return today - timedelta(days=1)

        formats = [
            "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
            "%Y-%m-%d",  # YYYY-MM-DD
            "%H:%M:%S",  # HH:MM:SS (today's date)
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        raise ValueError(
            f"Unable to parse datetime '{value}'. "
            f"Supported formats: YYYY-MM-DD HH:MM:SS, YYYY-MM-DD, HH:MM:SS, "
            f"or special keywords: 'now', 'today', 'tomorrow'"
        )

    def load(self, context: Context, *args: Any, **kwargs: Any) -> datetime:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        start = self._parse_datetime(kwargs["start_date"])
        end = self._parse_datetime(kwargs["end_date"])

        if start >= end:
            raise ValueError("start_date must be before end_date")

        start_timestamp = start.timestamp()
        end_timestamp = end.timestamp()
        random_timestamp = random.uniform(start_timestamp, end_timestamp)

        result = datetime.fromtimestamp(random_timestamp)

        timezone = kwargs.get("timezone")
        if timezone:
            try:
                tz = ZoneInfo(timezone)
                result = result.replace(tzinfo=tz)
            except Exception as e:
                raise ValueError(f"Invalid timezone '{timezone}' ({e})") from e

        return result


def random_datetime(
    name: str,
    start_date: str | datetime,
    end_date: str | datetime,
    timezone: str | None = None,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random datetime.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parent node.
        start_date (str | datetime):
            The datetime to start at.
            If a string is provided, the following formats are supported:
                - YYYY-MM-DD HH:MM:SS
                - YYYY-MM-DD
                - HH:MM:SS
                - Special keywords: 'now', 'today', 'tomorrow', 'yesterday'
        end_date (str | datetime):
            The datetime to end at.
            If a string is provided, the following formats are supported:
                - YYYY-MM-DD HH:MM:SS
                - YYYY-MM-DD
                - HH:MM:SS
                - Special keywords: 'now', 'today', 'tomorrow', 'yesterday'
        timezone (str | None, optional):
            The timezone to use (e.g., 'UTC', 'US/Eastern', 'Europe/London').
            If None, the datetime will be timezone-naive.
        seed (int | None, optional):
            Optional seed for reproducible randomness.

    Returns:
        Decorator:
            The decorator function.

    Raises:
        ValueError:
            If the timezone is invalid or start_date is after end_date.
    """
    return RandomDateTime.as_decorator(
        name=name,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        seed=seed,
    )
