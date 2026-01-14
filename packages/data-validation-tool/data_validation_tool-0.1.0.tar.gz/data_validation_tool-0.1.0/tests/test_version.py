"""Tests for version handling."""

import sys
from unittest.mock import patch


class TestVersion:
    """Tests for version handling."""

    def test_version_is_available(self) -> None:
        """Test version is available when package is installed."""
        from data_validation_tool import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_fallback_on_error(self) -> None:
        """Test version falls back to 0.0.0 when metadata is unavailable."""
        # Remove the module from cache to force reimport
        modules_to_remove = [key for key in sys.modules if key.startswith("data_validation_tool")]
        for mod in modules_to_remove:
            del sys.modules[mod]

        # Mock importlib.metadata.version to raise an exception
        with patch("importlib.metadata.version", side_effect=Exception("Not found")):
            from data_validation_tool import __version__

            assert __version__ == "0.0.0"

        # Cleanup: reimport properly
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]
