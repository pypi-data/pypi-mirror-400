"""Error handling utilities for SyncLangs."""

from synclangs.errors.codes import (
    ErrorCode,
    SY001,
    SY002,
    SY003,
    SY004,
    SY005,
    SY006,
    SY007,
    SY008,
    SY010,
    SY011,
    SY020,
    SY021,
    SY030,
)
from synclangs.errors.formatter import format_error, format_errors
from synclangs.errors.types import SyncLangsError, SyncLangsFailure

__all__ = [
    "ErrorCode",
    "SyncLangsError",
    "SyncLangsFailure",
    "format_error",
    "format_errors",
    "SY001",
    "SY002",
    "SY003",
    "SY004",
    "SY005",
    "SY006",
    "SY007",
    "SY008",
    "SY010",
    "SY011",
    "SY020",
    "SY021",
    "SY030",
]

