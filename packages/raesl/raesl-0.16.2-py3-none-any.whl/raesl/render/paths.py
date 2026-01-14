"""Path rendering for ESL constructs."""

from dataclasses import dataclass
from functools import partial

from ragraph.graph import Graph
from ragraph.node import Node

from raesl.render.context import Context
from raesl.render.elements import Bold, Label, Raw, Reference
from raesl.render.renderer import LineGen, Renderer


@dataclass
class PathDisplay(Renderer):
    """A displayed path, consisting of joined segments."""

    display_segments: list[str]
    """Path segments to display."""

    ref_path: str
    """Original full path reference to use in labels and references."""

    pretty: bool = True
    """Whether to display pretty arrows between path segments."""

    bold: bool = True
    """Whether to generate a bold path."""

    raw: bool = False
    """Whether to display the path as raw/code."""

    label: bool = False
    """Whether to generate a label to link to using the ref_path."""

    link: bool = False
    """Whether this path should link to the ref_path."""

    replace_spaces: bool = True
    """Whether to replace the Renderer.SPACE characters with spaces in the output."""

    def gen_content(self) -> LineGen:
        if self.FORMAT == "typst" and self.pretty and not self.raw:
            char = "#{sym.arrow.r}"
        else:
            char = self.SEPARATOR

        display: str = char.join(self.display_segments)

        if self.replace_spaces:
            display = self.spaced(display)

        if self.raw:
            display = Raw(self.context, display)

        if self.bold:
            display = Bold(self.context, display)

        if self.link:
            yield from Reference(
                self.context, kind="path", label=self.ref_path, display=str(display)
            )
        elif self.label:
            label = Label(self.context, kind="path", label=self.ref_path)
            yield f"{display}{label}"
        else:
            yield str(display)


def path_display(
    context: Context,
    node: Node | str | list[str],
    graph: Graph | None = None,
    parent: Node | str | list[str] | None = None,
    skip_world: bool = True,
    skip_parent_comp: bool = False,
    skip_all: bool = False,
    pretty: bool = False,
    bold: bool = False,
    raw: bool = False,
    label: bool = False,
    link: bool = False,
) -> "PathDisplay":
    """Renderer for any path to display.

    Arguments:
        context: Rendering context containing path splitting options.
        node: Node, reference path (string), or path segments.
        graph: Node lookup graph when figuring out the component split.
        parent: Optional component context node to strip.
        skip_world: Whether to skip the "world" segment.
        skip_parent_comp: Whether to skip all parent component segments.
        skip_all: Whether to skip everything except the last segment.
        bold: Display path as bold.
        raw: Display path as raw/code.
        label: Create a label using the reference path to the node.
        link: Create a link to a label defined elsewhere.
    """
    ref_path, segments = context._ref_path_and_segments(node)

    if skip_all:  # Skip everything except the last segment.
        segments = segments[-1:]
    elif parent or skip_parent_comp:
        # Find the split between component path segments and bundle/var/other indexing.
        comp_split = context._try_component_path_split_with_args(
            ref_path,
            segments,
            node if isinstance(node, Node) else None,
            graph,
        )

        # Check whether the context (i.e. parent component) allows skipping or that the path
        # that is to be displayed needs it's context.
        if parent:
            context_segments = context._path_segments(parent)
            potential_overlap = min(comp_split, len(context_segments), len(segments) - 1)
            if context_segments == segments[:potential_overlap]:
                segments = segments[potential_overlap:]
                comp_split -= potential_overlap

        # Skip component prefix altogether.
        if skip_parent_comp:
            keep_at_least_one = min(comp_split, len(segments) - 1)
            segments = segments[keep_at_least_one:]

    # Check the world skip.
    if not skip_all and skip_world and segments[0] == "world":
        segments = segments[1:]

    return PathDisplay(
        context,
        display_segments=segments,
        ref_path=ref_path,
        pretty=pretty,
        label=label,
        link=link,
        raw=raw,
        bold=bold,
    )


var_path = partial(
    path_display,
    raw=True,
)

pretty_path = partial(
    path_display,
    pretty=True,
    bold=True,
)
