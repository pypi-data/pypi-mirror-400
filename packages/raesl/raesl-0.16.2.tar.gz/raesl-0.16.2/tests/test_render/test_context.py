"""Tests for the rendering context."""

from pathlib import Path

import pytest

from raesl.render.context import (
    Context,
    _format_from_path,
    _format_from_suffix,
    _suffix_from_format,
)


@pytest.mark.parametrize(
    "format,suffix",
    [
        ["typst", ".typ"],
        ["html", ".html"],
        ["pdf", ".pdf"],
        ["markdown", ".md"],
    ],
)
def test_format_suffix_path_conversions(format, suffix):
    assert _suffix_from_format(format) == suffix
    assert _format_from_suffix(suffix) == format

    path = Path("foo").with_suffix(suffix)
    assert _format_from_path(path) == format


def test_format_from_path_pdf_fallback():
    assert _format_from_path(Path("foo")) == "pdf"
    assert _format_from_path(Path("foo.bar")) == "bar"


def test_context_dirs():
    ctx = Context()

    assert ctx.output_dir is None

    with ctx.output_dir_context() as out:
        assert out == Path.cwd()

        assert ctx.output_dir is not None, "Should get current working directory within context."

        assert ctx.figures_dir == Path("figures")

        assert ctx.figure_path("foo.svg", resolved=True) == out / "figures" / "foo.svg"
        assert ctx.figure_path("foo.svg", resolved=False) == Path("figures") / "foo.svg"

    assert ctx.output_dir is None


def test_temp_context(temp_context):
    ctx = temp_context
    assert ctx.output_dir is not None

    with ctx.output_dir_context() as out:
        assert out != Path.cwd()
        assert ctx.figures_dir == Path("figures")
        assert ctx.figure_path("foo.svg", resolved=True) == out / "figures" / "foo.svg"
        assert ctx.figure_path("foo.svg", resolved=False) == Path("figures") / "foo.svg"


@pytest.mark.parametrize(
    "name,parts",
    [
        ["foo", ["foo"]],
        ["foo.bar", ["foo", "bar"]],
        ["foo.bar.baz", ["foo", "bar", "baz"]],
    ],
)
def test_split_join(name, parts):
    ctx = Context()
    assert ctx.split(name) == parts
    assert ctx.join(parts) == name

    ctx.separator = "o"
    assert ctx.split(name) != parts


@pytest.mark.parametrize(
    "name,spaced",
    [
        ["foo", ["foo"]],
        ["foo_bar", ["foo bar"]],
        ["foo_bar_baz", ["foo bar baz"]],
    ],
)
def test_spaced(name, spaced):
    ctx = Context()
    ctx.spaced(name) == spaced


def test_figure_flushing(temp_context):
    ctx = temp_context
    out = ctx.output_dir / ctx.figures_dir

    import plotly.graph_objs as go

    ctx.add_figure(go.Figure(), "foo.svg")
    ctx.add_figure(go.Figure(), "bar.svg")

    assert len(ctx.figures_cache) == 2
    assert not out.exists()

    ctx.flush_figures()
    set((out).iterdir()) == {out / "foo.svg", out / "bar.svg"}
    assert len(ctx.figures_cache) == 0
