"""Matrix based views on an ESL specification."""
from typing import List, Optional

import ragraph.plot
from plotly import graph_objs as go
from ragraph.colors import get_categorical
from ragraph.graph import Graph, GraphView
from ragraph.node import Node

from raesl.plot import view_funcs
from raesl.plot.generic import Style


def mdm(
    graph: Graph,
    node_kinds: Optional[List[str]] = None,
    edge_kinds: Optional[List[str]] = None,
    edge_labels: Optional[List[str]] = None,
    edge_weights: Optional[List[str]] = None,
    lead_components: Optional[List[Node]] = None,
    depth: Optional[int] = 2,
    style: Style = Style(),
) -> go.Figure:
    """Create a Multi-Domain Matrix plot using Plotly.

    Arguments:
        node_kinds: The node kinds to display.
        edge_kinds: The edge kinds to display.
        edge_labels: The edge labels to display.
        edge_weights: The edge weights to display.
        lead_components: The lead components to be used in node selection.
        depth: The depth up to which components and related nodes must be included.
        style: RaESL style options.

    Returns:
       Plotly :obj:`go.Figure` object of the Multi-Domain Matrix.
    """
    view = GraphView(
        graph,
        view_func=view_funcs.multi_domain,
        view_kwargs={
            "node_kinds": node_kinds,
            "edge_kinds": edge_kinds,
            "edge_labels": edge_labels,
            "edge_weights": edge_weights,
            "lead_components": lead_components,
            "depth": depth,
        },
    )

    style = style.ragraph
    if style.piemap.display == "labels":
        if not style.piemap.fields:
            style.piemap.fields = edge_labels

        if not style.palettes.get("fields"):
            style.palettes = {
                "fields": {
                    field: color
                    for field, color in zip(
                        graph.edge_labels,
                        get_categorical(n_colors=len(graph.edge_labels)),
                    )
                }
            }

    elif style.piemap.display == "kinds":
        if not style.piemap.fields:
            style.piemap.fields = edge_kinds
    elif style.piemap.display in ["weights", "weight labels"]:
        if not style.piemap.fields:
            style.piemap.fields = edge_weights

    return ragraph.plot.mdm(leafs=view.nodes, edges=view.edges, show=False, style=style, sort=False)
