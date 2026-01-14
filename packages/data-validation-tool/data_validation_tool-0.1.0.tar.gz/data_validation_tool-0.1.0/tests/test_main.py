"""Tests for __main__ module entry point."""

import subprocess
import sys


class TestMainModule:
    """Tests for running as a module."""

    def test_run_as_module(self) -> None:
        """Test running data_validation_tool as a module."""
        result = subprocess.run(
            [sys.executable, "-m", "data_validation_tool", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Data Validation Tool" in result.stdout

    def test_run_as_module_version(self) -> None:
        """Test --version flag when running as a module."""
        result = subprocess.run(
            [sys.executable, "-m", "data_validation_tool", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "dvt" in result.stdout
