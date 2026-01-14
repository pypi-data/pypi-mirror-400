"""Graphviz diagrams of an ESL specification."""
from typing import Dict, List, Tuple

from graphviz import Digraph
from ragraph.graph import Graph, GraphView
from ragraph.node import Node

from raesl.plot import utils, view_funcs
from raesl.plot.generic import Style


def hierarchy_diagram(
    graph: Graph, roots: List[Node], levels: int, style: Style = Style()
) -> Digraph:
    """Draw a hierarchical decomposition tree using Graphviz.

    Arguments:
        graph: Instantiated ESL graph.
        roots: List of root nodes for which a tree must be drawn.
        levels: Number of levels to include in the tree.
        style: RaESL style options.

    Returns:
        Graphviz Digraph object of the decomposition tree.
    """
    view = GraphView(
        graph=graph,
        view_func=view_funcs.hierarchy,
        view_kwargs={"roots": roots, "levels": levels},
    )

    dot = _draw_migrated_graph(view, view.nodes, style)

    return dot


def functional_dependency_diagram(
    graph: Graph, root: Node, levels: int, style: Style = Style()
) -> Digraph:
    """Draw a functional dependency diagram using Graphviz.

    Arguments:
        graph: Instantiated ESL graph.
        root: Root node for which the dependency structure must be drawn.
        levels: Number of levels to include in the tree.
        style: RaESL style options.

    Returns:
        Graphviz Digraph object of the functional dependency diagram.
    """
    if root.kind != "component":
        raise ValueError(
            "Root node is of kind '{}' while it must be of kind 'component'.".format(root.kind)
        )

    view = GraphView(
        graph,
        view_func=view_funcs.functional_dependency,
        view_kwargs={"root": root, "levels": levels},
    )

    if style.diagram.show_hierarchy:
        roots = [root]
    else:
        roots = [n for n in view.nodes if n.kind == "component"]

    dot = _draw_migrated_graph(view, roots, style)

    return dot


def functional_context_diagram(
    graph: Graph, root: Node, degree: int = 1, style: Style = Style()
) -> Digraph:
    """Draw a functional context diagram using Graphviz.

    Arguments:
        graph: Instantiated ESL graph.
        root: Root node for which the functional context is drawn.
        degree: The degree up to which neighbors must be collected (neighbors of
            neighbors). Defaults to 1.
        style: RaESL style options.

    Returns:
        Graphviz Digraph object of the functional context diagram.
    """
    if root.kind != "component":
        raise ValueError(
            "Root node is of kind '{}' while it must be of kind 'component'.".format(root.kind)
        )

    view = GraphView(
        graph,
        view_func=view_funcs.functional_context,
        view_kwargs={"root": root, "degree": degree, "style": style},
    )

    components = [n for n in view.nodes if n.kind == "component"]
    if style.diagram.show_root_children or style.diagram.show_neighbor_children:
        roots = [c for c in components if c.depth <= root.depth]
        roots.extend([c.parent for c in components if c.parent.depth == root.depth])
    else:
        roots = components

    dot = _draw_migrated_graph(view, roots, style=style)

    return dot


def function_chain_diagram(
    graph: Graph,
    start_points: List[Tuple[Node, List[Node]]],
    end_points: List[Tuple[Node, List[Node]]],
    levels: int = 1,
    style: Style = Style(),
) -> Digraph:
    """Draw a function chain diagram using Graphviz.

    Arguments:
        graph: Instantiated ESL graph.
        start_points: List of tuples that contain the component node and list of
            function nodes that serve as the starting point of the function chains.
        end_points: List of tuples that contain the component node and list of
            function nodes that serve as the end point of the function chains.
        levels: Number of levels to decompose intermediate components into.
            This number is relative to the depth of the start nodes and end nodes.
        style: RaESL style options.

    Returns:
        Graphviz Digraph object of the function chain diagram.
    """
    utils.check_start_and_end_points(start_points=start_points, end_points=end_points)

    view = GraphView(
        graph,
        view_func=view_funcs.function_chain,
        view_kwargs=dict(
            start_points=start_points, end_points=end_points, levels=levels, style=style
        ),
    )

    components = [n for n in view.nodes if n.kind == "component"]
    if style.diagram.show_hierarchy:
        ancestors = set([a for c in components for a in c.ancestors])
        roots = [n for n in ancestors if not n.parent]
    else:
        roots = components

    dot = _draw_migrated_graph(view, roots, style)

    return dot


def function_traceability_diagram(
    graph: Graph, root: Node, levels: int, style: Style = Style()
) -> Digraph:
    """Draw a functional traceability diagram using Graphviz.

    Arguments:
        graph: Instantiated ESL graph.
        root: Node that serves a the root of the traceability tree. Must be a
            transformation specification.
        levels: Number of levels to go down into the traceability tree.
        style: RaESL Style options.

    Returns
        Graphviz Digraph object of the functional traceability diagram.
    """

    # Input checks.
    if root.kind != "function_spec":
        raise ValueError(
            "Root node must be of kind 'function_spec' not of kind '{}'".format(root.kind)
        )

    if root.annotations.esl_info["sub_kind"] != "transformation":
        raise ValueError(
            """Root node must be of sub-kind 'transformation'
            not of sub-kind '{}'""".format(
                root.annotations.esl_info["sub_kind"]
            )
        )

    view = GraphView(
        graph,
        view_func=view_funcs.traceability,
        view_kwargs=dict(root=root, levels=levels, style=style),
    )

    components = [n for n in view.nodes if n.kind == "component"]
    dot = _draw_migrated_graph(view, components, style)

    return dot


