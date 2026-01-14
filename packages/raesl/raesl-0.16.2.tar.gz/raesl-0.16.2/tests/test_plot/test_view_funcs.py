"""Tests for the view_funcs module."""

import pytest

from raesl.plot import view_funcs

funcs = [
    view_funcs.multi_domain,
    view_funcs.hierarchy,
    view_funcs.function_chain,
    view_funcs.functional_context,
    view_funcs.functional_dependency,
    view_funcs.traceability,
]


@pytest.fixture(params=funcs)
def view_func(request):
    """Returns each view_func once."""
    return request.param


@pytest.fixture
def view_func_kwargs_graph(view_func, pump_example_graph):
    """Creates a combination of view_func, kwargs and graph data."""
    graph = pump_example_graph

    if view_func == view_funcs.hierarchy:
        kwargs = dict(roots=graph.roots, levels=4)

    elif view_func == view_funcs.function_chain:
        kwargs = dict(
            start_points=[
                (
                    graph["world.drive-mechanism.power-source"],
                    [graph["world.drive-mechanism.power-source.convert-potential"]],
                )
            ],
            end_points=[(graph["world.pump"], [graph["world.pump.convert-torque"]])],
        )

    elif view_func == view_funcs.functional_context:
        kwargs = dict(root=graph["world.drive-mechanism"], degree=2)

    elif view_func == view_funcs.functional_dependency:
        kwargs = dict(root=graph["world"], levels=4)

    elif view_func == view_funcs.traceability:
        kwargs = dict(root=graph["world.drive-mechanism.convert-power-potential"], levels=2)

    else:
        kwargs = dict()

    return view_func, kwargs, graph


def test_preserve_graph(view_func_kwargs_graph):
    """Check whether original Graph data remains untouched by view_funcs."""
    view_func, kwargs, graph = view_func_kwargs_graph
    ref = graph.json_dict
    view_func(graph, **kwargs)
    assert graph.json_dict == ref, "Graph data should be untouched by the view_func."
