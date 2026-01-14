"""Tests for the run command."""

from click.testing import CliRunner

from data_validation_tool.cli.main import main


class TestRunCommand:
    """Tests for the run command."""

    def test_run_help(self, cli_runner: CliRunner) -> None:
        """Test run --help displays help text."""
        result = cli_runner.invoke(main, ["run", "--help"])
        assert result.exit_code == 0
        assert "Execute validation processes" in result.output
        assert "--models-dir" in result.output
        assert "--type" in result.output
        assert "--skip-run" in result.output
        assert "--run-only" in result.output

    def test_run_with_valid_dir(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test run with a valid models directory."""
        result = cli_runner.invoke(
            main,
            ["run", "--models-dir", str(tmp_models_dir)],
        )
        assert result.exit_code == 0
        assert "Would run all validation" in result.output

    def test_run_with_validation_type(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test run with specific validation type."""
        result = cli_runner.invoke(
            main,
            ["run", "--models-dir", str(tmp_models_dir), "--type", "count"],
        )
        assert result.exit_code == 0
        assert "count validation" in result.output

    def test_run_conflicting_flags(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test run fails with conflicting --skip-run and --run-only."""
        result = cli_runner.invoke(
            main,
            ["run", "--models-dir", str(tmp_models_dir), "--skip-run", "--run-only"],
        )
        assert result.exit_code != 0
        assert "Cannot use both" in result.output

    def test_run_with_model_filter(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test run with specific model filter."""
        result = cli_runner.invoke(
            main,
            ["run", "--models-dir", str(tmp_models_dir), "--model", "my_model"],
        )
        assert result.exit_code == 0
        assert "my_model" in result.output

    def test_run_with_audit_date(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test run with audit date option."""
        result = cli_runner.invoke(
            main,
            ["run", "--models-dir", str(tmp_models_dir), "--audit-date", "2024-01-01"],
        )
        assert result.exit_code == 0
        assert "2024-01-01" in result.output