def _draw_migrated_graph(
    view: GraphView,
    roots: List[Node],
    style: Style,
) -> Digraph:
    """Get a correctly migrated :obj:`graphviz.Digraph` of a :obj:`Graph`.

    Arguments:
        view: GraphView using one of the ESL filters below.
        roots: List of root nodes.
        style: RaESL style options.
    """
    digraph = Digraph("G", comment=view.name, **style.diagram.digraph)
    digraph.graph_attr["rankdir"] = style.diagram["orientation"]

    trans, goals = utils.get_component_function_dicts(view)
    cmps = set([n for n in view.nodes if n.kind == "component"])
    leafs = {c.name: c for c in cmps if not c.children or not set(c.children).intersection(cmps)}

    for r in roots:
        if r.name in leafs:
            _add_component(digraph, r, trans, goals, style)
        else:
            migrated_goals = []
            for a in r.ancestors:
                migrated_goals.extend(goals.get(a.name, []))

            for goal in migrated_goals:
                _add_goal(digraph, goal, style)

            _add_cluster(digraph, r, leafs, trans, goals, style)

    for e in view.edges:
        src = _get_display_name(e.source, trans, leafs)
        trg = _get_display_name(e.target, trans, leafs)
        digraph.edge(src, trg, style=style.diagram.edge_styles[e.kind])

    return digraph


def _add_component(
    digraph: Digraph,
    node: Node,
    trans: Dict[str, List[Node]],
    goals: Dict[str, List[Node]],
    style: Style,
):
    """Adding a component to a Digraph object. Associated goals
    and transformations are added as well.

    Arguments:
        digraph: Digraph object to add the transformation to.
        node: The component to be added.
        trans: Dictionary of component node names to a lists of transformation
           specifications.
        goals: Dictionary of component node names to lists of goal specifications.
        style: RaESL style options.
    """
    if trans[node.name]:
        with digraph.subgraph(name="cluster_" + node.name) as sg:
            sg.attr(label=node.name)
            for t in trans[node.name]:
                _add_transformation(sg, t, style)
    else:
        digraph.node(
            node.name,
            label=node.name.split(".")[-1].replace("_", " "),
            shape=style.diagram.node_shapes["component"],
        )

    for goal in goals[node.name]:
        _add_goal(digraph, goal, style)


def _add_cluster(
    digraph: Digraph,
    node: Node,
    leafs: Dict[str, Node],
    trans: Dict[str, List[Node]],
    goals: Dict[str, List[Node]],
    style: Style,
):
    """Adding a cluster to a Digraph object. Associated goals are added as well.
    Children are added recursively.

    Arguments:
        digraph: Digraph object to add the transformation to.
        node: The component to be added.
        leafs: Dictionary of leaf node names to leaf nodes.
        trans: Dictionary of component node names to a lists of transformation
           specifications.
        goals: Dictionary of component node names to lists of goal specifications.
        style: RaESL style options.
    """

    with digraph.subgraph(name="cluster_" + node.name) as sd:
        sd.attr(label=node.name)
        for child in node.children:
            if child.name in leafs:
                _add_component(sd, child, trans, goals, style)
            else:
                _add_cluster(sd, child, leafs, trans, goals, style)

    for goal in goals[node.name]:
        _add_goal(digraph, goal, style=style)


def _add_goal(digraph: Digraph, node: Node, style: Style):
    """Adding a goal specification to a Digraph object.

    Arguments:
        digraph: Digraph object to add the goal specification to.
        node: The Node corresponding to the goal specification to be added.
        style: RaESL style options.
    """
    if style.diagram.list_variables:
        label = "\n - ".join(
            [node.name + "\n Variables:"] + node.annotations.esl_info["body"]["variables"]
        )
        digraph.node(
            name=node.name,
            label=label,
            shape=style.diagram.node_shapes["goal"],
        )
    else:
        digraph.node(name=node.name, shape=style.diagram.node_shapes["goal"])


def _add_transformation(digraph: Digraph, trans: Node, style: Style):
    """Adding a transformation specification to a Digraph object.

    Arguments:
        digraph: Digraph object to add the transformation to.
        trans: The Node corresponding to the transformation specification to be added.
        style: RaESL style options.
    """
    if style.diagram.list_variables:
        inputs = "\n -".join(
            ["Input variables:"] + trans.annotations.esl_info["body"]["input_variables"]
        )
        outputs = "\n -".join(
            ["Output variables:"] + trans.annotations.esl_info["body"]["output_variables"]
        )
        label = "\n".join([trans.name, inputs, outputs])
        digraph.node(
            name=trans.name,
            label=label,
            shape=style.diagram.node_shapes["transformation"],
        )
    else:
        digraph.node(trans.name, shape=style.diagram.node_shapes["transformation"])


def _get_display_name(node: Node, trans: Dict[str, List[str]], leafs: Dict[str, Node]) -> str:
    """Get the display name for a Node in the diagram.

    Arguments:
        node: Node to get the display name for.
        trans: Dictionary of component node names to a list of transformation specs.
        leafs: Dictionary of leaf node names to leaf nodes.

    Returns:
        Display name of the Node.

    Note:
        Clusters are prepended with ``cluster_``.
    """
    if _is_clusternode(node, trans, leafs):
        return "cluster_" + node.name

    return node.name


def _is_clusternode(node: Node, trans: Dict[str, List[str]], leafs: Dict[str, Node]):
    """Check whether a Node represents a clusternode in the diagram.

    Arguments:
        node: Node to get the display name for.
        trans: Dictionary of component node names to a list of transformation specs.
        leafs: Dictionary of leaf node names to leaf nodes.

    Returns:
        Whether the Node represents a clusternode in the diagram.
    """
    if node.kind != "component":
        return False

    if node.name not in leafs:
        return True

    if trans.get(node.name):
        return True

    return False
