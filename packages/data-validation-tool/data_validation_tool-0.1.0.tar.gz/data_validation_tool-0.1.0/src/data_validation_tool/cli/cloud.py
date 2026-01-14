"""Cloud command - Manage dbt Cloud jobs as code."""

from pathlib import Path

import click

from data_validation_tool.core.logger import get_logger

logger = get_logger()


@click.command()
@click.option(
    "--models-dir",
    "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("models/03_mart"),
    help="Directory containing dbt models.",
)
@click.option(
    "--model",
    "-m",
    type=str,
    default=None,
    help="Specific model name to create job for.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("dataops/dbt_cloud_jobs.yml"),
    help="Output path for the jobs YAML file.",
)
@click.option(
    "--account-id",
    type=str,
    envvar="DBT_CLOUD_ACCOUNT_ID",
    required=True,
    help="dbt Cloud account ID (or set DBT_CLOUD_ACCOUNT_ID).",
)
@click.option(
    "--project-id",
    type=str,
    envvar="DBT_CLOUD_PROJECT_ID",
    required=True,
    help="dbt Cloud project ID (or set DBT_CLOUD_PROJECT_ID).",
)
@click.option(
    "--environment-id",
    type=str,
    envvar="DBT_CLOUD_ENVIRONMENT_ID",
    required=True,
    help="dbt Cloud environment ID (or set DBT_CLOUD_ENVIRONMENT_ID).",
)
@click.pass_context
def cloud(
    _ctx: click.Context,
    models_dir: Path,
    model: str | None,
    output: Path,
    account_id: str,
    project_id: str,
    environment_id: str,
) -> None:
    """Generate dbt Cloud job configurations as YAML.

    Creates a YAML file compatible with dbt-jobs-as-code for managing
    validation jobs in dbt Cloud.
    """
    logger.info("Generating dbt Cloud job configuration...")
    logger.debug("Account ID: %s", account_id)
    logger.debug("Project ID: %s", project_id)
    logger.debug("Environment ID: %s", environment_id)

    # TODO: Implement job YAML generation logic
    click.echo(f"Would generate jobs YAML from {models_dir} to {output}")
    if model:
        click.echo(f"Filtering to model: {model}")
    click.echo(f"Using dbt Cloud account: {account_id}")
