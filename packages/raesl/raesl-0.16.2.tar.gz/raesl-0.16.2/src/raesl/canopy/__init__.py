"""Module to ESL derived graph to a graph suitable for exporting to Canopy."""

from ragraph.graph import Graph

from raesl.canopy.html import get_comp_node_html_table, get_edge_html_text, get_spec_node_html_text

DEFAULT_NODE_KINDS: list[str] = [
    "component",
    "function_spec",
    "behavior_spec",
    "design_spec",
    "need",
    "relation_spec",
    "variable",
]

DEFAULT_EDGE_KINDS: list[str] = [
    "functional_dependency",
    "logical_dependency",
    "design_dependency",
    "coordination_dependency",
    "mapping_dependency",
    "traceability_dependency",
]


def add_canopy_annotations(
    graph: Graph,
    node_kinds: list[str] | None = None,
    edge_kinds: list[str] | None = None,
):
    """Convert ESL derived graph to a graph suitable for exporting to Canopy.

    Arguments:
        graph: Graph to be converted
        node_kinds: List of node kinds to be considered in conversion.
        edge_kinds: List of edge kinds to be considered in conversion.

    Returns
        Converted graph object.
    """
    node_kinds = node_kinds or DEFAULT_NODE_KINDS.copy()
    edge_kinds = edge_kinds or DEFAULT_EDGE_KINDS.copy()
    for k in node_kinds:
        for n in graph.get_nodes_by_kind(k):
            if k == "component" and n.name != "world":
                n.annotations.canopy = " ".join(
                    [
                        html
                        for html in get_comp_node_html_table(
                            node=n, graph=graph, node_kinds=node_kinds
                        )
                    ]
                )

            if k in {"function_spec", "design_spec", "behavior_spec", "need"}:
                n.annotations.canopy = " ".join(
                    [html for html in get_spec_node_html_text(h=1, node=n, graph=graph)]
                )

    for k in edge_kinds:
        for e in graph.get_edges_by_kind(k):
            e.annotations.canopy = " ".join(
                [html for html in get_edge_html_text(h=1, edge=e, graph=graph)]
            )
