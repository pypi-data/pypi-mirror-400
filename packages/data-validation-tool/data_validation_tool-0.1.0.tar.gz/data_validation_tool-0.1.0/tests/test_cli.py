"""Tests for the main CLI entry point."""

from click.testing import CliRunner

from data_validation_tool import __version__
from data_validation_tool.cli.main import main


class TestMainCli:
    """Tests for the main CLI group."""

    def test_version_option(self, cli_runner: CliRunner) -> None:
        """Test --version flag displays version."""
        result = cli_runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help_option(self, cli_runner: CliRunner) -> None:
        """Test --help flag displays help text."""
        result = cli_runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Data Validation Tool" in result.output
        assert "init" in result.output
        assert "run" in result.output
        assert "cloud" in result.output

    def test_debug_flag(self, cli_runner: CliRunner) -> None:
        """Test --debug flag is accepted."""
        result = cli_runner.invoke(main, ["--debug", "--help"])
        assert result.exit_code == 0

    def test_main_invoked_directly(self, cli_runner: CliRunner) -> None:
        """Test main can be invoked without subcommand."""
        result = cli_runner.invoke(main, [])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_debug_mode_runs_subcommand(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test --debug flag with a subcommand."""
        result = cli_runner.invoke(
            main,
            ["--debug", "init", "--models-dir", str(tmp_models_dir)],
        )
        assert result.exit_code == 0
