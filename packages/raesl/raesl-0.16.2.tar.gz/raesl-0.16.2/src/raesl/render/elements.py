"""Elementary rendering blocks such as a heading, paragraph, list, and so on."""

from collections.abc import Generator, Iterable
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import pypst
import pypst.utils

from raesl.render import html
from raesl.render.renderer import LineGen, Renderer
from raesl.render.typst import ensure_typst_arg
from raesl.utils import cap


@dataclass
class Heading(Renderer):
    """Heading of a variable level."""

    body: str | Renderer
    level: int = 1
    capitalize: bool = False
    label: str | None = None

    def __post_init__(self) -> None:
        self.body = str(self.body).strip()
        if self.capitalize:
            self.body = cap(self.body)

    def gen_typst(self) -> LineGen:
        yield str(pypst.Heading(level=self.level, body=str(self.body)))
        if self.label:
            yield f"<{self.label}>\n"

    def gen_markdown(self) -> LineGen:
        yield f"{self.level * '#'} {self.body}"

    def gen_html(self) -> LineGen:
        yield html.tagged(tag=f"h{self.level}", content=self.body)


@dataclass
class BoldHeading(Renderer):
    """Bold heading without numbering."""

    body: str | Renderer
    cap: bool = False

    def __post_init__(self) -> None:
        self.body = str(self.body).strip()
        if self.cap:
            self.body = cap(self.body)

    def gen_typst(self) -> LineGen:
        yield ""
        yield Bold(self.context, self.body)
        yield ""

    def gen_markdown(self) -> LineGen:
        yield ""
        yield Bold(self.context, self.body)
        yield ""

    def gen_html(self) -> LineGen:
        yield f"{html.BREAK}{Bold(self.context, self.body)}{html.BREAK}"


@dataclass
class Bold(Renderer):
    """Bold text."""

    body: str | Renderer

    def __post_init__(self) -> None:
        self.body = str(self.body).strip()

    def gen_typst(self) -> LineGen:
        yield f"#strong[{self.body}]"

    def gen_markdown(self) -> LineGen:
        yield f"**{self.body}**"

    def gen_html(self) -> LineGen:
        yield html.tagged("strong", content=self.body)


@dataclass
class Emph(Renderer):
    """Emphasized text."""

    body: str | Renderer

    def __post_init__(self) -> None:
        self.body = str(self.body).strip()

    def gen_typst(self) -> LineGen:
        yield f"#emph[{self.body}]"

    def gen_markdown(self) -> LineGen:
        yield f"*{self.body}*"

    def gen_html(self):
        yield html.tagged("em", content=self.body)


@dataclass
class Raw(Renderer):
    "Raw text/code."

    body: str | Renderer

    def gen_typst(self) -> LineGen:
        yield f"`{self.body}`"

    def gen_markdown(self) -> LineGen:
        yield f"`{self.body}`"

    def gen_html(self) -> LineGen:
        yield html.tagged("code", content=self.body)


@dataclass
class Par(Renderer):
    """Paragraph containing text."""

    body: str | Renderer | list[str] | list[Renderer] | list[str | Renderer] | None

    def yield_stripped_body(
        self, body: str | Renderer | list[str] | list[Renderer] | list[str | Renderer] | None = None
    ) -> Generator[str, None, None]:
        if isinstance(body, str):
            yield body.strip("\n")
        elif body is None:
            return None
        else:
            for el in body:
                if el:
                    yield from self.yield_stripped_body(el)

    def gen_typst(self) -> LineGen:
        yield from self.yield_stripped_body(self.body)
        yield ""

    def gen_markdown(self) -> LineGen:
        yield from self.gen_typst()

    def gen_html(self) -> LineGen:
        if self.body is None:
            return None
        yield html.tagged("p", content=list(self.yield_stripped_body(self.body)))


