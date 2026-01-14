"""ESL compiler.

Compiles ESL documents and workspaces, meaning:

- Parsing lines
- Typechecking
- Building an AST
- Instantiating components, variables and requirements.
- Deriving dependencies from these to build an output graph (network).
"""
from pathlib import Path
from typing import Optional, Union

from ragraph.graph import Graph

import raesl.compile.cli


class EslCompilationError(Exception):
    """Error during ESL compilation."""


def to_graph(
    *paths: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    force: bool = False,
) -> Graph:
    """Convert ESL file(s) into a :obj:`ragraph.graph.Graph`.

    Arguments:
        paths: Paths to resolve into ESL files. May be any number of files and
            directories to scan.
        output: Optional output file (JSON) to write the graph to.
        force: Whether to overwrite the output file or raise an error if it the file
            already exists.

    Returns:
        Instantiated graph.
    """

    diag, spec, graph = raesl.compile.cli.run(*paths, output=output, force=force)

    if graph is None:
        errors = "\n".join(str(d) for d in diag.diagnostics)
        raise EslCompilationError(
            f"Could not compile the specification into a Graph object:\n{errors}"
        )

    return graph
