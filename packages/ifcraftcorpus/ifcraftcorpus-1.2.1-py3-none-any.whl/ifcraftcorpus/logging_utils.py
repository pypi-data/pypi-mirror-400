"""Shared logging helpers for the IF Craft Corpus codebase."""

from __future__ import annotations

import logging
import os
import sys
from typing import Final

LOG_LEVEL_ENV: Final[str] = "LOG_LEVEL"
VERBOSE_ENV: Final[str] = "VERBOSE"

__all__ = ["configure_logging", "LOG_LEVEL_ENV", "VERBOSE_ENV"]

_TRUTHY_VALUES: Final[set[str]] = {"1", "true", "yes", "on"}
_configured: bool = False
_CHATTY_LOGGERS: Final[tuple[str, ...]] = (
    "httpx",
    "fakeredis",
    "docket",
)


def _is_truthy(value: str | None) -> bool:
    """Return True if the string resembles a truthy flag."""

    if value is None:
        return False
    return value.strip().lower() in _TRUTHY_VALUES


def _resolve_level(value: str | None) -> int | None:
    """Convert a logging level string (name or integer) to ``int``."""

    if not value:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    if candidate.isdigit():
        return int(candidate)
    name = candidate.upper()
    return getattr(logging, name, None)


def configure_logging(
    *,
    env_level: str = LOG_LEVEL_ENV,
    env_verbose: str = VERBOSE_ENV,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
) -> int | None:
    """Configure root logging when LOG_LEVEL/VERBOSE are set.

    Returns the configured level when logging is enabled, ``None`` otherwise.
    """

    global _configured

    raw_level = os.getenv(env_level)
    level = _resolve_level(raw_level)
    verbose_flag = os.getenv(env_verbose)

    if raw_level and level is None:
        print(
            f"ifcraftcorpus: unknown log level '{raw_level}', defaulting to INFO",
            file=sys.stderr,
        )
        level = logging.INFO

    if level is None and not _is_truthy(verbose_flag):
        return None

    if level is None:
        level = logging.DEBUG

    root = logging.getLogger()
    if not (root.handlers and _configured):
        logging.basicConfig(level=level, format=fmt, stream=sys.stderr)
        _configured = True
    root.setLevel(level)

    for name in _CHATTY_LOGGERS:
        logging.getLogger(name).setLevel(max(logging.WARNING, level))
    return level
