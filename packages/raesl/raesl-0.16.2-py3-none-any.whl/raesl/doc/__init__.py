"""ESL to Doc

A Python package to process specifications in the form of `.esl` files into regular
document formats such as `.pdf`.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from raesl import logger
from raesl.doc.doc import Doc
from raesl.doc.locales import register_default_locale
from raesl.utils import check_output_file_path

register_default_locale()

LANGUAGE = "en"
TITLE = "ESL specification"
OUTPUT = "./esl.pdf"
PROLOGUE = None
EPILOGUE = None
RICH = "tex"
VARTABLE = True
FORCE = False
DRY = False


def convert(
    *paths: Union[str, Path],
    output: Union[str, Path] = OUTPUT,
    language: str = LANGUAGE,
    title: str = TITLE,
    prologue: Optional[Union[str, Path]] = PROLOGUE,
    epilogue: Optional[Union[str, Path]] = EPILOGUE,
    var_table: bool = VARTABLE,
    rich: Optional[str] = RICH,
    rich_opts: Optional[Dict[str, Any]] = None,
    force: bool = FORCE,
    dry: bool = DRY,
    **metadata,
):
    """Convert ESL files and/or directories to a formatted document.

    Arguments:
        paths: Paths to resolve into ESL files. May be any number of files and
            directories to scan.
        output: Optional output file (i.e. Markdown, PDF, DOCX).
        language: Output document language.
        title: Output document title.
        prologue: Optional prologue document to include (Markdown).
        epilogue: Optional epilogue document to include (Markdown).
        var_table: Add table with all variables within appendix.
        rich: Format of rich output to use. One of "tex", "md" or "off".
        rich_opts: Extra options for selected rich output.
        force: Whether to overwrite the output file or raise an error if the file
            already exists.
        dry: Dry run. Skip creating an output document.
    """
    output = Path(output)
    prologue = Path(prologue) if prologue else None
    epilogue = Path(epilogue) if epilogue else None

    logger.debug("Creating Doc object...")
    doc = Doc(
        *paths,
        language=language,
        title=title,
        prologue=prologue,
        epilogue=epilogue,
        var_table=var_table,
        rich=rich,
        rich_opts=rich_opts,
        **metadata,
    )
    logger.debug("Created Doc object!")

    if output:
        output = check_output_file_path(output, force)
        if dry:
            logger.debug("Dry run. Skipped writing to file.")
            return None
        doc.save(output)
