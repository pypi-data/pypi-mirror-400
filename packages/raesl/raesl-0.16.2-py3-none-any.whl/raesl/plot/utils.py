"""RaESL plotting utility functions."""

from collections import defaultdict
from copy import deepcopy
from typing import Dict, Generator, List, Set, Tuple

from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node
from ragraph.plot.utils import get_axis_sequence


def get_component_function_dicts(
    graph: Graph,
) -> Tuple[Dict[str, List[Node]], Dict[str, List[Node]]]:
    """Get two dictionaries from component node names to lists of transformation and
    goal function nodes.

    Arguments
       graph: Instantiated ESL graph.

    Returns
       Dictionaries from component node names to transformation and goal function nodes.
    """
    trans = defaultdict(list)
    goals = defaultdict(list)
    for f in graph.get_nodes_by_kind(kind="function_spec"):
        if f.annotations.esl_info["sub_kind"] == "transformation":
            trans[f.annotations.esl_info["body"]["active"]].append(f)
        elif f.annotations.esl_info["sub_kind"] == "goal":
            goals[f.annotations.esl_info["body"]["active"]].append(f)

    return trans, goals


def crawl_descendants(node: Node, max_depth: int) -> Tuple[List[Node], List[Edge]]:
    """Walk down the decomposition tree of a node, add its children and create
    composition dependencies accordingly.

    Arguments:
        node: The parent node to unfold.
        max_depth: Max depth to unfold nodes to (absolute depth w.r.t. root).

    Returns:
        List of (additionally) crawled nodes and "composition_dependency" edges.

    Note:
        Since we explicitly need to figure out which (partial) hierarchies to display
        using Graphviz, we recreate those parts of the hierarchy using explicit
        "composition dependency" :obj:`Edge` objects in the preprocessing step using
        :obj:`ragraph.graph.GraphView` objects.
    """
    nodes, edges = [], []

    for child in node.children:
        nodes.append(child)
        edges.append(Edge(node, child, kind="composition_dependency"))

        if child.children and child.depth < max_depth:
            cnodes, cedges = crawl_descendants(child, max_depth)
            nodes.extend(cnodes)
            edges.extend(cedges)

    return nodes, edges


def get_neighbors(
    graph: Graph, root: Node, node: Node, node_kinds: Set[str], degree: int = 1
) -> Set[Node]:
    """Get neighbors of a node within the graph.

    Arguments:
        graph: Instantiated ESL graph.
        root: The root node for which the nodes must be sought up to the given degree.
        node: The node for which the direct neighbors must be collected.
        node_kinds: The kinds of the neighbor nodes that must be collected.
        degree: The degree up to which neighbors must be collected (neighbors of
            neighbors). Defaults to 1.

    Returns
        Set of neighbors.
    """

    neighbors = set(
        [
            neighbor
            for neighbor in list(graph.targets_of(node)) + list(graph.sources_of(node))
            if (
                neighbor.kind in node_kinds
                and (
                    neighbor.depth == root.depth
                    or (neighbor.depth < root.depth and not neighbor.children)
                )
            )
        ]
    )

    if degree == 1:
        # Stop searching further.
        return neighbors

    for neighbor in neighbors:
        neighbors = neighbors.union(
            get_neighbors(graph, root, neighbor, node_kinds, degree=degree - 1)
        )

    return neighbors


def get_paths_between_all(
    sources: List[Node], targets: List[Node], edges: List[Edge]
) -> List[List[str]]:
    """Compute paths between nodes. Based on depth first search.

    Arguments:
         sources: List of starting nodes of paths.
         targets: Set of ending nodes of path.
         edges: List of edges between nodes.

    Yields:
        List of lists of node names.
    """
    paths = []

    ed: Dict[str, Dict[str, Edge]] = defaultdict(dict)
    for e in edges:
        ed[e.source][e.target] = e

    for source in sources:
        paths.extend(get_paths(source, ed, set(targets), visited=[source.name]))

    return paths


def get_paths(
    source: Node,
    edges: Dict[Node, Dict[Node, Edge]],
    targets: Set[Node],
    visited: List[Node] = [],
) -> List[List[str]]:
    """Collection all paths (list of node names) between the source node and the set of
    target nodes.

    Arguments:
        source: The source node where all paths should start.
        edges: Dictionary of Node to Node to Edge. Contains the edges to be
            considered when searching for paths.
        targets: Set of node where the paths should end.
        visited: List of nodes already visited. Required to prevent running in cycles.

    Returns:
        List of lists of node names.
    """
    paths: List[List[str]] = []
    steps = edges.get(source)
    if not steps:
        return paths

    for target in steps:
        if target.name in visited:
            # node has already been visited. Loop entered.
            continue
        elif target in targets:
            # A target has been reached
            visited.append(target.name)
            paths.append(visited)
        else:
            new_path = deepcopy(visited)
            new_path.append(target.name)
            paths.extend(get_paths(target, edges, targets, visited=new_path))

    return paths


