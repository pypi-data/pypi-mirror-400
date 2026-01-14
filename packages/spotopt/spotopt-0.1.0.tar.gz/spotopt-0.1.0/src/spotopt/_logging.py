"""Logging utilities for the spotopt package."""

from __future__ import annotations

import logging
from typing import IO


def configure_logging(
    *,
    level: int = logging.INFO,
    stream: IO[str] | None = None,
    fmt: str | None = None,
    datefmt: str | None = None,
    propagate: bool = False,
) -> None:
    """Configure logging for the ``spotopt`` package.

    Args:
        level: Logging level for the ``spotopt`` logger.
        stream: Optional stream for log output. Defaults to
            ``sys.stderr``.
        fmt: Optional logging format.
        datefmt: Optional datetime format string for log records.
        propagate: Whether the ``spotopt`` logger should propagate to
            ancestor loggers. Defaults to ``False`` so that handlers
            added here control the output.
    """
    logger = logging.getLogger("spotopt")

    # Drop any existing non-null handlers to avoid duplicate output when
    # this helper is called multiple times.
    logger.handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.NullHandler)
    ]

    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt or "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=datefmt,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = propagate
