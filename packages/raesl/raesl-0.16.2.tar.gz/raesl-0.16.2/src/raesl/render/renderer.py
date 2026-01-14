"""Main Renderer class module."""

import warnings
from collections.abc import Generator, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, get_args

import plotly.graph_objs as go
import pypst
import pypst.utils

from raesl import logger
from raesl.l10n import LocaleId, get_locale
from raesl.l10n.abc import LocaleAbc
from raesl.render.context import Context, _format_from_path
from raesl.utils import check_output_file_path

Format = Literal["typst", "pdf", "html", "markdown"]
LineGen = Generator["str | Renderer", None, None]


@dataclass
class Renderer:
    """Base class for rendering all supported formats.

    When inheriting, make sure to implement the following

    ```python
    def gen_typst(self) -> LineGen:
        ...
    ```

    or replace the `gen_content` function altogether:

    ```python
    def gen_content(self) -> LineGen:
        ...
    ```
    """

    context: Context = field(metadata=dict(skip=True))

    @property
    def L10N(self) -> LocaleAbc:
        """Localization to use while rendering text."""
        return self.context.l10n

    @L10N.setter
    def L10N(self, locale: LocaleId | LocaleAbc) -> None:
        """Set the rendering locale."""
        if isinstance(locale, LocaleAbc):
            self.context.l10n = locale
        else:
            self.context.l10n = get_locale(locale)

    @property
    def FORMAT(self) -> Format:
        """Output format."""
        return self.context.format

    @FORMAT.setter
    def FORMAT(self, format: Format | str) -> None:
        allowed = get_args(Format)
        if format in allowed:
            self.context.format = "typst" if format == "pdf" else format  # type: ignore
        else:
            raise ValueError(f"Format {format} is unsupported, only {allowed}.")

    @property
    def SEPARATOR(self) -> str:
        """Path segment separator when dealing with ESL types."""
        return self.context.separator

    @property
    def SPACE_CHAR(self) -> str:
        """Character to treat as space when displaying names."""
        return self.context.space_char

    @property
    def OUTPUT_DIR(self) -> Path | None:
        """Output directory."""
        return self.context.output_dir

    @OUTPUT_DIR.setter
    def output_dir(self, dir: Path | None) -> None:
        """Set the renderer's output directory."""
        if dir is not None:
            if dir.is_file():
                raise ValueError(f"Attempted output directory path points to a file: '{dir}'")
            dir.mkdir(parents=True, exist_ok=True)

        self.context.output_dir = dir

    @property
    def FIGURES_DIR(self) -> str | None:
        """(Sub-)directory of the output directory to put figures in."""
        return self.context.figures_dir

    @property
    def FIGURE_CACHE(self) -> dict[str, go.Figure]:
        """Figures waiting to be written to disk."""
        return self.context.figures_cache

    @property
    def RICH(self) -> bool:
        """Whether to generate rich content such as figures."""
        return self.context.rich

    @property
    def FORCE(self) -> bool:
        """Whether to forcefully overwrite any exsiting files when saving."""
        return self.context.force

    def split(self, name: str) -> list[str]:
        """Split a name into its path segments."""
        return self.context.split(name)

    def join(self, segments: Iterable[str]) -> str:
        """Join path segments."""
        return self.context.join(segments)

    def spaced(self, name: str) -> str:
        """Replace characters in a name that are considered a space."""
        return self.context.spaced(name)

    def todo(self) -> LineGen:
        """Render a todo warning, but no content."""
        warnings.warn(f"TODO: implement: {self.__class__.__name__}")
        if False:
            yield ""

    def gen_typst(self) -> LineGen:
        """Generate Typst content."""
        if isinstance(self, pypst.Renderable):
            yield self.render()
        else:
            raise NotImplementedError(f"Typst format not implemented for '{__class__.__name__}'.")

    def gen_markdown(self) -> LineGen:
        """Generate Markdown content."""
        try:
            yield from self.gen_html()
        except NotImplementedError:
            raise NotImplementedError(
                f"Markdown format not implemented for '{__class__.__name__}'."
            )

    def gen_html(self) -> LineGen:
        """Generate HTML content."""
        raise NotImplementedError(f"HTML format not implemented for '{__class__.__name__}'.")

    def gen_content(self) -> LineGen:
        """Generate content for the currently set format."""
        match self.FORMAT:
            case "typst":
                for obj in self.gen_typst():
                    if isinstance(obj, Renderer):
                        yield from obj
                    elif isinstance(obj, str):
                        yield obj
                    else:
                        yield pypst.utils.render(obj)
            case other:
                generator = getattr(self, f"gen_{other}", None)
                if generator is None:
                    raise ValueError(f"Format {self.FORMAT} is not supported.")
                else:
                    yield from generator()

    def __iter__(self) -> LineGen:
        return self.gen_content()

    def __str__(self) -> str:
        return "\n".join(str(c) for c in self.gen_content())

    def compile(
        self,
        path: Path | str | None = None,
        format: Format | str | None = None,
    ) -> bytes | None:
        """Compile this instance's contents to either bytes or a file."""
        logger.debug("Managing output file path, format, and directory...")
        path = path or (self.__class__.__name__)
        path = self.context.resolved_path(path)
        path = check_output_file_path(path, self.FORCE)

        format = format or _format_from_path(path)
        if format:
            self.FORMAT = format

        # Works with a temporary dir if no output is set!
        with self.context.output_dir_context(path.parent) as output_dir:
            logger.debug("Generating textual content...")

            # This also populates self.FIGURE_CACHE, which we can then flush.
            try:
                content = str(self)
            finally:
                self.context.flush_figures()

            match format:
                case "pdf":
                    try:
                        import typst
                    except ImportError:
                        raise ImportError(
                            "Missing the `typst` dependency. Please install the raesl[doc] extra."
                        )

                    input_path = path.with_suffix(".typ")
                    input_path.write_text(content)
                    typst.compile(input_path, output=path, root=output_dir)

                case _:
                    path.write_text(content, encoding="utf-8")
