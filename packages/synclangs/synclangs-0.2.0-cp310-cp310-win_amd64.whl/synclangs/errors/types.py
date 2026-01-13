"""Error types for SyncLangs."""

from __future__ import annotations

from dataclasses import dataclass

from synclangs.errors.codes import ErrorCode


@dataclass(frozen=True)
class SyncLangsError:
    """A structured error with optional source context."""

    code: ErrorCode
    message: str
    file_path: str | None = None
    line: int | None = None
    column: int | None = None
    line_text: str | None = None
    span: int | None = None
    hint: str | None = None


class SyncLangsFailure(Exception):
    """Exception raised for one or more SyncLangs errors."""

    def __init__(self, errors: list[SyncLangsError]) -> None:
        super().__init__("SyncLangs error")
        self.errors = errors

