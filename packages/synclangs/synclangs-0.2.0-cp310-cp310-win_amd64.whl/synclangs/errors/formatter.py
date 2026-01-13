"""Formatting utilities for SyncLangs errors."""

from __future__ import annotations

from synclangs.errors.types import SyncLangsError


def format_error(error: SyncLangsError) -> str:
    """Format an error into a user-facing string."""
    lines = [f"Error: {error.code.code} - {error.code.title}"]

    if error.file_path:
        location = error.file_path
        if error.line is not None:
            location = f"{location}:{error.line}"
            if error.column is not None:
                location = f"{location}:{error.column}"
        lines.append(f"  --> {location}")

        if error.line is not None and error.line_text is not None:
            line_text = error.line_text.rstrip("\n")
            lines.append("   |")
            lines.append(f"{error.line} | {line_text}")
            if error.column is not None:
                span = error.span or 1
                caret = "^" * max(span, 1)
                caret_padding = " " * max(error.column - 1, 0)
                caret_line = f"   | {caret_padding}{caret}"
                if error.message:
                    caret_line = f"{caret_line} {error.message}"
                lines.append(caret_line.rstrip())
            elif error.message:
                lines.append(f"   | {error.message}")
            lines.append("   |")

    if error.message and not (
        error.line is not None and error.line_text is not None
    ):
        lines.append(f"  Detail: {error.message}")

    if error.hint:
        lines.append(f"Help: {error.hint}")

    return "\n".join(lines)


def format_errors(errors: list[SyncLangsError]) -> list[str]:
    """Format multiple errors for output."""
    return [format_error(error) for error in errors]
