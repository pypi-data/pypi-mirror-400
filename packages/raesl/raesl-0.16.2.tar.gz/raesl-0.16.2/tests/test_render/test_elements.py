"""Tests for the rendering content data."""

from typing import get_args

from pytest import mark

from raesl.render.context import Context
from raesl.render.elements import (
    Bold,
    BoldHeading,
    Emph,
    Heading,
    IncludeFile,
    Label,
    Ordered,
    Par,
    Raw,
    Reference,
    Renderer,
    Table,
    TableCell,
    TableHeader,
    TableHLine,
    Unordered,
)
from raesl.render.renderer import Format

context = Context()


@mark.parametrize(
    "input,typst,markdown,html",
    [
        (
            Heading(context, "Hello world!"),
            "= Hello world!",
            "# Hello world!",
            "<h1>Hello world!</h1>",
        ),
        (
            BoldHeading(context, " Hello world!   "),
            "\n#strong[Hello world!]\n",
            "\n**Hello world!**\n",
            "<br><strong>Hello world!</strong><br>",
        ),
        (
            Bold(context, " Le foo est bar. "),
            "#strong[Le foo est bar.]",
            "**Le foo est bar.**",
            "<strong>Le foo est bar.</strong>",
        ),
        (
            Emph(context, " Qu que le quux! "),
            "#emph[Qu que le quux!]",
            "*Qu que le quux!*",
            "<em>Qu que le quux!</em>",
        ),
        (
            Raw(context, " Qu que le quux! "),
            "` Qu que le quux! `",
            "` Qu que le quux! `",
            "<code> Qu que le quux! </code>",
        ),
        (
            Par(context, "\nQue que le quux! Le foo est bar.\n\n"),
            "Que que le quux! Le foo est bar.\n",
            "Que que le quux! Le foo est bar.\n",
            "<p>Que que le quux! Le foo est bar.</p>",
        ),
        (
            Ordered(context, ["Foo", "Bar Baz"]),
            "+ Foo\n+ Bar Baz\n",
            "1. Foo\n1. Bar Baz\n",
            "<ol>\n<li>Foo</li>\n<li>Bar Baz</li>\n</ol>",
        ),
        (
            Unordered(context, ["Quuxqe", "Foosball"]),
            "- Quuxqe\n- Foosball\n",
            "- Quuxqe\n- Foosball\n",
            "<ul>\n<li>Quuxqe</li>\n<li>Foosball</li>\n</ul>",
        ),
        (
            Ordered(
                context, ["Foo", Ordered(context, ["Bar", "Baz", Unordered(context, ["Que?"])])]
            ),
            "+ Foo\n  + Bar\n  + Baz\n    - Que?\n",
            "1. Foo\n  1. Bar\n  1. Baz\n    - Que?\n",
            "<ol>\n<li>Foo</li>\n<ol>\n<li>Bar</li>\n<li>Baz</li>\n<ul>\n<li>Que?</li>\n</ul>\n</ol>\n</ol>",
        ),
        (
            Label(context, kind="sec", label="full-label"),
            "<sec:full-label>",
            '<div id="sec:full-label" />',
            '<div id="sec:full-label" />',
        ),
        (
            Reference(context, kind="sec", label="full-label"),
            "@sec:full-label",
            '<a href="#sec:full-label">sec:full-label</a>',
            '<a href="#sec:full-label">sec:full-label</a>',
        ),
        (
            Reference(context, kind="sec", label="full-label", display="hello world!"),
            "#context{if query(<sec:full-label>).len() == 0 [hello world!] else "
            + "[#link(<sec:full-label>)[hello world!]]}",
            '<a href="#sec:full-label">hello world!</a>',
            '<a href="#sec:full-label">hello world!</a>',
        ),
        (
            TableCell(
                context,
            ),
            "#table.cell(none)",
            "<td />",
            "<td />",
        ),
        (
            TableCell(context, "hello world"),
            "#table.cell([hello world])",
            "<td>hello world</td>",
            "<td>hello world</td>",
        ),
        (
            TableHeader(
                context,
                ["hello", "world", "foo", TableCell(context, "quux")],
            ),
            "#table.header([hello], [world], [foo], table.cell([quux]), repeat: true)",
            "<th>hello</th>\n<th>world</th>\n<th>foo</th>\n<th>quux</th>",
            "<th>hello</th>\n<th>world</th>\n<th>foo</th>\n<th>quux</th>",
        ),
        (
            TableHLine(
                context,
            ),
            '#table.hline(stroke: (thickness: 1pt, dash: "dashed", paint: palette.secondary-100))',
            "<tr style=\"border-top: '1pt dashed'\" />",
            "<tr style=\"border-top: '1pt dashed'\" />",
        ),
        (
            TableHLine(context, y=2),
            "#table.hline(y: 2, "
            + 'stroke: (thickness: 1pt, dash: "dashed", paint: palette.secondary-100))',
            "<tr style=\"border-top: '1pt dashed'\" />",
            "<tr style=\"border-top: '1pt dashed'\" />",
        ),
        (
            Table(
                context,
                [
                    TableHeader(context, ["foo", "bar", "baz", "quux"]),
                    TableHLine(
                        context,
                    ),
                    "some",
                    "separate",
                    "cells",
                ],
            ),
            "#figure(table(table.header([foo], [bar], [baz], [quux], repeat: true), "
            + "table.hline(stroke: "
            + '(thickness: 1pt, dash: "dashed", paint: palette.secondary-100)), '
            + "[some], [separate], [cells], "
            + "columns: 4, column-gutter: 0.5em, row-gutter: auto, inset: (x: 0pt)), "
            + "outlined: false)",
            "<table>\n"
            + "<th>foo</th>\n<th>bar</th>\n<th>baz</th>\n<th>quux</th>\n"
            + "<tr style=\"border-top: '1pt dashed'\" />\n"
            + "<tr><td>some</td>\n<td>separate</td>\n<td>cells</td></tr>\n</table>",
            "<table>\n"
            + "<th>foo</th>\n<th>bar</th>\n<th>baz</th>\n<th>quux</th>\n"
            + "<tr style=\"border-top: '1pt dashed'\" />\n"
            + "<tr><td>some</td>\n<td>separate</td>\n<td>cells</td></tr>\n</table>",
        ),
    ],
)
def test_element_rendering(input: Renderer, typst: str, markdown: str, html: str):
    input.context.format = "typst"
    assert str(input) == typst

    input.context.format = "markdown"
    assert str(input) == markdown

    input.context.format = "html"
    assert str(input) == html


def test_include_file(temp_context):
    fpath = temp_context.resolved_path("foo.txt")
    fpath.write_text("hello world")

    include = IncludeFile(context, fpath)

    for fmt in get_args(Format):
        include.FORMAT = fmt
        assert str(include) == "hello world"
