"""HTML specific helpers."""

from raesl.render.renderer import Renderer


def tagged(
    tag: str,
    content: str | Renderer | list[str] | list[Renderer] | list[str | Renderer] | None = None,
    multiline: bool = False,
    **kwargs,
) -> str:
    """Content wrapped in an HTML tag."""

    if kwargs:
        attrs = " ".join(str(k) if v is None else f'{k}="{v}"' for k, v in kwargs.items())
        open = f"{tag} {attrs}"
    else:
        open = f"{tag}"

    if content is None:
        return f"<{open} />"

    content = "\n".join(str(c) for c in content) if isinstance(content, list) else str(content)
    if multiline and "\n" in content:
        return f"<{open}>\n{content}\n</{tag}>"
    else:
        return f"<{open}>{content}</{tag}>"


BREAK = "<br>"
