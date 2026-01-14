"""Tests for the init command."""

from click.testing import CliRunner

from data_validation_tool.cli.main import main


class TestInitCommand:
    """Tests for the init command."""

    def test_init_help(self, cli_runner: CliRunner) -> None:
        """Test init --help displays help text."""
        result = cli_runner.invoke(main, ["init", "--help"])
        assert result.exit_code == 0
        assert "Generate validation macros" in result.output
        assert "--models-dir" in result.output
        assert "--model" in result.output
        assert "--output-dir" in result.output

    def test_init_with_valid_dir(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test init with a valid models directory."""
        result = cli_runner.invoke(
            main,
            ["init", "--models-dir", str(tmp_models_dir)],
        )
        assert result.exit_code == 0
        assert "Would generate macros" in result.output

    def test_init_with_model_filter(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test init with a specific model filter."""
        result = cli_runner.invoke(
            main,
            ["init", "--models-dir", str(tmp_models_dir), "--model", "sample_model"],
        )
        assert result.exit_code == 0
        assert "sample_model" in result.output
