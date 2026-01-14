"""Tests for logging utilities."""

import logging

from data_validation_tool.core.logger import (
    LOGGER_NAME,
    disable_logging,
    enable_debug_logging,
    get_logger,
    setup_logging,
)


class TestGetLogger:
    """Tests for the get_logger function."""

    def test_get_root_logger(self) -> None:
        """Test get_logger returns root logger without name."""
        logger = get_logger()
        assert logger.name == LOGGER_NAME

    def test_get_child_logger(self) -> None:
        """Test get_logger returns child logger with name."""
        logger = get_logger("submodule")
        assert logger.name == f"{LOGGER_NAME}.submodule"


class TestSetupLogging:
    """Tests for logging setup functions."""

    def test_setup_logging_default_level(self) -> None:
        """Test setup_logging configures INFO level by default."""
        setup_logging()
        logger = get_logger()
        assert logger.level == logging.INFO

    def test_setup_logging_custom_level(self) -> None:
        """Test setup_logging accepts custom level."""
        setup_logging(level=logging.WARNING)
        logger = get_logger()
        assert logger.level == logging.WARNING

    def test_enable_debug_logging(self) -> None:
        """Test enable_debug_logging sets DEBUG level."""
        enable_debug_logging()
        logger = get_logger()
        assert logger.level == logging.DEBUG

    def test_disable_logging(self) -> None:
        """Test disable_logging disables the logger."""
        disable_logging()
        logger = logging.getLogger(LOGGER_NAME)
        assert logger.disabled is True
        # Re-enable for other tests
        logger.disabled = False
