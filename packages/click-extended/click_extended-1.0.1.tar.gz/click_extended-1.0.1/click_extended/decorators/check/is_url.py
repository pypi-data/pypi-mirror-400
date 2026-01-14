"""Check if a value is a valid URL."""

from typing import Any
from urllib.parse import urlparse

from click_extended.core.nodes.child_node import ChildNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator
from click_extended.utils.humanize import humanize_iterable


class IsUrl(ChildNode):
    """Check if a value is a valid URL."""

    def handle_str(
        self,
        value: str,
        context: Context,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        schemes = kwargs.get("schemes")
        require_tld = kwargs.get("require_tld", True)

        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                raise ValueError(f"Value '{value}' is not a valid URL.")

            if schemes and result.scheme not in schemes:
                humanized_schemes = humanize_iterable(
                    schemes,
                    wrap="'",
                    prefix_singular="scheme is",
                    prefix_plural="shemes are",
                )
                raise ValueError(
                    f"URL scheme '{result.scheme}' is not allowed. "
                    f"Allowed {humanized_schemes}"
                )

            if require_tld and "." not in result.netloc:
                raise ValueError(f"URL '{value}' does not have a valid TLD.")

        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Value '{value}' is not a valid URL.") from e

        return value


def is_url(
    schemes: list[str] | None = None,
    require_tld: bool = True,
) -> Decorator:
    """
    Check if a value is a valid URL.

    Type: `ChildNode`

    Supports: `str`

    Args:
        schemes (list[str] | None, optional):
            List of allowed URL schemes (e.g., ["http", "https"]).
            Defaults to `None` (all schemes allowed).
        require_tld (bool, optional):
            Whether to require a Top-Level Domain (TLD). Defaults to `True`.

    Returns:
        Decorator:
            The decorated function.
    """
    return IsUrl.as_decorator(schemes=schemes, require_tld=require_tld)
