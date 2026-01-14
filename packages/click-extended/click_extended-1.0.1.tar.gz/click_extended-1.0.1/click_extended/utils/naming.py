"""Utilities for validating and parsing naming conventions."""

import re
import sys

import click

from click_extended.utils.humanize import humanize_iterable

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
SCREAMING_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$")
KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

LONG_FLAG_PATTERN = re.compile(r"^--[a-z][a-z0-9-]*$")
SHORT_FLAG_PATTERN = re.compile(r"^-[a-zA-Z]$")


def is_valid_name(name: str) -> bool:
    """
    Check if a name is a valid name, in this case only `snake_case` formats
    are considered valid.

    Args:
        name (str):
            The name to validate.

    Returns:
        bool:
            `True` if the name is valid, `False` otherwise.
    """
    return bool(SNAKE_CASE_PATTERN.match(name))


def is_long_flag(value: str) -> bool:
    """
    Check if a value is a long flag (e.g. --option).

    Args:
        value (str):
            The value to check.

    Returns:
        `True` if the value is a long flag, `False` otherwise.
    """
    return bool(LONG_FLAG_PATTERN.match(value))


def is_short_flag(value: str) -> bool:
    """
    Check if a value is a short flag (e.g. -o).

    Args:
        value (str):
            The value to check.

    Returns:
        `True` if the value is a short flag, `False` otherwise.
    """
    return bool(SHORT_FLAG_PATTERN.match(value))


def validate_name(name: str, context: str = "name") -> None:
    """
    Validate a name follows naming conventions.

    Args:
        name (str):
            The name to validate.
        context (Context):
            Context string for error messages
            (e.g. "option name", "argument name").

    Raises:
        ValueError:
            If the name doesn't follow valid conventions.
    """
    if not is_valid_name(name):

        def _exit_program(message: str, tip: str) -> None:
            click.echo(f"InvalidNameError: {message}", err=True)
            click.echo(f"Tip: {tip}", err=True)
            sys.exit(1)

        # Empty name
        if not name:
            _exit_program(
                "The name cannot be empty.",
                "Provide a valid snake_case name (e.g. name, my_name)",
            )

        # Starts with number
        if re.match(r"^\d", name):
            _exit_program(
                f"The name '{name}' cannot start with a number.",
                f"Try with a letter prefix (e.g. 'var_{name}' or 'opt_{name}')",
            )

        # Starts with underscore
        if name[0] == "_":
            _exit_program(
                f"The name '{name}' cannot start with an underscore.",
                f"Try '{name[1:]}' without the leading underscore",
            )

        # Contains uppercase
        if re.search(r"[A-Z]", name):
            suggested = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
            _exit_program(
                f"The name '{name}' contains uppercase letters.",
                f"Only use lowercase characters such as '{suggested}'",
            )

        # Contains hyphens
        if "-" in name:
            _exit_program(
                f"The name '{name}' contains hyphens.",
                f"Use underscores instead like '{name.replace('-', '_')}'",
            )

        # Contains spaces
        if re.search(r"\s", name):
            suggested_name = re.sub(r"\s+", "_", name).lower()
            _exit_program(
                f"The name '{name}' contains whitespace.",
                f"Use underscores instead like '{suggested_name}'",
            )

        # Contains consecutive underscores
        if re.search(r"__+", name):
            _exit_program(
                f"The name '{name}' contains consecutive underscores.",
                f"Use single underscores like '{re.sub(r'__+', '_', name)}'",
            )

        # Contains invalid characters
        invalid_match = re.search(r"[^a-z0-9_]", name)
        if invalid_match:
            invalid_chars = set(re.findall(r"[^a-z0-9_]", name))
            contains_chars = humanize_iterable(
                invalid_chars,
                wrap="'",
                prefix_singular="an invalid character",
                prefix_plural="invalid characters",
            )
            remove_chars = humanize_iterable(
                invalid_chars,
                wrap="'",
                prefix_singular="the character",
                prefix_plural="the characters",
            )
            _exit_program(
                f"The name '{name}' is invalid and contains {contains_chars}",
                f"Remove {remove_chars}",
            )

        # General fallback
        _exit_program(
            f"The name '{name}' is invalid.",
            "Names must be in snake_case (e.g. name, my_name, my_name1)",
        )


def parse_option_args(*args: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse option decorator arguments intelligently.

    Supports three forms:

    1. **@option("my_option")**: name only
    2. **@option("--my-option")**: long flag (derives name)
    3. **@option("-m", "--my-option")**: short and long flags

    Args:
        *args (str):
            Positional arguments passed to `@option` decorator.

    Returns:
        Tuple of (name, short, long):

        - **name**: The parameter name (`None` if not provided)
        - **short**: The short flag (`None` if not provided)
        - **long**: The long flag (`None` if not provided)

    Raises:
        ValueError:
            If arguments are invalid or ambiguous.
    """

    if len(args) == 0:
        return None, None, None

    if len(args) == 1:
        arg = args[0]

        # @option("--my-option")
        if is_long_flag(arg):
            return None, None, arg

        # @option("-m")
        if is_short_flag(arg):
            raise ValueError(
                f"Short flag '{arg}' provided without long flag or name. "
                f"Use one of:\n"
                f"  @option('{arg}', '--flag')  # with long flag\n"
                f"  @option('name', short='{arg}')  # with name parameter"
            )

        # @option("my_option")
        validate_name(arg, "option name")
        return arg, None, None

    if len(args) == 2:
        first, second = args

        # @option("-m", "--my-option")
        if is_short_flag(first) and is_long_flag(second):
            return None, first, second

        # @option("--my-option", "-m")
        if is_long_flag(first) and is_short_flag(second):
            raise ValueError(
                "Invalid argument order. "
                "Short flag must come before long flag:\n"
                f"  Use: @option('{second}', '{first}')"
            )

        raise ValueError(
            f"Invalid arguments: '{first}', '{second}'. "
            f"Expected one of:\n"
            f"  @option('name')  # name only\n"
            f"  @option('--flag')  # long flag only\n"
            f"  @option('-f', '--flag')  # short and long flags"
        )

    raise ValueError(
        f"Too many positional arguments ({len(args)}). "
        f"Maximum is 2 (short and long flags)."
    )
