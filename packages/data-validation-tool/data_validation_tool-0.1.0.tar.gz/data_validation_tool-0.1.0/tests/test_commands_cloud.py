"""Tests for the cloud command."""

from click.testing import CliRunner

from data_validation_tool.cli.main import main


class TestCloudCommand:
    """Tests for the cloud command."""

    def test_cloud_help(self, cli_runner: CliRunner) -> None:
        """Test cloud --help displays help text."""
        result = cli_runner.invoke(main, ["cloud", "--help"])
        assert result.exit_code == 0
        assert "Generate dbt Cloud job configurations" in result.output
        assert "--models-dir" in result.output
        assert "--account-id" in result.output
        assert "--project-id" in result.output
        assert "--environment-id" in result.output

    def test_cloud_missing_required_options(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test cloud fails without required options."""
        result = cli_runner.invoke(main, ["cloud", "--models-dir", str(tmp_models_dir)])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_cloud_with_all_options(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test cloud with all required options."""
        result = cli_runner.invoke(
            main,
            [
                "cloud",
                "--models-dir",
                str(tmp_models_dir),
                "--account-id",
                "12345",
                "--project-id",
                "67890",
                "--environment-id",
                "11111",
            ],
        )
        assert result.exit_code == 0
        assert "Would generate jobs YAML" in result.output
        assert "12345" in result.output

    def test_cloud_with_env_vars(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test cloud reads from environment variables."""
        result = cli_runner.invoke(
            main,
            ["cloud", "--models-dir", str(tmp_models_dir)],
            env={
                "DBT_CLOUD_ACCOUNT_ID": "99999",
                "DBT_CLOUD_PROJECT_ID": "88888",
                "DBT_CLOUD_ENVIRONMENT_ID": "77777",
            },
        )
        assert result.exit_code == 0
        assert "99999" in result.output

    def test_cloud_with_model_filter(self, cli_runner: CliRunner, tmp_models_dir) -> None:
        """Test cloud with specific model filter."""
        result = cli_runner.invoke(
            main,
            [
                "cloud",
                "--models-dir",
                str(tmp_models_dir),
                "--account-id",
                "12345",
                "--project-id",
                "67890",
                "--environment-id",
                "11111",
                "--model",
                "my_model",
            ],
        )
        assert result.exit_code == 0
        assert "my_model" in result.output
