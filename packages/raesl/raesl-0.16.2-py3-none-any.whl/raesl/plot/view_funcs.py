"""GraphView view functions for ESL."""

from copy import deepcopy
from typing import List, Optional, Tuple

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node

from raesl.plot import utils
from raesl.plot.generic import Style


def multi_domain(
    graph: Graph,
    node_kinds: Optional[List[str]] = None,
    edge_kinds: Optional[List[str]] = None,
    edge_labels: Optional[List[str]] = None,
    edge_weights: Optional[List[str]] = None,
    lead_components: Optional[List[Node]] = None,
    depth: int = 2,
) -> Tuple[List[Node], List[Edge]]:
    """Create multi-domain-matrix visualization based on an ESL derived graph.

    Arguments:
        graph: Input graph object derived from an ESL specification.
        node_kinds: The node kinds that are included in the plot. Defaults to all
            node_kinds present within the graph.
        edge_kinds: The edge kinds that are included in the plot. Defaults to all
            edge_kinds present within the graph.
        edge_labels: The edge labels that are shown in the plot. Defaults to all
            edge_labels present within the graph.
        edge_weights: The edge weight types that are shown in the plot. Defaults to a
            single random edge weight present within the graph.
        lead_components: The lead components to be used to select other nodes.
        depth: Depth up to which lead components must be selected if no lead components
            are provided.

    Returns:
        Node list and Edge list.
    """

    if lead_components:
        utils.check_tree_disjunction(nodes=lead_components)
    else:
        lead_components = list(
            utils.get_up_to_depth(
                roots=[r for r in graph.roots if r.kind == "component"], depth=depth
            )
        )

    node_kinds = graph.node_kinds if node_kinds is None else node_kinds
    edge_kinds = graph.edge_kinds if edge_kinds is None else edge_kinds
    edge_labels = graph.edge_labels if edge_labels is None else edge_labels
    edge_weights = graph.edge_weight_labels if edge_weights is None else edge_weights

    nodes = utils.filter_nodes(graph, lead_components=lead_components, node_kinds=node_kinds)

    edges = [
        e for e in graph.edges_between_all(sources=nodes, targets=nodes) if e.kind in edge_kinds
    ]

    # Ensure that mapping dependencies appear below the diagonal.
    n2n = {kind: idx for idx, kind in enumerate(node_kinds)}
    modified_edges = []
    added_edges = []
    for e in edges:
        if e.kind != "mapping_dependency":
            continue
        if n2n[e.source.kind] > n2n[e.target.kind]:
            modified_edges.append(e)
            modified_edge = deepcopy(e)
            modified_edge.source = graph[e.source.name]
            modified_edge.target = graph[e.target.name]
            added_edges.append(modified_edge)

    for e in modified_edges:
        edges.remove(e)

    edges += added_edges

    if "variable" in node_kinds and "functional_dependency" in edge_kinds:
        edges += utils.migrate_edges_between_variables(graph, lead_components=lead_components)

    return nodes, edges


def hierarchy(graph: Graph, roots: List[Node], levels: int) -> Tuple[List[Node], List[Edge]]:
    """Filter nodes and create edges for drawing a hierarchical decomposition diagram.

    Arguments:
       graph: Source data graph.
       roots: Roots of the hierarchical diagram.
       levels: Number of levels to include in the diagram.

    Returns:
        List of selected nodes and list of created edges.
    """

    nodes, edges = [], []
    for r in roots:
        max_depth = r.depth + levels - 1
        nodes.append(r)
        crawled_nodes, crawled_edges = utils.crawl_descendants(r, max_depth)
        nodes.extend(crawled_nodes)
        edges.extend(crawled_edges)

    # Create nodes in which hierarchy information is stripped to prevent
    # nested plotting.
    stripped_nodes = []
    for node in nodes:
        copied_node = deepcopy(node)
        copied_node.parent = None
        copied_node.children = None
        stripped_nodes.append(copied_node)

    # Modify source and targets of edges to stripped nodes.
    node_dict = {n.name: n for n in stripped_nodes}
    for e in edges:
        e.source = node_dict[e.source.name]
        e.target = node_dict[e.target.name]

    return stripped_nodes, edges


def functional_dependency(graph: Graph, root: Node, levels: int) -> Tuple[List[Node], List[Node]]:
    """Filter method for drawing a nested functional dependency structure.

    Arguments
        graph: Instantiated ESL graph.
        root: Root node for which the dependency structure must be drawn.
        levels: Number of levels to include in the tree.

    Returns:
       List of nodes and edges to be displayed.

    Note:
       This method assumes that the data source graph is generated from an
       ESL specification.
    """

    components = list(utils.get_up_to_depth(roots=[root], depth=root.depth + levels))

    functions, edges = multi_domain(
        graph,
        node_kinds=["function_spec"],
        edge_kinds=["functional_dependency", "logical_dependency"],
        lead_components=components,
    )

    # Add dependencies between goals and components that cannot be traced down to
    # transformations.
    tree = sorted(
        set([a.name for c in components for a in c.ancestors]).union(
            set([c.name for c in components])
        )
    )
    edges += _add_component_goal_edges(graph, tree, functions)

    return components + functions, edges