def select_components_for_function_path(
    graph: Graph,
    start_points: List[Tuple[Node, List[Node]]],
    end_points: List[Tuple[Node, List[Node]]],
    levels: int,
) -> List[Node]:
    """Select components that belong to a certain level within the decomposition
    structure to draw a functional path.

    Arguments:
        graph: Instantiated ESL graph.
        start_points: List of tuples that contain the component node and list of
            function nodes that serve as a starting point of the function chains.
        end_points: List of Tuples that contain the component node and list of functions
            that nodes server.
        levels: Number of levels to decompose intermediate components into.
            This number is relative to the maximum of the depth of the start
            node and end node.

    Note:
       Components that are a descendant of the start or end component node of the
       function path are excluded.
    """
    start_comps = [p[0] for p in start_points]
    end_comps = [p[0] for p in end_points]
    level = max([n.depth for n in start_comps + end_comps]) + levels - 1
    start_descendants = get_all_descendants(start_comps)
    end_descendants = get_all_descendants(end_comps)
    components = []

    for c in graph.get_nodes_by_kind(kind="component"):
        if c in start_descendants or c in end_descendants or c.depth > level:
            continue
        elif c.depth == level or (c.depth < level and not c.children):
            components.append(c)

    return components


def add_level(graph: Graph, sliced: Graph, parents: Set[Node]):
    """Add a level to the sliced graph based on the hierarchy in the source graph.

    Arguments:
        graph: Instantiated ESL graph.
        sliced: Sliced data graph.

    Note:
        Creates deepcopies of child nodes to preserve the original data structure.
    """
    comp_names = set([c.name for c in sliced.get_nodes_by_kind(kind="component")])

    for p in parents:
        children = comp_names.intersection(set([child.name for child in p.children]))
        if children:
            n = deepcopy(p)
            n.children = [sliced[child] for child in children]
            sliced.add_node(n)


def rebuild_hierarchical_structure(graph: Graph, sliced: Graph):
    """Rebuilding the hierarchical structure within the sliced graph.

    Arguments:
        graph: Instantiated ESL graph.
        sliced: Sliced data graph.

    Note:
        Creates deepcopies of child nodes to preserve the original data structure.
    """
    components = sliced.get_nodes_by_kind(kind="component")
    depth = max([graph[c.name].depth for c in components]) if components else 0
    parents = set(
        [
            graph[c.name].parent
            for c in components
            if graph[c.name].parent is not None and graph[c.name].parent.depth == depth - 1
        ]
    )

    while parents:
        add_level(graph, sliced, parents=parents)
        depth -= 1
        comps = sliced.get_nodes_by_kind(kind="component")
        parents = set(
            [
                graph[c.name].parent
                for c in comps
                if graph[c.name].parent is not None and graph[c.name].parent.depth == depth - 1
            ]
        )


def get_all_descendants(nodes: List[Node]) -> Set[Node]:
    """Get all descendants from a list of provided nodes.

    Arguments:
        nodes: List of nodes for which the descendants must be found.

    Returns:
        Set of nodes containing all descendants of the provided nodes.
    """
    all_descendants: Set[Node] = set()
    for n in nodes:
        all_descendants.union(set(n.descendants))

    return all_descendants


def check_comp_func_pairs(points: List[Tuple[Node, List[Node]]]):
    """Check of for all points the provided components functions pairs are consistent.

    Arguments:
        points: List of points for which the consistency must be checked.

    Raises:
        ValueError: If the active component of the given functions does not match.
    """
    for point in points:
        comp = point[0]
        functions = point[1]
        for f in functions:
            if comp.name != f.annotations.esl_info["body"]["active"]:
                msg = "Active component of '{}' is not equal to start component '{}'."
                raise ValueError(msg.format(comp.name, f.annotations.esl_info["body"]["active"]))


def check_tree_disjunction(nodes: List[Node]):
    """Check if list of nodes are not part of each others descendants.

    Raises:
        ValueError: If node is in the descendants of another node that was provided.
    """
    decendants = get_all_descendants(nodes)
    for n in nodes:
        if n in decendants:
            raise ValueError("Node {} is a descendant of another provided node.".format(n.name))


def check_start_and_end_points(
    start_points: List[Tuple[Node, List[Node]]],
    end_points: List[Tuple[Node, List[Node]]],
):
    """Check start and end points for consistency.

    Arguments:
        start_points: List of tuples that contain the component node and list of
            function nodes that serve as starting points of the function chains.
        end_points: List of tuples that contain the component node and list of
            functions nodes that serve as end points of the function chains.

    Raises:
        ValueError: If the component-function pairs do not have a corresponding active
            component.
        ValueError: If any of the components are a descendant of another component.
    """
    points = start_points + end_points
    check_comp_func_pairs(points)
    check_tree_disjunction([p[0] for p in points])


