"""Run command - Execute validation processes."""

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
    help="Specific model name to validate.",
)
@click.option(
    "--type",
    "-t",
    "validation_type",
    type=click.Choice(["all", "count", "schema", "all_row", "all_col"]),
    default="all",
    help="Type of validation to run.",
)
@click.option(
    "--audit-date",
    "-p",
    type=str,
    default=None,
    help="Audit helper date for cloning from legacy data.",
)
@click.option(
    "--skip-run",
    "-r",
    is_flag=True,
    help="Skip model runs, validate only.",
)
@click.option(
    "--run-only",
    "-v",
    is_flag=True,
    help="Run models only, skip validation.",
)
@click.pass_context
def run(
    _ctx: click.Context,
    models_dir: Path,
    model: str | None,
    validation_type: str,
    audit_date: str | None,
    skip_run: bool,
    run_only: bool,
) -> None:
    """Execute validation processes.

    Runs dbt models and executes validation macros to compare
    source and target data.
    """
    logger.info("Running validations...")
    logger.debug("Models directory: %s", models_dir)
    logger.debug("Validation type: %s", validation_type)

    if skip_run and run_only:
        raise click.UsageError("Cannot use both --skip-run and --run-only")

    # TODO: Implement validation execution logic
    click.echo(f"Would run {validation_type} validation on {models_dir}")
    if model:
        click.echo(f"Filtering to model: {model}")
    if audit_date:
        click.echo(f"Using audit date: {audit_date}")
