from collections import defaultdict
from typing import Generator, List

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node

import raesl.doc.lines as lns
from raesl.doc import utils

LineGen = Generator[str, None, None]


def get_comp_node_html_table(node: Node, graph: Graph, node_kinds: List[str]) -> LineGen:
    """Returns a HTML grid table."""
    h = 1
    yield lns.header(h, lns.node_path(node.name), html=True)
    if node.children:
        yield lns.header(h + 2, "sub-components:", html=True)
        yield from lns.unordered([lns.node_path(c.name) for c in node.children], html=True)
    props = utils.get_component_properties(node, graph)
    if props:
        yield lns.header(h + 2, "properties:", html=True)
        yield from lns.unordered([lns.node_path(p.name) for p in props], html=True)

    plain_comments = (
        [("comments", node.annotations.esl_info.get("comments", []))]
        if node.annotations.esl_info.get("comments", [])
        else []
    )

    tagged_comments = list(node.annotations.esl_info["tagged_comments"].items())

    if plain_comments or tagged_comments:
        for key, comments in plain_comments + tagged_comments:
            yield lns.header(h + 2, key, html=True)
            yield " ".join(comments)

    related_nodes_by_kind = defaultdict(list)
    for n in [
        e.target
        for e in graph.edges_from(node)
        if e.kind == "mapping_dependency" and e.target.kind in node_kinds
    ]:
        if n.kind == "function_spec":
            related_nodes_by_kind[n.annotations.esl_info["sub_kind"]].append(n)
        else:
            related_nodes_by_kind[n.kind].append(n)

    if "function_spec" in node_kinds:
        if related_nodes_by_kind.get("goal"):
            yield lns.header(h + 1, "goal function specifications", html=True)
            for g in related_nodes_by_kind.get("goal") or []:
                yield from get_spec_node_html_text(h=h + 2, node=g, graph=graph)

        if related_nodes_by_kind.get("transformation"):
            yield lns.header(h + 1, "Transformation function specifications", html=True)
            for t in related_nodes_by_kind.get("transformation") or []:
                yield from get_spec_node_html_text(h=h + 2, node=t, graph=graph)

    if "behavior_spec" in node_kinds:
        if related_nodes_by_kind.get("behavior_spec", None):
            yield lns.header(h + 1, "behavior specifications", html=True)
            for g in related_nodes_by_kind.get("behavior_spec") or []:
                yield from get_spec_node_html_text(h=h + 2, node=g, graph=graph)

    if "design_spec" in node_kinds:
        if related_nodes_by_kind.get("design_spec", None):
            yield lns.header(h + 1, "design specifications", html=True)
            for g in related_nodes_by_kind.get("design_spec") or []:
                yield from get_spec_node_html_text(h=h + 2, node=g, graph=graph)

    if "need" in node_kinds:
        if related_nodes_by_kind.get("need", None):
            yield lns.header(h + 1, "needs", html=True)
            for g in related_nodes_by_kind.get("need") or []:
                yield from get_spec_node_html_text(h=h + 2, node=g, graph=graph)

    if "relation_spec" in node_kinds:
        if related_nodes_by_kind.get("relation_spec", None):
            yield lns.header(h + 1, "Relations specifications", html=True)
            for r in related_nodes_by_kind.get("relation_spec") or []:
                yield from relation_node_html_table(r=r, g=graph)


def get_spec_node_html_text(h: int, node: Node, graph: Graph) -> LineGen:
    """Yields ESL info belonging to spec node in html format."""

    yield "<ins>"
    yield lns.boldhead(lns.node_path(node.name), html=True)
    yield "</ins>"
    yield "<br>"
    yield from lns.lines(node, graph=graph, html=True)

    sub_nodes = None
    if node.kind == "function_spec":
        if node.annotations.esl_info["sub_kind"]:
            sub_nodes = [
                e.target
                for e in graph.edges
                if e.source is node and e.kind == "traceability_dependency"
            ]

    if sub_nodes:
        yield "<br>"
        yield "<br>"
        yield lns.boldhead("subordinate function specifications:", html=True)
        yield "<br>"
        yield from lns.unordered([lns.node_path(s.name) for s in sub_nodes], html=True)

    plain_comments = (
        [("comments", node.annotations.esl_info.get("comments", []))]
        if node.annotations.esl_info.get("comments", [])
        else []
    )

    tagged_comments = list(node.annotations.esl_info["tagged_comments"].items())

    if plain_comments or tagged_comments:
        if not sub_nodes:
            yield "<br>"
        for key, comments in plain_comments + tagged_comments:
            yield "<br>"
            yield lns.boldhead(text=key, html=True)
            yield "<br>"
            yield " ".join(comments)
            yield "<br>"

    if not sub_nodes and not plain_comments and not tagged_comments:
        yield "<br><br>"
    else:
        yield "<br>"


