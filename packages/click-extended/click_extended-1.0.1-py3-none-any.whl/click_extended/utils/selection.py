"""Interactive selection prompt for runtime use."""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

import sys
import termios
import tty


def selection(
    selections: list[str | tuple[str, str]],
    prompt: str = "Select an option",
    multiple: bool = False,
    default: str | list[str] | None = None,
    min_selections: int = 0,
    max_selections: int | None = None,
    cursor_style: str = ">",
    checkbox_style: tuple[str, str] = ("◯", "◉"),
    show_count: bool = False,
) -> str | list[str]:
    """
    Interactive selection prompt with arrow key navigation.

    Creates an interactive terminal prompt that allows users to select one or
    more options using arrow keys (or j/k vim-style keys). The list wraps around
    (carousel behavior) when scrolling past the first or last item.

    Args:
        selections (list[str | tuple[str, str]]):
            List of options. Each item can be:
            - str: Used as both display text and value
            - tuple[str, str]: (display_text, value)
        prompt (str):
            Text to display above the selection list.
            Defaults to "Select an option".
        multiple (bool):
            If `True`, allows multiple selections with checkboxes.
            If `False`, allows single selection only. Defaults to `False`.
        default (str | list[str] | None):
            Default selection(s). Should be a string for single mode,
            or list of strings for multiple mode. Defaults to `None`.
        min_selections (int):
            Minimum number of selections required (multiple mode only).
            Defaults to 0. User cannot confirm until minimum is met.
        max_selections (int | None):
            Maximum number of selections allowed (multiple mode only).
            Defaults to `None` (unlimited). Prevents selecting more than max.
        cursor_style (str):
            The cursor indicator string. Defaults to ">".
            Examples: ">", "→", "▶", "•"
        checkbox_style (tuple[str, str]):
            Tuple of (unselected, selected) checkbox indicators.
            Defaults to ("◯", "◉").
            Examples: ("☐", "☑"), ("○", "●"), ("[ ]", "[x]")
        show_count (bool):
            Whether to show selection count in the prompt.
            Defaults to `False`. Shows "(X/Y selected)" when enabled.

    Returns:
        str | list[str]:
            Selected value(s). `str` for single mode, `list[str]` for
            multiple mode.

    Raises:
        ValueError:
            If selections list is empty or invalid.
        RuntimeError:
            If not running in a TTY and no default is provided.
        KeyboardInterrupt:
            If user presses Ctrl+C.

    Examples:
        >>> from click_extended.interactive import selection
        >>>
        >>> # Simple single selection
        >>> framework = selection(["React", "Vue", "Angular"])
        >>> print(f"Selected: {framework}")
        >>>
        >>> # Multiple selection with constraints
        >>> features = selection(
        ...     [("TypeScript", "ts"), ("ESLint", "eslint"),
                 ("Prettier", "prettier")],
        ...     prompt="Select features",
        ...     multiple=True,
        ...     min_selections=1,
        ...     max_selections=2,
        ...     default=["eslint"]
        ... )
        >>> print(f"Enabled: {features}")
    """
    if not selections:
        raise ValueError("Selections list cannot be empty")

    normalized: list[tuple[str, str]] = []
    for item in selections:
        if isinstance(item, tuple):
            if len(item) != 2:
                raise ValueError(
                    "Tuple selections must have exactly "
                    f"2 elements, got {len(item)}"
                )
            display, value = item
            normalized.append((str(display), str(value)))
        else:
            normalized.append((str(item), str(item)))

    if multiple:
        if min_selections < 0:
            raise ValueError(
                f"min_selections must be >= 0, got {min_selections}"
            )
        if max_selections is not None:
            if max_selections < 1:
                raise ValueError(
                    f"max_selections must be >= 1, got {max_selections}"
                )
            if max_selections < min_selections:
                raise ValueError(
                    f"max_selections ({max_selections}) must be >= "
                    f"min_selections ({min_selections})"
                )
            if max_selections > len(normalized):
                raise ValueError(
                    f"max_selections ({max_selections}) cannot exceed "
                    f"number of options ({len(normalized)})"
                )

    if not sys.stdin.isatty():
        if default is not None:
            return default
        raise RuntimeError(
            "Interactive selection requires a TTY. "
            "Please provide a default value."
        )

    cursor = 0
    selected: set[int] = set()

    if default is not None:
        value_to_idx = {value: idx for idx, (_, value) in enumerate(normalized)}

        if multiple and isinstance(default, list):
            for val in default:
                if val in value_to_idx:
                    selected.add(value_to_idx[val])
        elif not multiple and isinstance(default, str):
            if default in value_to_idx:
                cursor = value_to_idx[default]
                selected.add(cursor)
        elif multiple and isinstance(default, str):
            if default in value_to_idx:
                selected.add(value_to_idx[default])
        elif not multiple and isinstance(default, list) and len(default) > 0:
            if default[0] in value_to_idx:
                cursor = value_to_idx[default[0]]
                selected.add(cursor)

    num_options = len(normalized)
    num_lines = 0

    try:
        while True:
            if num_lines > 0:
                for _ in range(num_lines):
                    sys.stdout.write("\x1b[1A\x1b[2K")
                sys.stdout.flush()

            lines: list[str] = []
            title = prompt.strip().rstrip(":")

            if multiple:
                count = len(selected)
                if max_selections is not None:
                    title += f" ({count}/{max_selections} selected"
                    if min_selections > 0 and count < min_selections:
                        needed = min_selections - count
                        title += f", need {needed} more"
                    title += ")"
                elif min_selections > 0 and count < min_selections:
                    needed = min_selections - count
                    title += f" ({count} selected, need {needed} more)"
                elif show_count:
                    title += f" ({count} selected)"

            title += ":"
            lines.append(title)

            for idx, (display, _) in enumerate(normalized):
                is_cursor = idx == cursor
                is_selected = idx in selected

                if multiple:
                    checkbox = (
                        checkbox_style[1] if is_selected else checkbox_style[0]
                    )
                    prefix = f"{cursor_style} " if is_cursor else "  "
                    lines.append(f"{prefix}{checkbox} {display}")
                else:
                    prefix = f"{cursor_style} " if is_cursor else "  "
                    lines.append(f"{prefix}{display}")

            output = "\n".join(lines)
            sys.stdout.write(output + "\n")
            sys.stdout.flush()
            num_lines = len(lines)

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)

                if ch == "\x1b":
                    next_chars = sys.stdin.read(2)
                    if next_chars == "[A":
                        key = "up"
                    elif next_chars == "[B":
                        key = "down"
                    else:
                        key = "other"
                elif ch in ("\r", "\n"):
                    key = "enter"
                elif ch == " ":
                    key = "space"
                elif ch == "\x03":  # Ctrl+C
                    key = "ctrl_c"
                elif ch == "k":
                    key = "up"
                elif ch == "j":
                    key = "down"
                else:
                    key = "other"
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            if key == "up":
                cursor = (cursor - 1) % num_options
            elif key == "down":
                cursor = (cursor + 1) % num_options
            elif key == "space" and multiple:
                if cursor in selected:
                    selected.remove(cursor)
                else:
                    if max_selections is None or len(selected) < max_selections:
                        selected.add(cursor)
            elif key == "enter":
                if multiple:
                    if len(selected) < min_selections:
                        continue
                    result = [normalized[idx][1] for idx in sorted(selected)]
                    return result
                return normalized[cursor][1]
            elif key == "ctrl_c":
                raise KeyboardInterrupt("Selection cancelled by user")

    except KeyboardInterrupt:
        if num_lines > 0:
            for _ in range(num_lines):
                sys.stdout.write("\x1b[1A\x1b[2K")
            sys.stdout.write("\x1b[1A")
            sys.stdout.flush()
        raise
