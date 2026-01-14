"""Generic utility functions."""

import os
import urllib.parse
from collections.abc import Generator
from pathlib import Path
from typing import Any

from ragraph.graph import Graph
from ragraph.node import Node

from raesl import logger
from raesl.types import Location, Position, Range


def path_contents_or_str(input: Path | str | None) -> str | None:
    """Return a file path's contents or the input string (contents) as is."""
    if isinstance(input, Path):
        return input.read_text("utf-8")
    else:
        return input


def get_esl_paths(*paths: str | Path) -> list[Path]:
    """Get a sorted list of ESL file paths from multiple file or directory paths."""
    if not paths:
        raise ValueError("No paths were specified.")

    result: set[Path] = set()

    pathlist = list(paths)
    for path in pathlist:
        logger.debug(f"Resolving '{path}'...")
        if isinstance(path, list):
            pathlist.extend(path)
            continue
        p = Path(path)

        if not p.exists():
            logger.info(f"Skipped '{p}' as it does not exist.")
            continue

        if p.is_dir():
            result.update(
                p for p in p.glob("**/*.esl") if not any(part.startswith(".") for part in p.parts)
            )

        if p.is_file():
            result.add(p)

    if not result:
        raise ValueError("No ESL files found.")

    return sorted(result)


def check_output_file_path(fpath: str | Path, force: bool) -> Path:
    """Check output filepath versus force overwrite status."""
    p = Path(fpath)

    if p.exists() and not force:
        raise ValueError(f"Path {p} already exists and force overwrite isn't set.")

    if p.is_dir():
        raise ValueError(f"Path {p} is a directory.")

    return p


def get_location(
    uri: str = "Unknown",
    start_line: int = 0,
    start_character: int = 0,
    end_line: int | None = None,
    end_character: int | None = None,
) -> Location:
    """Generation utility to quickly drum up a location.

    Arguments:
        uri: Location uri.
        start_line: Location's range start line.
        start_character: Location's range start offset.
        end_line: Optional Location's range end line (otherwise identical to start.)
        end_character: Optional Location's range end offset (otherwise identical to
            start.)

    Returns:
        Newly created location instance.
    """
    end_line = start_line if end_line is None else end_line
    end_character = start_character if end_character is None else end_character

    return Location(
        uri,
        Range(Position(start_line, start_character), Position(end_line, end_character)),
    )


def cleanup_path(path: str | Path) -> Path:
    """Cleanup pathname for some typical mistakes."""
    p = str(path)
    result = uri_to_path(p)
    return result


def uri_to_path(uri: str) -> Path:
    """Convert a file URI to a regular path."""
    parsed = urllib.parse.unquote(urllib.parse.urlparse(uri).path)

    if os.name == "nt" and parsed.startswith("/"):
        parsed = parsed[1:]

    return Path(parsed)


def path_to_uri(path: str | Path) -> str:
    """Convert a path to a file URI."""
    if str(path).startswith("file:"):
        return str(path)
    return Path(path).resolve().as_uri()


def split_first_dot(name: str) -> tuple[str, str, int]:
    """Split the provided name on the first dot if it exists, return both parts, and
    the length of the dot.
    """
    i = name.find(".")
    if i >= 0:
        return name[:i], name[i + 1 :], 1
    else:
        return name, "", 0


def get_first_namepart(name: str) -> str:
    """Return the name upto and excluding the first dot."""
    i = name.find(".")
    if i < 0:
        return name
    return name[:i]


def get_scoped_nodes(graph: Graph, scopes: dict[str, int | None]) -> list[Node]:
    """Get scoped nodes, being subtrees of the graph of varying depth.

    Arguments:
        graph: Graph data.
        scopes: Node names mapped to depths of the subtree to include. A depth of
            :obj:`None` includes the whole subtree starting at that node.

    Returns:
        List of nodes in all given scopes.
    """
    seen: set[str] = set()
    nodes = []

    for name, depth in scopes.items():
        try:
            node = graph[name]
        except KeyError:
            raise KeyError(
                f"Node '{name}' does not exist in the graph. "
                "Make sure you provide the entire instantiated path "
                "(e.g. 'world.component.subcomponent')."
            )

        for candidate in yield_subtree(node, depth):
            if candidate.name in seen:
                continue
            nodes.append(candidate)

    return nodes


def yield_subtree(root: Node, depth: int | None) -> Generator[Node, None, None]:
    """Yield nodes from a given subtree starting at Node and with given depth.

    Arguments:
        root: Root node of subtree.
        depth: Depth of subtree. If None, defaults to full depth.

    Yields:
        Nodes in the subtree.
    """
    yield root

    if depth is None or depth > 0:
        for c in root.children:
            yield from yield_subtree(c, None if depth is None else depth - 1)


def cap(text: str) -> str:
    """Capitalize first char of text while leaving the rest untouched."""
    return text[0].upper() + text[1:]


def is_subpath(partial: list[Any], reference: list[Any]) -> int | None:
    """Check if a partial path is anywhere in the reference. Returns the starting integer if so."""
    if not partial:
        return None
    chunk = len(partial)
    walk = max(0, len(reference) - len(partial) + 1)
    for i in range(walk):
        if partial == reference[i : i + chunk]:
            return i
    return None