def get_edge_html_text(h: int, edge: Edge, graph: Graph) -> LineGen:
    """Yields ESL info belonging to an edge."""
    if not edge.annotations.get("esl_info", None):
        yield ""
    elif edge.annotations.esl_info["reason"].get("function_specifications", None):
        yield lns.header(h=h, text="Function specifications", html=True)
        for fname in edge.annotations.esl_info["reason"]["function_specifications"]:
            yield from get_spec_node_html_text(h=h + 1, node=graph[fname], graph=graph)

    elif edge.annotations.esl_info["reason"].get("design_specifications", None):
        yield lns.header(h=h, text="Design specifications", html=True)
        for dname in edge.annotations.esl_info["reason"]["design_specifications"]:
            yield from get_spec_node_html_text(h=h + 1, node=graph[dname], graph=graph)

    elif edge.annotations.esl_info["reason"].get("relation_specifications", None):
        yield lns.header(h=h, text="Relation specifications", html=True)
        for rname in edge.annotations.esl_info["reason"]["relation_specifications"]:
            yield from relation_node_html_table(r=graph[rname], g=graph)

    elif edge.annotations.esl_info["reason"].get("behavior_specifications", None):
        yield lns.header(h=h, text="Behavior specifications", html=True)
        for bname in edge.annotations.esl_info["reason"]["behavior_specifications"]:
            yield from get_spec_node_html_text(h=h + 1, node=graph[bname], graph=graph)
    elif edge.annotations.esl_info["reason"].get("shared_variables", None):
        yield lns.header(h=h, text="Shared variables", html=True)
        for vname in edge.annotations.esl_info["reason"]["shared_variables"]:
            yield lns.node_path(vname)
    else:
        yield ""


def relation_node_html_table(r: Node, g: Graph) -> LineGen:
    ri = r.annotations.esl_info
    yield lns.bold(lns.node_path(r.name), html=True)
    yield "<br>"
    yield lns.bold("model definition name:", html=True)
    yield "<br>"
    yield ri["definition_name"].replace("\n", "")
    yield "<br>"
    if ri.get("required_variables"):
        yield lns.bold("required variables:", html=True)
        yield "<br>"
        yield from lns.unordered(
            [lns.var_path(g[v]).replace("\n", "") for v in ri.get("required_variables")],
            html=True,
        )
    if ri.get("returned_variables"):
        yield lns.bold("returned variables:", html=True)
        yield "<br>"
        yield from lns.unordered(
            [lns.var_path(g[v]).replace("\n", "") for v in ri.get("returned_variables")],
            html=True,
        )
    if ri.get("related_variables"):
        yield lns.bold("related variables:", html=True)
        yield "<br>"
        yield from lns.unordered(
            [lns.var_path(g[v]).replace("\n", "") for v in ri.get("related_variables")],
            html=True,
        )
    yield "<br>"

    plain_comments = (
        [("comments", r.annotations.esl_info.get("comments", []))]
        if r.annotations.esl_info.get("comments", [])
        else []
    )

    tagged_comments = list(r.annotations.esl_info["tagged_comments"].items())

    if plain_comments or tagged_comments:
        for key, comments in plain_comments + tagged_comments:
            yield "<br>"
            yield lns.boldhead(text=key, html=True)
            yield "<br>"
            yield " ".join(comments)
            yield "<br>"
    elif not plain_comments and not tagged_comments:
        yield "<br><br>"
    else:
        yield "<br>"
