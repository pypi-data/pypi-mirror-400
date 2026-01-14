"""Ratio ESL ``raesl`` Command Line Interface (CLI)."""
import click
import click_log

from raesl import __version__, logger
from raesl.doc.cli import doc
from raesl.excel.cli import component_excel, excel
from raesl.jupyter.cli import jupyter
from raesl.server.cli import serve

# Compile module is excluded during docs generation.
try:
    from raesl.compile.cli import compile
except ImportError:
    pass

click_log.basic_config(logger=logger)


@click.group("raesl")
@click_log.simple_verbosity_option(logger)
@click.pass_context
def cli(ctx: click.Context):
    """Elephant Specification Language support by Ratio."""
    pass


@cli.command()
def version():
    """Print Ratio ESL version and exit."""
    logger.info(f"Ratio ESL version: {__version__}.")


cli.add_command(compile)
cli.add_command(doc)
cli.add_command(excel)
cli.add_command(component_excel)
cli.add_command(jupyter)
cli.add_command(serve)

if __name__ == "__main__":
    cli()