@dataclass
class List(Renderer):
    """Any list, ordered or unordered."""

    items: Iterable[str | Renderer]
    level: int = 0
    kind: Literal["ordered", "unordered", "terms"] = "unordered"

    def __post_init__(self):
        assert not isinstance(self.items, str)

    def indent(self) -> str:
        return self.level * "  "

    def gen_typst(self) -> LineGen:
        indent = self.indent()
        for obj in self.items:
            if isinstance(obj, list):
                next = self.__class__(obj, level=self.level + 1)
                yield from next.gen_typst()
            elif isinstance(obj, List):
                obj.level = self.level + 1
                yield from obj.gen_typst()
            else:
                if isinstance(obj, LabeledLine):
                    yield f"{indent}{obj}"
                    continue

                match self.kind:
                    case "terms":
                        prefix = "/ "
                    case "ordered":
                        prefix = "+ "
                    case _:
                        prefix = "- "

                text = str(obj)
                text = text.replace("\n", f"\n{indent}")
                yield f"{indent}{prefix}{text}"
        if self.level == 0:
            yield ""

    def gen_markdown(self) -> LineGen:
        indent = self.indent()
        for obj in self.items:
            if isinstance(obj, list):
                next = self.__class__(obj, level=self.level + 1)
                yield from next.gen_markdown()
            elif isinstance(obj, List):
                obj.level = self.level + 1
                yield from obj.gen_markdown()
            else:
                if isinstance(obj, LabeledLine):
                    yield f"{indent}{obj}"
                    continue

                match self.kind:
                    case "terms":
                        prefix = "- "
                    case "ordered":
                        prefix = "1. "
                    case _:
                        prefix = "- "

                text = str(obj)
                text = text.replace("\n", f"\n{indent}")
                yield f"{indent}{prefix}{text}"
        if self.level == 0:
            yield ""

    def gen_html(self) -> LineGen:
        match self.kind:
            case "terms":
                tag = "dl"
            case "ordered":
                tag = "ol"
            case "unordered":
                tag = "ul"

        yield f"<{tag}>"
        for obj in self.items:
            if isinstance(obj, List):
                obj.level = self.level + 1
                yield from obj
            else:
                yield html.tagged("li", content=str(obj))
        yield f"</{tag}>"


@dataclass
class Ordered(List):
    """Ordered (numbered) list."""

    def __post_init__(self) -> None:
        self.kind = "ordered"


@dataclass
class Unordered(List):
    """Unordered (bullet) list."""

    def __post_init__(self) -> None:
        self.kind = "unordered"


@dataclass
class Terms(List):
    """Term description list."""

    def __post_init__(self) -> None:
        self.kind = "terms"


@dataclass
class LabeledLine(Renderer):
    """Render a line with a label in front, resulting in a description in Typst."""

    line: str
    label: str | None = None

    def gen_typst(self) -> LineGen:
        yield f"/ {self.label}: {self.line}"

    def gen_markdown(self) -> LineGen:
        if self.label:
            label = Bold(self.context, f"{self.label}:")
            yield f"{label} {self.line}"
        else:
            yield {self.line}

    def gen_html(self) -> LineGen:
        yield html.tagged("dt", self.label)
        yield html.tagged("dd", self.line)


@dataclass
class IncludeFile(Renderer):
    """Verbatim inclusion of a file."""

    path: Path
    encoding: str = "utf-8"

    def text(self) -> str:
        return self.path.read_text(self.encoding)

    def gen_content(self) -> LineGen:
        yield self.text()


@dataclass
class Label(Renderer):
    """Label to reference to."""

    kind: Literal["fig", "sec", "tab", "path"]
    label: str | None

    def gen_typst(self) -> LineGen:
        yield f"<{self.kind}:{self.label}>"

    def gen_markdown(self) -> LineGen:
        yield from self.gen_html()

    def gen_html(self) -> LineGen:
        yield html.tagged("div", id=f"{self.kind}:{self.label}")


@dataclass
class Reference(Renderer):
    """Reference to a label defined elsewhere."""

    kind: Literal["fig", "sec", "tab", "path"]
    label: str
    display: str | None = None

    def gen_typst(self) -> LineGen:
        label_str = f"{self.kind}:{self.label}"
        if self.display is None:
            yield f"@{label_str}"
        else:
            yield f"#context{{if query(<{label_str}>).len() == 0 [{self.display}] else [#link(<{label_str}>)[{self.display}]]}}"  # noqa: E501

    def gen_markdown(self) -> LineGen:
        yield from self.gen_html()

    def gen_html(self) -> LineGen:
        label_str = f"{self.kind}:{self.label}"
        yield html.tagged("a", content=self.display or label_str, href=f"#{label_str}")


