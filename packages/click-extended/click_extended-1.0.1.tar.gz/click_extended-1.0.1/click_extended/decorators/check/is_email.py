"""Check if a value is a valid email address."""

from typing import Any

from email_validator import EmailNotValidError, validate_email

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class IsEmail(ChildNode):
    """Check if a value is a valid email address."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        try:
            validate_email(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError(
                f"Value '{value}' is not a valid email address ({e})."
            ) from e
        return value


def is_email() -> Decorator:
    """
    Check if a value is a valid email address.

    Type: `ChildNode`

    Supports: `str`

    Returns:
        Decorator:
            The decorated function.
    """
    return IsEmail.as_decorator()