def traceability(
    graph: Graph, root: Node, levels: int, style: Style = Style()
) -> Tuple[List[Node], List[Edge]]:
    """Filter nodes and edges for drawing a traceability diagram.

    Arguments:
        graph: Instantiated ESL graph.
        root: The root transformation specification.
        levels: Number of levels to include in the traceability diagram.
        style: RaESL style options.

    Returns:
        List of selected nodes and list of selected edges.
    """
    # Get functions in tree and traceability edges.
    g = deepcopy(graph)
    functions, edges = utils.get_function_tree(g, root, levels)

    components = [c for c in set([g[f.annotations.esl_info["body"]["active"]] for f in functions])]

    # Remove component hierarchy to make traceability hierarchy leading.
    for c in components:
        c.parent = None
        c.children = []

    if style.diagram.show_function_dependencies:
        edges.update(
            set(
                [
                    e
                    for e in g.edges_between_all(functions, functions)
                    if e.kind in ["functional_dependency", "logical_dependency"]
                ]
            )
        )

    return components + list(functions), list(edges)


def function_chain(
    graph: Graph,
    start_points: List[Tuple[Node, List[Node]]],
    end_points: List[Tuple[Node, List[Node]]],
    levels: int = 1,
    style: Style = Style(),
) -> Tuple[List[Node], List[Edge]]:
    """Filter nodes and edges for a function chain diagram.

    Arguments:
        graph: Instantiated ESL graph.
        start_points: List of start-points for the function chains.
        end_points: List of end-points for the function chains.
        levels: Number of levels to decompose intermediate components into (if present).
        style: style options class.

    Returns:
        List of selected nodes and list of selected edges.
    """
    components = set(
        utils.select_components_for_function_path(
            graph, start_points=start_points, end_points=end_points, levels=levels
        )
    )

    _, edges = multi_domain(
        graph,
        node_kinds=["function_spec"],
        edge_kinds=["functional_dependency", "logical_dependency"],
        lead_components=list(components),
    )

    sfs = []
    for p in start_points:
        sfs.extend(p[1])
    efs = []
    for p in end_points:
        efs.extend(p[1])

    path_functions = set()
    path_components = set()
    migrated_goals = []

    for path in utils.get_paths_between_all(sfs, efs, edges=edges):
        for fname in path:
            f = graph[fname]
            path_functions.add(f)
            active = graph[f.annotations.esl_info["body"]["active"]]
            if active in components:
                path_components.add(active)
            else:
                des = components.intersection(set(active.descendants))
                migrated_goals.append(f)
                for d in des:
                    if graph.edge_dict.get(d.name):
                        if graph.edge_dict[d.name].get(f.name):
                            path_components.add(d)

    sliced = graph.get_graph_slice(nodes=path_components.union(path_functions))

    if style.diagram.show_hierarchy:
        utils.rebuild_hierarchical_structure(graph, sliced)

    return sliced.leafs, [
        e
        for e in sliced.edges
        if e.source.kind == "function_spec" and e.target.kind == "function_spec"
    ]


def functional_context(
    graph: Graph, root: Node, degree: int, style: Style = Style()
) -> Tuple[List[Node], List[Edge]]:
    """Filter nodes and edges for drawing a functional context diagram.

    Arguments:
        graph: Instantiated ESL graph.
        root: The root node for which the functional context diagram must be
            drawn.
        degree: Degree up to which neighbors of neighbors must be sought.
        style: RaESL style options.

    Returns:
        List of selected nodes and list of selected edges.
    """
    neighbors = utils.get_neighbors(graph, root, root, node_kinds={"component"}, degree=degree)

    components = []
    tree = set()
    tree.add(root.name)
    if style.diagram.show_root_children and root.children:
        components.extend(root.children)
        tree.update(set([c.name for c in root.children]))
    else:
        components.append(root)

    tree.update(set([n.name for n in neighbors]))
    if style.diagram.show_neighbor_children:
        for neighbor in neighbors:
            if neighbor.children:
                components.extend(neighbor.children)
                tree.update(set([c.name for c in neighbor.children]))
            else:
                components.append(neighbor)
    else:
        components.extend(neighbors)

    functions, edges = multi_domain(
        graph,
        node_kinds=["function_spec"],
        edge_kinds=["functional_dependency", "logical_dependency"],
        lead_components=components,
    )

    edges += _add_component_goal_edges(graph, sorted(tree), functions)

    return components + functions, edges


def _add_component_goal_edges(graph: Graph, tree: List[Node], functions: List[Node]) -> List[Edge]:
    """Create edges between component or cluster nodes if a goal cannot be related
    to a transformation:

    Arguments:
        graph: Instantiated ESL graph.
        tree: List of components that are within the (sub)tree that is plotted.
        functions: List of function specs that is plotted.

    Returns:
        List of edges.
    """
    edges = []
    goals = [f for f in functions if f.annotations.esl_info["sub_kind"] == "goal"]
    transformations = [
        f for f in functions if f.annotations.esl_info["sub_kind"] == "transformation"
    ]
    for goal in goals:
        if (
            not list(graph.edges_between_all(sources=[goal], targets=transformations))
            and goal.annotations.esl_info["body"]["passive"] in tree
        ):
            # No destination transformation is found. Add edge to destination component
            # if the destination component is part of the selected components.
            for e in graph.directed_edges[goal.annotations.esl_info["body"]["passive"]][goal.name]:
                edges.append(
                    Edge(
                        source=e.target,
                        target=e.source,
                        kind=e.kind,
                        labels=e.labels,
                        weights=e.weights,
                        annotations=e.annotations,
                    )
                )

        if (
            not list(graph.edges_between_all(sources=transformations, targets=[goal]))
            and goal.annotations.esl_info["body"]["active"] in tree
        ):
            # No source transformation is found. Add edge from to source component.
            edges.extend(
                graph.directed_edges[goal.annotations.esl_info["body"]["active"]][goal.name]
            )

    return edges
