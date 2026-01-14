"""Tests for rendering paths pointing to elements in a specification."""

import pytest
from ragraph.graph import Graph
from ragraph.node import Node

from raesl.render.paths import PathDisplay, path_display, pretty_path, var_path


def test_comp_path(context, pump_example_graph: Graph):
    comp = pump_example_graph["world.drive-mechanism.motor"]

    p = path_display(context, comp)

    assert p == PathDisplay(
        context,
        display_segments=["drive-mechanism", "motor"],
        ref_path="world.drive-mechanism.motor",
        pretty=False,
        bold=False,
        raw=False,
        label=False,
        link=False,
        replace_spaces=True,
    )


@pytest.mark.parametrize(
    "name,parts",
    [
        ("world.torque", ["torque"]),
        ("world.drive-mechanism.power", ["drive-mechanism", "power"]),
        ("world.drive-mechanism.motor.conversion", ["drive-mechanism", "motor", "conversion"]),
    ],
)
def test_var_path(context, name: str, parts: list[str], pump_example_graph: Graph):
    graph = pump_example_graph
    node = graph[name]

    pd = var_path(context, node, graph=graph)
    assert pd.display_segments == parts


@pytest.mark.parametrize(
    "name,parts",
    [
        ("world.torque", ["torque"]),
        ("world.drive-mechanism.power", ["drive-mechanism", "power"]),
        ("world.drive-mechanism.motor.conversion", ["conversion"]),
    ],
)
def test_var_path_context(context, name: str, parts: list[str], pump_example_graph: Graph):
    graph = pump_example_graph
    node = graph[name]

    pd = var_path(context, node, graph=graph, parent=graph["world.drive-mechanism.motor"])
    assert pd.display_segments == parts, "Context should only apply to the last test case."


@pytest.mark.parametrize(
    "path_args,typst",
    [
        (
            dict(
                node=Node(name="world.foo.bar.quux.co", kind="component"),
                skip_world=True,
                bold=False,
            ),
            "foo#{sym.arrow.r}bar#{sym.arrow.r}quux#{sym.arrow.r}co",
        ),
        (
            dict(
                node=Node(name="world.foo.bar.quux.co", kind="component"),
                skip_world=False,
                bold=False,
            ),
            "world#{sym.arrow.r}foo#{sym.arrow.r}bar#{sym.arrow.r}quux#{sym.arrow.r}co",
        ),
    ],
)
def test_path_rendering(context, path_args, typst: str):
    path = pretty_path(context, **path_args)
    path.FORMAT = "typst"
    assert str(path) == typst
