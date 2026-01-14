"""Main CLI entry point for dvt."""

import click

from data_validation_tool import __version__
from data_validation_tool.cli.cloud import cloud
from data_validation_tool.cli.init import init
from data_validation_tool.cli.run import run
from data_validation_tool.core.logger import enable_debug_logging, setup_logging


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug logging.")
@click.version_option(version=__version__, prog_name="dvt")
@click.pass_context
def main(ctx: click.Context, debug: bool) -> None:
    """Data Validation Tool - CLI for dbt data validation workflows.

    This tool helps you generate validation macros, run validations,
    and manage dbt Cloud jobs for data validation.
    """
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    if debug:
        enable_debug_logging()
    else:
        setup_logging()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


main.add_command(init)
main.add_command(run)
main.add_command(cloud)
