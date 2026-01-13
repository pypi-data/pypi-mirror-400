"""Configuration loader for SyncLangs."""

from __future__ import annotations

import errno
import json
from pathlib import Path

from pydantic import ValidationError

from synclangs.config.schema import SyncLangsConfig
from synclangs.errors import (
    SY010,
    SY011,
    SY020,
    SY021,
    SyncLangsError,
    SyncLangsFailure,
)

_REQUIRED_FIELDS = ("version", "input", "outputs")


def resolve_config_path(config: Path | None) -> Path:
    """Resolve the config file path."""
    if config is not None:
        return config
    return Path("syln.config.json")


def load_config(config_path: Path) -> SyncLangsConfig:
    """Load and validate the SyncLangs configuration."""
    if not config_path.exists():
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=SY020,
                    message="Config file not found.",
                    file_path=str(config_path),
                )
            ]
        )

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        code = SY021 if exc.errno == errno.EACCES else SY020
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=code,
                    message="Failed to read config file.",
                    file_path=str(config_path),
                )
            ]
        ) from exc

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=SY010,
                    message=f"Invalid JSON: {exc.msg}",
                    file_path=str(config_path),
                    line=exc.lineno,
                    column=exc.colno,
                    line_text=_line_at(text, exc.lineno),
                )
            ]
        ) from exc

    if not isinstance(raw, dict):
        raise SyncLangsFailure(
            [
                SyncLangsError(
                    code=SY010,
                    message="Config root must be a JSON object.",
                    file_path=str(config_path),
                )
            ]
        )

    missing = [field for field in _REQUIRED_FIELDS if field not in raw]
    if missing:
        errors = [
            SyncLangsError(
                code=SY011,
                message=f"Missing required field '{field}'.",
                file_path=str(config_path),
            )
            for field in missing
        ]
        raise SyncLangsFailure(errors)

    try:
        return SyncLangsConfig.model_validate(raw)
    except ValidationError as exc:
        errors = [_convert_error(error, str(config_path)) for error in exc.errors()]
        raise SyncLangsFailure(errors) from exc


def _convert_error(error: dict[str, object], path: str) -> SyncLangsError:
    """Convert a pydantic error into a SyncLangs error."""
    code = SY011 if error.get("type") == "missing" else SY010
    loc = error.get("loc", ())
    location = ".".join(str(item) for item in loc) if loc else "config"
    message = f"{location}: {error.get('msg', 'Invalid value')}"
    return SyncLangsError(code=code, message=message, file_path=path)


def _line_at(text: str, line: int) -> str | None:
    """Return the source line at a 1-based line number."""
    if line <= 0:
        return None
    lines = text.splitlines()
    if line > len(lines):
        return None
    return lines[line - 1]
