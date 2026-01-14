"""Language Server class module."""

from collections import defaultdict
from pathlib import Path
from typing import List, Optional

import lsprotocol as lsp
from pygls import server

from raesl import logger
from raesl.server.config import EslConfig
from raesl.utils import cleanup_path, path_to_uri

# Compile module is excluded during docs generation.
try:
    from raesl.compile import diagnostics, parser, scanner
    from raesl.compile.instantiating import graph_building
except ImportError:
    pass

from raesl import __version__


class EslServer(server.LanguageServer):
    """ESL Language Server."""

    CONFIG = "esl"  # Config section in editors.
    CMD_COMPILE_PATH = "esl.compilePath"

    def __init__(self):
        super().__init__("RaESL", __version__)
        self.config = EslConfig()

    async def update_config(self):
        """Handle a config update request."""
        self.show_message_log("Refreshing server config...")
        try:
            cfg = await self.get_configuration_async(
                lsp.ConfigurationParams([lsp.ConfigurationItem("", self.CONFIG)])
            )
            self.config.parse_config(self.workspace, cfg[0])
            self.show_message_log("Refreshed server config.")
        except Exception as e:
            self.show_message_log(f"Error occurred while updating config: '{e}'.")


ls = EslServer()


@ls.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: EslServer, params: lsp.DidOpenTextDocumentParams):
    """Opened document handling."""
    ls.show_message_log(f"Opened: '{params.textDocument.uri}'")
    await ls.update_config()
    _validate(ls, ls.config.get_paths(ls.workspace, params.textDocument.uri))


@ls.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
async def did_close(ls: EslServer, params: lsp.DidCloseTextDocumentParams):
    """Closed document handling."""
    ls.show_message_log(f"Closed: '{params.textDocument.uri}'")
    await ls.update_config()
    paths = ls.config.get_paths(ls.workspace) or []
    if cleanup_path(params.textDocument.uri) not in paths:
        ls.publish_diagnostics(doc_uri=params.textDocument.uri, diagnostics=[])
    _validate(ls, paths)


@ls.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: EslServer, params: lsp.DidSaveTextDocumentParams):
    """Saved document handling."""
    ls.show_message_log(f"Saved: '{params.textDocument.uri}'")
    await ls.update_config()
    _validate(ls, ls.config.get_paths(ls.workspace, params.textDocument.uri))


@ls.feature(lsp.WORKSPACE_DID_CHANGE_WATCHED_FILES)
async def did_change_watched(ls: EslServer, params: lsp.DidChangeWatchedFilesParams):
    """Changed watched files handling."""
    ls.show_message_log(f"Changed: '{params.changes}")
    await ls.update_config()
    _validate(ls, ls.config.get_paths(ls.workspace))


@ls.feature(lsp.WORKSPACE_DID_CHANGE_CONFIGURATION)
async def did_change_config(ls: EslServer, params: lsp.DidChangeConfigurationParams):
    """Config changed handling."""
    ls.show_message_log("Workspace config changed.")
    await ls.update_config()
    _validate(ls, ls.config.get_paths(ls.workspace))


@ls.feature("$/setTraceNotification")
async def set_trace_notification(ls: EslServer, *args):
    """Unkown notification. Probably a config change."""
    ls.show_message_log("Unknown notification.")
    await ls.update_config()
    _validate(ls, ls.config.get_paths(ls.workspace))


def _validate(ls: EslServer, paths: Optional[List[Path]] = None) -> bool:
    """Validate ESL files on given paths and push diagnostics."""
    if not paths:
        logger.info("No paths to validate.")
        return True
    try:
        logger.info(f"Validating '{paths}'...")
        # Create specification object.
        diag_store, spec = parser.parse_spec(
            scanner.Lexer(str(p), p.read_text(), 0, 0, 0, []) for p in paths
        )
        if diag_store.has_severe() or spec is None:
            _publish(ls, paths, diag_store)
            logger.error("Parsing failed validation.")
            return False

        # Derive dependency graph.
        graph = graph_building.GraphFactory(diag_store=diag_store, spec=spec).make_graph()
        if diag_store.has_severe() or graph is None:
            _publish(ls, paths, diag_store)
            logger.error("Graph building failed validation.")
            return False
        elif ls.config.output is not None:
            ls.show_message_log(f"Dumping output graph to '{ls.config.output}'...")
            from ragraph.io.json import to_json

            to_json(graph, path=ls.config.output)
            ls.show_message_log("Dumped output graph.")

        # Publish any non-severe diagnostics.
        _publish(ls, paths, diag_store)
        logger.info("Successful validation.")
        return True

    except Exception as e:
        ls.show_message(
            f"Unexpected error:\n{e}",
            msg_type=lsp.MessageType.Error,
        )
        return False


def _publish(ls: EslServer, paths: List[Path], diag_store: diagnostics.DiagnosticStore):
    """Publish diagnostics from the Diagnostic Store via the language server."""
    ls.show_message_log(f"Publishing {len(diag_store.diagnostics)} diagnostic(s)...")

    # Fetch diagnostics per URI and cast to pygls Diagnostic.
    diag_map = defaultdict(list)
    for diag in diag_store.diagnostics:
        if diag.related_information:
            related = [
                lsp.DiagnosticRelatedInformation(info.location, info.message)
                for info in diag.related_information
            ]
        else:
            related = None

        diagnostic = lsp.Diagnostic(
            range=lsp.Range(diag.range.start, diag.range.end),
            message=diag.message,
            severity=lsp.DiagnosticSeverity[diag.severity.name],
            code=diag.code,
            source=diag.source,
            related_information=related,
        )

        uri = path_to_uri(diag.location.uri)
        diag_map[uri].append(diagnostic)

    # Publish diagnostics per URI.
    for path in paths:
        p = path_to_uri(path)
        ls.publish_diagnostics(doc_uri=p, diagnostics=diag_map[p])

    ls.show_message_log("Published diagnostic(s).")
