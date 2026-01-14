"""Tests for custom exceptions."""

import pytest

from data_validation_tool.core.exceptions import (
    ConfigurationError,
    DvtError,
    ModelNotFoundError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    def test_dvt_error_is_exception(self) -> None:
        """Test DvtError inherits from Exception."""
        assert issubclass(DvtError, Exception)

    def test_configuration_error_is_dvt_error(self) -> None:
        """Test ConfigurationError inherits from DvtError."""
        assert issubclass(ConfigurationError, DvtError)

    def test_model_not_found_error_is_dvt_error(self) -> None:
        """Test ModelNotFoundError inherits from DvtError."""
        assert issubclass(ModelNotFoundError, DvtError)

    def test_validation_error_is_dvt_error(self) -> None:
        """Test ValidationError inherits from DvtError."""
        assert issubclass(ValidationError, DvtError)


class TestExceptionUsage:
    """Tests for raising and catching exceptions."""

    def test_can_raise_and_catch_dvt_error(self) -> None:
        """Test DvtError can be raised and caught."""
        with pytest.raises(DvtError, match="test message"):
            raise DvtError("test message")

    def test_can_catch_subclass_as_dvt_error(self) -> None:
        """Test subclass exceptions can be caught as DvtError."""
        with pytest.raises(DvtError):
            raise ConfigurationError("config issue")

    def test_configuration_error_message(self) -> None:
        """Test ConfigurationError preserves message."""
        error = ConfigurationError("Missing env var")
        assert str(error) == "Missing env var"

    def test_model_not_found_error_message(self) -> None:
        """Test ModelNotFoundError preserves message."""
        error = ModelNotFoundError("Model xyz not found")
        assert str(error) == "Model xyz not found"

    def test_validation_error_message(self) -> None:
        """Test ValidationError preserves message."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