def get_function_tree(graph: Graph, node: Node, levels: int) -> Tuple[Set[Node], Set[Edge]]:
    """Walk down the traceability tree of a node.

    Arguments:
        graph: Instantiated ESL graph.
        node: Node to start the walk from.
        levels: Number of levels to continue walking.

    Returns:
        Tuple of the set of all nodes and the set of all edges that describe the
        traceability tree.

    """
    edges = set()
    functions = set()
    functions.add(node)

    if levels > 1:
        edges.update(
            set([e for e in graph.edges_from(node) if e.kind == "traceability_dependency"])
        )

        function_targets = set([e.target for e in edges])
        functions.update(function_targets)
        for f in function_targets:
            if f.annotations.esl_info["sub_kind"] == "goal":
                continue

            fs, es = get_function_tree(graph, f, levels - 1)

            edges.update(es)
            functions.update(fs)

    return functions, edges


def migrate_edges_between_variables(graph: Graph, lead_components: List[Node]) -> List[Edge]:
    """Migrate edges between variables up into the decomposition tree.

    Arguments:
        graph: Instantiated ESL graph.
        lead_components: The components that are displayed.

    Returns:
        List of edges to are created for the specific view.

    Note:
        The ESL compiler only adds functional dependencies between variables based on
        the transformation specs of leaf components. As such, when one displays
        components at higher hierarchical levels gaps appear in the variable dependency
        structure. Hence, this method is used to fill those gaps by adding additional
        edges.
    """
    edges = []
    for c in lead_components:
        if not c.children:
            continue
        # Component is a collapsed component so get transformation specs and add
        # dependencies between in and output variables.
        tfs = [
            n
            for n in graph.targets_of(c)
            if n.kind == "function_spec" and n.annotations.esl_info["sub_kind"] == "transformation"
        ]
        for t in tfs:
            for vi in t.annotations.esl_info["body"]["input_variables"]:
                for vj in t.annotations.esl_info["body"]["output_variables"]:
                    edges.append(
                        Edge(
                            source=graph[vi],
                            target=graph[vj],
                            labels=[graph[vi].annotations.esl_info["type_ref"]],
                            kind="functional_dependency",
                            annotations=dict(esl_info=dict(reason=dict(transformations=[t.name]))),
                        )
                    )
    return edges


def has_mapping_dependency(graph: Graph, node: Node, nodes: List[Node]) -> bool:
    """Check if a node is mapped to any node in a list of nodes.

    Arguments:
        graph: Instantiated ESL graph.
        node: The node for which the existence of mapping dependencies must be checked.
        nodes: List of nodes which are to be considered for checking the existence
            of a mapping dependency.

    Returns:
        Bool that indicates if a mapping dependency exists.
    """
    return any(
        True for e in graph.edges_between_all(nodes, [node]) if e.kind == "mapping_dependency"
    ) or any(True for e in graph.edges_between_all([node], nodes) if e.kind == "mapping_dependency")


def filter_nodes(graph: Graph, lead_components: List[Node], node_kinds: List[str]) -> List[Node]:
    """Filter nodes for displaying a multi-domain-matrix.

    Arguments:
        graph: Instantiated ESL graph.
        lead_components: List of nodes of kind 'component' that are leading
            when filtering the other nodes.
        node_kinds: List of node kinds to be included.

    Returns:
        List of filtered nodes.

    Note:
        Node of kind 'component' are always leading in filtering the nodes to ensure the consistency
        within the network of shown dependencies. Since the component hierarchy forms the central
        structure of an ESL specification.
    """
    nodes = []
    for kind in node_kinds:
        if kind == "component":
            nodes.extend(lead_components)
        else:
            domain_nodes = []
            for n in graph.get_nodes_by_kind(kind=kind):
                if has_mapping_dependency(graph, n, lead_components + nodes):
                    domain_nodes.append(n)

            nodes.extend(get_axis_sequence(nodes=domain_nodes, kinds=[kind]))

    return nodes


def get_up_to_depth(roots: List[Node], depth: int) -> Generator[Node, None, None]:
    """Get nodes up to a certain depth with bus nodes at the start of child lists.

    Arguments:
        roots: List of nodes to walk down from.
        depth: Depth up to which nodes must be returned.

    Returns:
        Nodes up to the provided list.
    """
    for node in roots:
        if node.is_leaf or node.depth == depth:
            yield node
            continue

        children = sorted(node.children, key=lambda n: n.is_bus, reverse=True)

        if node.depth == depth - 1:
            yield from children
        else:
            yield from get_up_to_depth(children, depth)
