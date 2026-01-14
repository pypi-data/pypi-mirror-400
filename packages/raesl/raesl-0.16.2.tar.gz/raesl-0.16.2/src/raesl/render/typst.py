"""Typst specific helpers."""

import pypst

from raesl.render.renderer import Renderer


def ensure_typst_arg(x) -> str:
    """Make sure a function argument is rendered correctly."""
    if isinstance(x, Renderer):
        return str(x).lstrip("#")

    if isinstance(x, pypst.Renderable):
        arg = x.render()
    else:
        arg = str(pypst.Content(str(x)))

    return arg.lstrip("#")
