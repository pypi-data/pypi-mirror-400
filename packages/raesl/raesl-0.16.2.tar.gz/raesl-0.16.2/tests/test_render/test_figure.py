"""Tests for the figure rendering module."""

import plotly.graph_objects as go

from raesl.render.figure import Figure


def test_figure_renderer_by_path(temp_context):
    fig = go.Figure()

    resolved = temp_context.figure_path("test.svg", resolved=True)
    resolved.parent.mkdir(exist_ok=True, parents=True)
    fig.write_image(resolved)

    renderer = Figure(
        temp_context,
        resolved.relative_to(temp_context.output_dir),
        label="test figure",
        caption="An empty Plotly figure, included from an SVG file.",
    )

    renderer.compile("test.pdf")
    renderer.compile("test.html")
    renderer.compile("test.md")


def test_figure_renderer_raw(temp_context):
    fig = go.Figure()
    renderer = Figure(
        temp_context,
        fig,
        label="test figure",
        caption="An empty Plotly figure, included directly in Typst.",
    )
    renderer.compile("test.pdf")
    renderer.compile("test.html")
    renderer.compile("test.md")
