"""Figure rendering module."""

from dataclasses import dataclass, field
from pathlib import Path

import pypst
from plotly import graph_objects as go
from ragraph.graph import Graph

from raesl import logger
from raesl.plot.generic import Style
from raesl.plot.matrix import mdm
from raesl.render.html import tagged
from raesl.render.renderer import LineGen, Renderer


@dataclass
class Figure(Renderer):
    """Figure (image) with optional caption."""

    image: str | Path | go.Figure
    label: str
    width: str | None = None
    height: str | None = None
    caption: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.image, str):
            self.image = Path(self.image)

        self.label = "fig:{}".format(self.label.replace(" ", "-"))

    def gen_typst(self) -> LineGen:
        if isinstance(self.image, Path):
            image = pypst.Image(
                path=str(self.image),
                width=self.width,
                height=self.height,
                alt=pypst.utils.String(self.caption),
            )
        else:
            byte_string = self.image.to_image(format="svg").decode().replace('"', '\\"')
            image = f'#image(bytes("{byte_string}"))'

        yield pypst.Figure(
            image,
            caption=pypst.utils.String(self.caption),
        ).render()
        yield f"<{self.label}>"
        yield ""

    def gen_html(self) -> LineGen:
        if isinstance(self.image, Path):
            image = tagged("img", src=str(self.image), alt=self.caption)
        else:
            image = self.image.to_image(format="svg").decode()
        caption = tagged("figcaption", self.caption)
        yield tagged("figure", [image, caption], **{"class": "figure"})


@dataclass
class Mdm(Renderer):
    """MDM figure."""

    graph: Graph
    depth: int
    node_kinds: list[str] = field(
        default_factory=lambda: ["component", "function_spec"],
    )
    edge_kinds: list[str] = field(
        default_factory=lambda: ["functional_dependency", "mapping_dependency"]
    )
    style: Style = field(
        default_factory=lambda: Style(
            ragraph=dict(
                piemap=dict(
                    display="labels",
                    mode="relative",
                ),
            )
        )
    )
    label: str | None = None

    def __post_init__(self):
        if self.label is None:
            self.label = f"mdm-level-{self.depth}"

    def gen_content(self) -> LineGen:
        logger.debug("Generating MDM for depth {}...".format(self.depth))

        fig = mdm(
            graph=self.graph,
            depth=self.depth,
            node_kinds=self.node_kinds,
            edge_kinds=self.edge_kinds,
            style=self.style,
        )
        caption = self.L10N.dsm_kind_caption(
            kind="-".join(self.spaced(n) for n in self.node_kinds),
            level=self.depth + 1,
        )

        logger.debug("Generated figure! Storing in Renderer...")
        path = self.context.figure_path(f"{self.label}.svg")
        self.context.add_figure(fig, path)

        yield from Figure(self.context, path, caption=caption, label=self.label)
