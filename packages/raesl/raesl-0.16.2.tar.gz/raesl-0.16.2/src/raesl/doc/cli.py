"""ESL to Doc Command Line Interface."""
import sys
from typing import Iterable, Optional

import click

import raesl.doc
from raesl import logger

run = raesl.doc.convert


@click.command("doc")
@click.argument("paths", nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option(
    "--output",
    "-o",
    default=raesl.doc.OUTPUT,
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help="Output file to write to.",
)
@click.option(
    "--language",
    "-l",
    default=raesl.doc.LANGUAGE,
    type=click.Choice(["en", "nl"], case_sensitive=False),
    help="Output document language.",
)
@click.option(
    "--title",
    "-t",
    default=raesl.doc.TITLE,
    type=click.STRING,
    help="Output document title.",
)
@click.option(
    "--prologue",
    "-p",
    default=raesl.doc.PROLOGUE,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Optional prologue document to include (Markdown).",
)
@click.option(
    "--epilogue",
    "-e",
    default=raesl.doc.EPILOGUE,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Optional epilogue document to include (Markdown).",
)
@click.option(
    "--rich",
    "-r",
    default=raesl.doc.RICH,
    type=click.Choice(["tex", "md", "off"], case_sensitive=False),
    help="Format of rich output to use.",
)
@click.option(
    "--force",
    "-f",
    default=raesl.doc.FORCE,
    is_flag=True,
    help="Force overwrite of output file.",
)
@click.option(
    "--dry",
    "-d",
    default=raesl.doc.DRY,
    is_flag=True,
    help="Dry run. Skip creating an output document.",
)
def doc(
    paths: Iterable[str],
    output: str,
    language: str,
    title: str,
    prologue: Optional[str],
    epilogue: Optional[str],
    rich: Optional[str],
    force: bool,
    dry: bool,
):
    """Convert ESL files and/or directories to a formatted document."""
    logger.info("This is the Ratio ESL Doc command line utility.")
    logger.info(f"Populating '{output}', titled as '{title}' in language '{language}'...")
    try:
        run(
            *paths,
            output=output,
            language=language,
            title=title,
            prologue=prologue,
            epilogue=epilogue,
            rich=rich,
            force=force,
            dry=dry,
        )
        logger.info("Doc generation done!")
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    doc()
