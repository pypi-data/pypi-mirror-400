"""Child decorator to load the contents of a CSV file."""

# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

import csv
from pathlib import Path
from typing import Any, Literal

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class LoadCsv(ChildNode):
    """Child decorator to load the contents of a CSV file."""

    def handle_path(
        self, value: Path, context: Context, *args: Any, **kwargs: Any
    ) -> list[dict[str, str]] | list[list[str]]:
        dialect = kwargs["dialect"]
        delimiter = kwargs["delimiter"]
        has_header = kwargs["has_header"]
        as_dict = kwargs["as_dict"]
        encoding = kwargs["encoding"]
        skip_empty = kwargs["skip_empty"]

        if value.is_dir():
            raise IsADirectoryError(
                f"Path '{value.absolute()}' is a directory, but must be a file."
            )

        with value.open("r", encoding=encoding, newline="") as f:
            reader_kwargs: dict[str, Any] = {}
            if dialect:
                reader_kwargs["dialect"] = dialect
            if delimiter:
                reader_kwargs["delimiter"] = delimiter

            if as_dict:
                reader = csv.DictReader(f, **reader_kwargs)
                rows: list[dict[str, str]] = []
                for row_dict in reader:
                    if skip_empty and not any(row_dict.values()):
                        continue
                    rows.append(row_dict)
                return rows

            reader_list = csv.reader(f, **reader_kwargs)
            rows_list: list[list[str]] = []

            if has_header:
                next(reader_list, None)  # Skip header row

            for row_list in reader_list:
                if skip_empty and not any(row_list):
                    continue
                rows_list.append(row_list)
            return rows_list


def load_csv(
    dialect: Literal["excel", "excel-tab", "unix"] | None = None,
    delimiter: str | None = None,
    has_header: bool = True,
    as_dict: bool = True,
    encoding: str = "utf-8",
    skip_empty: bool = True,
) -> Decorator:
    """
    Load the contents of a CSV file.

    Type: `ChildNode`

    Supports: `pathlib.Path`

    Args:
        dialect (Literal["excel", "excel-tab", "unix"] | None, optional):
            CSV dialect to use:
            - `"excel"`: Excel-generated CSV files (comma-delimited)
            - `"excel-tab"`: Excel-generated tab-delimited files
            - `"unix"`: Unix-style CSV files (quote all fields)
            If not specified, the reader will use default settings.
            Defaults to `None`.
        delimiter (str, optional):
            Character used to separate fields. Common values are ',' and '\\t'.
            If not specified, defaults to comma for most dialects.
            Defaults to `None`.
        has_header (bool, optional):
            Whether the CSV file has a header row. Only used when
            `as_dict=False`. When `as_dict=True`, the first row is
            always treated as headers. Defaults to `True`.
        as_dict (bool, optional):
            Whether to return rows as dictionaries (using header as keys)
            or as lists. When `True`, uses `csv.DictReader`. When `False`,
            uses `csv.reader`.
            Defaults to `True`.
        encoding (str, optional):
            The encoding to use when reading the file.
            Defaults to `"utf-8"`.
        skip_empty (bool, optional):
            Whether to skip empty rows in the CSV file.
            Defaults to `True`.

    Returns:
        Decorator:
            The decorated function.
    """
    return LoadCsv.as_decorator(
        dialect=dialect,
        delimiter=delimiter,
        has_header=has_header,
        as_dict=as_dict,
        encoding=encoding,
        skip_empty=skip_empty,
    )
