"""ESL compiler Command Line Interface."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import click

from raesl import logger
from raesl.utils import check_output_file_path, get_esl_paths

# Compile module is excluded during docs generation.
try:
    from raesl.compile import parser, scanner
    from raesl.compile.instantiating import graph_building
except ImportError:
    pass

if TYPE_CHECKING:
    from ragraph.graph import Graph

    from raesl.compile.ast.specification import Specification
    from raesl.compile.diagnostics import DiagnosticStore


def run(
    *paths: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    force: bool = False,
    files: Optional[Union[List[str], List[Path]]] = None,
) -> Tuple["DiagnosticStore", Optional["Specification"], Optional["Graph"]]:
    """Run the compiler on ESL files.

    Arguments:
        paths: Paths to resolve into ESL files. May be any number of files and
            directories to scan.
        output: Optional output file (JSON) to write the graph to.
        force: Whether to overwrite the output file or raise an error if the file
            already exists.
        files: Optional paths argument (deprecated).

    Returns:
        Diagnostic storage.
        Specification object (if successfully parsed).
        Instantiated graph (if successfully instantiated).
    """
    if files is not None:
        paths = tuple(files)
        msg = " ".join(
            (
                "The 'files' keyword argument will be deprecated.",
                "Please use your file and directory paths as (any number of)",
                "positional arguments to this function.",
                "Also, take a look at 'raesl.compile.to_graph'",
                "or its alias 'ragraph.io.esl.from_esl'. to obtain a Graph.",
            )
        )
        logger.warning(msg)

    try:
        in_files = get_esl_paths(*paths)
        out_file = None if output is None else check_output_file_path(output, force)
    except ValueError as e:
        if click.get_current_context(silent=True):
            logger.error(str(e))
            sys.exit(1)
        raise e

    # Parse lexers per file.
    diag_store, spec = parser.parse_spec(
        scanner.Lexer(str(f), f.read_text(), 0, 0, 0, []) for f in in_files
    )

    # Errors have been reported to stdout already.
    if diag_store.has_severe() or spec is None:
        if click.get_current_context(silent=True):
            sys.exit(1)
        return diag_store, None, None

    # Succeeded so far: instantiate.
    graph = graph_building.GraphFactory(diag_store=diag_store, spec=spec).make_graph()
    if diag_store.has_severe() or graph is None:
        if click.get_current_context(silent=True):
            sys.exit(1)
        return diag_store, spec, None

    if output is not None:
        from ragraph.io.json import to_json

        to_json(graph, path=out_file)

    return diag_store, spec, graph


@click.command("compile")
@click.argument("paths", nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(file_okay=True, dir_okay=False),
    help="Graph output file.",
)
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    help="Whether to overwrite an existing output file.",
)
def compile(paths: List[str], output: Optional[str], force: bool):
    """Run the ESL compiler."""
    run(*paths, output=output, force=force)