def is_number(v: Any) -> bool:
    """Check whether something can be converted to a float."""
    try:
        float(v)
        return True
    except ValueError:
        return False


def get_design_rule_line_vars(rules: list[dict[str, Any]], g: Graph) -> list[dict[str, Any]]:
    """Get variables that are used within a design rule line"""
    vrs = [
        g[r["subject"]]
        for r in rules
        if g[r["subject"]].annotations.esl_info.get("bundle_root_name")
    ]

    vrs += [
        g[r["bound"]["value"]]
        for r in rules
        if (
            r["comparison"] not in ["minimized", "maximized"]
            and g.node_dict.get(r["bound"]["value"], None)
        )
        and g[r["bound"]["value"]].annotations.esl_info.get("bundle_root_name")
    ]

    return vrs


def get_component_goals(
    component: Node, graph: Graph, constraint: bool = True, inherited: bool = True
) -> list[Node]:
    """Get relevant goal requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    ancestors = set([a.name for a in component.ancestors]) if inherited else set()
    goals = [
        n
        for n in graph.nodes
        if n.kind == "function_spec"
        and n.annotations.esl_info.get("sub_kind") == "goal"
        and n.annotations.esl_info.get("form") == form
        and (
            n.annotations.esl_info["body"].get("active") in ancestors
            if inherited
            else n.annotations.esl_info["body"].get("active") == component.name
        )
        and [e for e in graph.edges_between(component, n) if e.kind == "mapping_dependency"]
    ]
    return goals


def get_component_transformations(
    component: Node, graph: Graph, constraint: bool = True
) -> list[Node]:
    """Get relevant transformation requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    transformations = [
        n
        for n in graph.nodes
        if n.kind == "function_spec"
        and n.annotations.esl_info.get("sub_kind") == "transformation"
        and n.annotations.esl_info["body"].get("active") == component.name
        and n.annotations.esl_info.get("form") == form
    ]
    return transformations


def get_component_behaviors(component: Node, graph: Graph, constraint: bool = True) -> list[Node]:
    """Get relevant behavior requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"

    shared_flow_behaviors = [
        b
        for b in graph.targets_of(component)
        if b.kind == "behavior_spec" and b.annotations.esl_info.get("form") == form
    ]

    unlinked_child_behaviors = [
        b
        for b in graph.nodes
        if b.kind == "behavior_spec"
        and b.annotations.esl_info.get("form") == form
        and b.name.split(".")[:-1] == component.name.split(".")
        and not any(comp for comp in graph.sources_of(b) if comp.kind == "component")
    ]

    return shared_flow_behaviors + unlinked_child_behaviors


def get_component_designs(component: Node, graph: Graph, constraint: bool = True) -> list[Node]:
    """Get relevant design requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    return [
        d
        for d in graph.targets_of(component)
        if d.kind == "design_spec" and d.annotations.esl_info.get("form") == form
    ]


def get_global_designs(graph: Graph, constraint: bool = True) -> list[Node]:
    """Get globally relevant design requirments or constraints."""
    form = "constraint" if constraint else "requirement"
    dc_dict = {}
    for e in graph.edges:
        if e.source.kind != "component":
            continue
        dc_dict[e.target.name] = e.source.name

    drs = [
        d
        for d in graph.nodes
        if d.kind == "design_spec"
        and d.annotations.esl_info.get("form") == form
        and d.name not in dc_dict
    ]

    return drs


def get_component_needs(component: Node, graph: Graph) -> list[Node]:
    """Get relevant needs for a component."""
    subjects = set([n.name for n in graph.targets_of(component) if n.kind != "component"])
    subjects.add(component.name)
    return [
        n for n in graph.nodes if n.kind == "need" and n.annotations.esl_info["subject"] in subjects
    ]


def get_global_needs(graph: Graph) -> list[Node]:
    """Get globally relevant needs."""
    sc_dict = {}
    for e in graph.edges:
        if e.source.kind != "component":
            continue
        sc_dict[e.target.name] = e.source.name

    all_needs = graph.get_nodes_by_kind("need")

    def get_subject(need):
        return need.annotations.esl_info["subject"]

    return [
        need
        for need in all_needs
        if get_subject(need) not in sc_dict and graph[get_subject(need)].kind != "component"
    ]


def get_node_comments(component: Node) -> list[str]:
    """Get the plain comments from a component node."""

    return component.annotations.esl_info.get("comments", [])


def get_node_tagged_comments(component: Node) -> dict[str, str | list[str]]:
    """Get the tagged comments from a component node."""
    return component.annotations.esl_info.get("tagged_comments", dict())


def get_component_properties(component: Node, graph: Graph) -> list[Node]:
    """Get relevant properties for a component."""
    return [graph[prop] for prop in component.annotations.esl_info.get("property_variables", [])]


def get_component_relations(component: Node, graph: Graph) -> list[Node]:
    """Get relevant relations for a component."""
    return [n for n in graph.nodes if n.kind == "relation_spec" and graph[component.name, n.name]]
