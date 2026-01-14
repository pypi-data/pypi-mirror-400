"""Tests for the document renderer class."""

import pypst
import pytest

from raesl.l10n.en_us import EnUs
from raesl.l10n.nl_nl import NlNl
from raesl.render.renderer import (
    LineGen,
    Renderer,
)


def test_set_format(context):
    renderer = Renderer(context)
    assert renderer.FORMAT == "typst"

    renderer.FORMAT = "markdown"
    assert renderer.FORMAT == "markdown"

    with pytest.raises(ValueError) as e:
        renderer.FORMAT = "foo"
    assert "unsupported" in e.value.args[0]


def test_set_locale(context):
    renderer = Renderer(context)

    assert renderer.L10N == EnUs()

    renderer.L10N = "nl-NL"
    assert renderer.L10N != EnUs()
    assert renderer.L10N == NlNl()

    renderer.L10N = "en"
    assert renderer.L10N == EnUs()

    renderer.L10N = "nl"
    assert renderer.L10N == NlNl()


def test_todo(context):
    class Foo(Renderer):
        pass

    with pytest.warns(UserWarning, match="TODO: implement: Foo"):
        _ = list(Foo(context).todo())


def test_gen_typst(context):
    with pytest.raises(NotImplementedError):
        list(Renderer(context).gen_typst())

    class Foo(Renderer):
        # Adding a render methods passes the Pypst package renderable test.
        def render(self) -> str:
            return "foo"

    assert "\n".join(Foo(context).gen_typst()) == "foo"


def test_gen_content(context):
    class Foo(Renderer):
        def gen_typst(self) -> LineGen:
            yield "= Hello"
            yield pypst.Heading("Heading", level=2)

        def gen_markdown(self) -> LineGen:
            yield "Hello from Markdown."

    class Bar(Renderer):
        def gen_typst(self) -> LineGen:
            yield Foo(self.context)
            yield "fin."

    foo = Foo(context)
    bar = Bar(context)

    assert str(foo) == "= Hello\n== Heading"
    assert str(bar) == "= Hello\n== Heading\nfin."

    foo.FORMAT = "markdown"
    assert str(foo) == "Hello from Markdown."

    with pytest.raises(NotImplementedError) as _:
        str(bar)
