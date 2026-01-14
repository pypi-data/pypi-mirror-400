"""Rendering context module."""

from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from plotly import graph_objects as go
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.plot.utils import write_images

from raesl import logger
from raesl.l10n.abc import LocaleAbc
from raesl.l10n.en_us import EnUs
from raesl.render import Format
from raesl.utils import check_output_file_path


def _suffix_from_format(format: Format | str) -> str:
    """Get the corresponding file suffix for a supported document format."""
    match format:
        case "typst":
            return ".typ"
        case "markdown":
            return ".md"
        case _:
            return f".{format}"


def _format_from_suffix(suffix: str) -> Format | str:
    """Extract a target from a file suffix."""
    suffix = suffix.lstrip(".")
    match suffix:
        case "typ":
            return "typst"
        case "md":
            return "markdown"
        case _:
            return suffix


def _format_from_path(path: Path) -> Format | str:
    """Extract a target from an output path and returns "pdf" if there isn't any."""
    if path.suffix:
        return _format_from_suffix(path.suffix)
    else:
        return "pdf"


@dataclass
class Context:
    """Rendering context containing common settings for any renderer."""

    l10n: LocaleAbc = field(default_factory=EnUs)
    """Localization to use while rendering text."""

    format: Format = "typst"
    """Output format."""

    separator: str = "."
    """Path segment separator when dealing with ESL types."""

    space_char: str = "_"
    """Character to treat as space when displaying names."""

    output_dir: Path | None = None
    """Output directory for files."""

    figures_dir: Path = field(default=Path("figures"))
    """(Sub-)directory of the output directory to put figures in."""

    figures_cache: dict[str, go.Figure] = field(default_factory=dict)
    """FIgures waiting to be written to disk."""

    rich: bool = True
    """Whether to generate rich content such as figures."""

    force: bool = True
    """Whether to forcefully overwrite any exsiting files when saving."""

    def split(self, name: str) -> list[str]:
        """Split a name into its path segments."""
        return name.split(self.separator)

    def join(self, segments: Iterable[str]) -> str:
        """Join path segments."""
        return self.separator.join(segments)

    def spaced(self, name: str) -> str:
        """Replace characters in a name that are considered a space."""
        return name.replace(self.space_char, " ")

    @contextmanager
    def output_dir_context(self, path: str | Path | None = None) -> Generator[Path, None, None]:
        """Either ensure the given directory exists or yield a temporary directory to work in."""
        current = self.output_dir
        try:
            if path is None:
                if current is None:
                    self.output_dir = Path.cwd()
            else:
                self.output_dir = Path(path)

            self.output_dir.mkdir(exist_ok=True, parents=True)

            yield self.output_dir
        finally:
            self.output_dir = current

    @contextmanager
    def figures_dir_context(self) -> Generator[Path, None, None]:
        with self.output_dir_context() as out:
            figs_dir = out / self.figures_dir
            figs_dir.mkdir(exist_ok=True, parents=True)
            yield figs_dir

    def resolved_path(self, path: str | Path) -> Path:
        """Generate a relative path to the output directory."""
        path = Path(path)
        if path.is_absolute():
            return path

        if self.output_dir is None:
            return Path.cwd() / path

        return self.output_dir / path

    def figure_path(self, path: str, resolved: bool = False) -> Path:
        """Get a resolved path in the figures directory."""
        path = self.figures_dir / path
        return self.resolved_path(path) if resolved else path

    def add_figure(self, figure: go.Figure, file: str):
        """Add a figure to the queue to be output in the output directory under "figures"
        subdirectory.
        """
        self.figures_cache[str(file)] = figure

    def flush_figures(self):
        """Write images to the output directory and clear the queue."""
        if not self.figures_cache:
            logger.debug("No figures to flush.")
            return

        logger.debug(f"Writing {len(self.figures_cache)} figures to file...")

        with self.output_dir_context() as out:
            (out / self.figures_dir).mkdir(exist_ok=True, parents=True)
            paths = [
                check_output_file_path(self.resolved_path(p), force=self.force)
                for p in self.figures_cache.keys()
            ]
            figures = list(self.figures_cache.values())
            write_images(figures=figures, paths=paths)
            self.figures_cache.clear()

    def _path_segments(self, node: Node | str | list[str]) -> list[str]:
        """Get the path segments for various input options."""
        if isinstance(node, list):
            return node
        else:
            name = node.name if isinstance(node, Node) else node
            return self.split(name)

    def _ref_path_and_segments(self, node: Node | str | list[str]) -> tuple[str, list[str]]:
        """Split commond node argument into a reference path and it's segments."""
        if isinstance(node, list):
            segments = node
            ref_path = self.join(segments)
        else:
            ref_path = node.name if isinstance(node, Node) else node
            segments = self.split(ref_path)
        return (ref_path, segments)

    def _try_component_path_split_with_args(
        self,
        ref_path: str,
        segments: list[str],
        node: Node | None = None,
        graph: Graph | None = None,
    ) -> int:
        """Try to obtain the component path split point, and raise an error for incompatible
        arguments.

        Arguments:
            ref_path: Full string path to the item.
            segments: Split path to the item.
            node: Optional node in the graph. Used to check whether it's a component.
            graph: Optional graph to figure out the split point between component segments and
                others.
        """
        if isinstance(node, Node) and node.kind == "component":
            return len(segments)
        elif graph is None:
            raise ValueError(
                "Graph can't be None for non-component paths where context or parent component "
                "skipping is relevant."
            )
        elif ref_path in graph and graph[ref_path].kind == "component":
            return len(segments)
        else:
            return self._find_component_path_split(segments, graph)

    def _find_component_path_split(self, segments: list[str], graph: Graph) -> int:
        """Find the split between component path segments and bundle indexing.

        Arguments:
            segments: Path segments to check for the split between component and other node types.
            graph: Node lookup graph.
        """
        n_segments = len(segments)
        lookup = segments[0]
        i = 1
        while i < n_segments and lookup in graph and graph[lookup].kind == "component":
            lookup = self.join((lookup, segments[i]))
            i += 1
        # now i minus 1 is the split between component path and variable path/bundle indexing.
        return i - 1
