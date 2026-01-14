"""Centralized logging configuration for dvt."""

import logging
import sys

LOGGER_NAME = "dvt"


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Optional name suffix for child logger.

    Returns:
        Logger instance.
    """
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level to use.
    """
    logger = get_logger()
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def enable_debug_logging() -> None:
    """Enable debug level logging."""
    setup_logging(logging.DEBUG)


def disable_logging() -> None:
    """Disable all logging output."""
    logging.getLogger(LOGGER_NAME).disabled = True