@dataclass
class TableCell(Renderer, pypst.utils.Function):
    """Cell in a table to render."""

    __is_function__ = "table.cell"

    body: str | Renderer | None = field(
        default=None, metadata=dict(positional=True, keep_none=True)
    )
    colspan: int | None = None
    x: int | None = None
    y: int | None = None
    colspan: int | None = None
    rowspan: int | None = None
    fill: str | None = None
    align: str | None = None
    inset: str | None = None
    stroke: str | None = None
    breakable: bool | None = None
    html_head: bool = field(default=False, metadata=dict(skip=True))

    def gen_typst(self) -> LineGen:
        patched = deepcopy(self)
        patched.body = str(pypst.Content(str(self.body))) if self.body else "none"
        yield patched.render()

    def gen_html(self) -> LineGen:
        yield html.tagged("th" if self.html_head else "td", content=self.body)


@dataclass
class TableHeader(Renderer, pypst.utils.Function):
    __is_function__ = "table.header"

    children: list[TableCell | Renderer | str | None] | str | Renderer | None = field(
        default=None, metadata={"positional": True, "keep_none": True}
    )
    repeat: bool = True
    row_length: int = field(default=1, metadata=dict(skip=True))

    def gen_typst(self) -> LineGen:
        patched = deepcopy(self)
        patched.children = ", ".join(ensure_typst_arg(c) for c in self.children)
        yield patched.render()

    def gen_html(self) -> LineGen:
        for child in self.children:
            if isinstance(child, TableCell):
                child.html_head = True
                yield from child
            else:
                yield from TableCell(self.context, body=child, html_head=True)


@dataclass
class TableHLine(Renderer, pypst.utils.Function):
    __is_function__ = "table.hline"

    y: int | None = None
    start: int | None = None
    end: int | None = None
    stroke: str | None = '(thickness: 1pt, dash: "dashed", paint: palette.secondary-100)'
    position: str | None = None

    def gen_html(self) -> LineGen:
        yield html.tagged("tr", style="border-top: '1pt dashed'")


@dataclass
class Table(Renderer, pypst.utils.Function):
    """Table to render."""

    children: list[TableHeader | TableCell | TableHLine | Renderer | str | None] | str | None = (
        field(
            default=None,
            metadata=dict(positional=True, keep_none=True),
        )
    )
    columns: int | list[str] | str | None = None
    rows: int | list[str] | str | None = None
    gutter: int | list[str] | str | None = None
    column_gutter: int | list[str] | str | None = field(
        default="0.5em",
        metadata=dict(name="column-gutter"),
    )
    row_gutter: int | list[str] | str | None = field(
        default="auto",
        metadata=dict(name="row-gutter"),
    )
    fill: list[str] | str | None = None
    align: list[str] | str | None = None
    stroke: list[str] | str | None = None
    inset: list[str] | str | None = "(x: 0pt)"
    caption: str | None = field(default=None, metadata=dict(skip=True))
    label: str | None = field(default=None, metadata=dict(skip=True))

    def __post_init__(self) -> None:
        if self.columns is None:
            for child in self.children:
                if isinstance(child, list):
                    self.columns = len(child)
                    break
                elif isinstance(child, TableHeader):
                    if isinstance(child.children, list):
                        self.columns = len(child.children)
                        break

    def gen_typst(self) -> LineGen:
        # Create a copy without caption and label to get them skipped when rendering the table fn.
        patched = deepcopy(self)
        patched.children = ", ".join(ensure_typst_arg(c) for c in patched.children)
        body = patched.render()

        yield pypst.Figure(
            body=body,
            caption=self.caption,
            outlined=bool(self.caption),
        ).render()

        if self.label:
            yield Label(self.context, kind="tab", label=self.label)

    def gen_html(self) -> LineGen:
        match self.columns:
            case int():
                n_columns = self.columns
            case str():
                n_columns = len(self.columns.split(","))
            case list():
                n_columns = len(self.columns)
            case _:
                n_columns = 1

        rows = []
        row = []
        for child in self.children:
            if isinstance(child, TableHeader):
                if row:
                    rows.append(html.tagged("tr", row))
                    row = []
                rows.append(child)
            elif isinstance(child, TableCell):
                row.append(child)
            elif isinstance(child, TableHLine):
                if row:
                    rows.append(html.tagged("tr", row))
                    row = []
                rows.append(child)
            else:
                row.append(TableCell(self.context, child))

            if len(row) == n_columns:
                rows.append(html.tagged("tr", row))
                row = []

        # Don't forget about any unfinished rows!
        if row:
            rows.append(html.tagged("tr", row))

        # Yield the full table.
        yield html.tagged("table", content=rows, multiline=True)
