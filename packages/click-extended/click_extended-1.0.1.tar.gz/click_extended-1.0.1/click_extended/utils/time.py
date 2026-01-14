"""Time, date, and datetime utilities."""


def normalize_datetime_format(fmt: str) -> str:
    """
    Convert simplified format strings to Python strptime format.

    Supports both Python strptime format (e.g., %Y-%m-%d, %H:%M:%S)
    and simplified format (e.g., YYYY-MM-DD, HH:mm:SS).

    Args:
        fmt (str):
            A format string in either Python strptime format or
            simplified format.

    Returns:
        str:
            The normalized Python strptime format string.

    Example:
        ```python
        >>> normalize_datetime_format("YYYY-MM-DD HH:mm:SS")
        '%Y-%m-%d %H:%M:%S'
        >>> normalize_datetime_format("%Y-%m-%d")
        '%Y-%m-%d'
        ```
    """
    if "%" in fmt:
        return fmt

    replacements = {
        "YYYY": "%Y",
        "YY": "%y",
        "MM": "%m",
        "DD": "%d",
        "HH": "%H",
        "mm": "%M",
        "SS": "%S",
        "ss": "%S",
    }

    result = fmt
    for simple, strp in replacements.items():
        result = result.replace(simple, strp)

    return result
