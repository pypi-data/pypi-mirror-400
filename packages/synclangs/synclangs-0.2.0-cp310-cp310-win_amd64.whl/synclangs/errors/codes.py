"""Error code definitions for SyncLangs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorCode:
    """Represents a categorized SyncLangs error code."""

    code: str
    title: str
    category: str


SY001 = ErrorCode("SY001", "Syntax error", "Parser")
SY002 = ErrorCode("SY002", "Invalid type reference", "Parser")
SY003 = ErrorCode("SY003", "Circular import detected", "Parser")
SY004 = ErrorCode("SY004", "Duplicate type definition", "Parser")
SY005 = ErrorCode("SY005", "Duplicate enum variant", "Parser")
SY006 = ErrorCode("SY006", "Name conflict", "Parser")
SY007 = ErrorCode("SY007", "Duplicate constant", "Parser")
SY008 = ErrorCode("SY008", "Invalid constant type", "Parser")
SY010 = ErrorCode("SY010", "Invalid configuration", "Config")
SY011 = ErrorCode("SY011", "Missing required field", "Config")
SY020 = ErrorCode("SY020", "File not found", "IO")
SY021 = ErrorCode("SY021", "Permission denied", "IO")
SY030 = ErrorCode("SY030", "Unsupported feature", "CodeGen")

