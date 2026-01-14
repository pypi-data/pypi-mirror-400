"""ESL Language Server config object."""

from pathlib import Path
from typing import Any, List, Optional

from pygls.workspace import Workspace

from raesl import logger
from raesl.utils import check_output_file_path, cleanup_path, get_esl_paths


class EslConfig:
    """ESL workspace configuration.

    Attributes:
        paths: ESL input paths derived from workspace config.
        output: Graph output path derived from workspace config.
    """

    def __init__(self):
        self.paths: Optional[List[Path]] = None
        self.output: Optional[Path] = None

    def get_paths(
        self,
        ws: Workspace,
        doc_uri: Optional[str] = None,
    ) -> Optional[List[Path]]:
        """Current set of ESL paths."""
        if doc_uri is None:
            return self.paths

        doc_path = cleanup_path(doc_uri)

        # If no paths are set or if outside of current scope: return doc_path.
        # Otherwise, we have paths set and the doc_path is part of them.
        if self.paths is None:
            logger.info("No paths set, returning document path...")
            return [doc_path]
        elif doc_path not in self.paths:
            logger.info("Document path outside current set paths, returning that...")
            return [doc_path]
        else:
            logger.info("Returning set paths...")
            return self.paths

    def parse_config(self, ws: Workspace, cfg: Any):
        """Parse workspace config."""
        logger.info(f"Parsing config: '{cfg}'...")

        # Handle paths variable.
        paths = getattr(cfg, "eslPaths", False)
        if ws and ws.root_path:
            root = ws.root_path
            logger.info(f"Found root '{root}'.")
        else:
            root = None

        if paths:
            logger.info(f"Parsing config paths {paths}...")
            self.paths = get_esl_paths([cleanup_path(p) for p in paths], root=root)
            logger.info(f"Parsed into '{self.paths}'.")

        elif ws is not None and ws.root_path:
            logger.info("Parsing workspace root...")
            self.paths = get_esl_paths([ws.root_path], root=root)

        else:
            logger.info("No paths found so far, setting None.")
            self.paths = None

        # Handle graph output variable.
        try:
            output = getattr(cfg, "graphPath", None)
            self.output = check_output_file_path(cleanup_path(output), True, root=root)
        except (ValueError, TypeError):
            self.output = None
        logger.info(f"Set graph output to '{self.output}'.")

        logger.info("Parsed config.")
