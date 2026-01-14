from ragraph.graph import Graph

import raesl.plot


def test_hierarchy_diagram(pump_example_graph: Graph, check_digraph):
    graph = pump_example_graph

    for depth in [1, 2, 3]:
        fname = f"hierarchy_diagram_{depth}.txt"
        digraph = raesl.plot.hierarchy_diagram(
            graph,
            roots=[graph["world"]],
            levels=depth,
        )
        check_digraph(digraph, fname)


def test_functional_context_diagram(pump_example_graph: Graph, check_digraph):
    """Test functional context diagram."""
    graph = pump_example_graph

    styles = [
        raesl.plot.Style(diagram=dict(show_root_children=False, show_neighbour_children=False)),
        raesl.plot.Style(diagram=dict(show_root_children=True, show_neighbour_children=False)),
        raesl.plot.Style(diagram=dict(show_root_children=False, show_neighbour_children=True)),
        raesl.plot.Style(diagram=dict(show_root_children=True, show_neighbour_children=True)),
    ]

    for idx, style in enumerate(styles):
        fname = f"functional_context_diagram_{idx}.txt"
        digraph = raesl.plot.functional_context_diagram(
            graph,
            root=graph["world.drive-mechanism.motor"],
            degree=1,
            style=style,
        )
        check_digraph(digraph, fname)


def test_functional_traceability_diagram(pump_example_graph: Graph, check_digraph):
    graph = pump_example_graph

    styles = [
        raesl.plot.Style(diagram=dict(show_function_dependencies=False)),
        raesl.plot.Style(diagram=dict(show_function_dependencies=True)),
    ]

    for idx, style in enumerate(styles):
        fname = f"function_chain_diagram_pump_{idx}.txt"
        digraph = raesl.plot.function_traceability_diagram(
            graph,
            root=graph["world.drive-mechanism.convert-power-potential"],
            levels=3,
            style=style,
        )
        check_digraph(digraph, fname)


def test_functional_dependency_diagram(pump_example_graph: Graph, check_digraph):
    graph = pump_example_graph
    depths = [1, 2, 3, 4]
    for depth in depths:
        fname = f"functional_dependency_diagram_{depth}.txt"
        digraph = raesl.plot.functional_dependency_diagram(
            graph,
            root=graph["world"],
            levels=depth,
        )
        check_digraph(digraph, fname)


def test_function_chain_diagram(pump_example_graph: Graph, check_digraph):
    graph = pump_example_graph
    start_points = [
        (
            graph["world.drive-mechanism.power-source"],
            [graph["world.drive-mechanism.power-source.convert-potential"]],
        )
    ]
    end_points = [(graph["world.pump"], [graph["world.pump.convert-torque"]])]
    style = raesl.plot.Style(diagram=dict(show_variables=True))

    for levels in [1, 2]:
        fname = f"function_chain_diagram_{levels}.txt"
        digraph = raesl.plot.function_chain_diagram(
            graph,
            start_points=start_points,
            end_points=end_points,
            levels=levels,
            style=style,
        )
        check_digraph(digraph, fname)
