"""Line matcher state machines for comments."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder

_COMMENT_HEADER_SPEC = """
comment_header:
    start initial;
    start -> s1 [COMMENT_KW] tag=comment;

    end accept=comment_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_comment_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["comment"][0], False)


_COMMENT_LINE_SPEC = """
comment_line:
    start initial;
    start -> s1 [DOTTEDNAME] tag=name;

    end accept=comment_name;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_comment_name(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_comment(tags["name"][0])


MACHINES: typing.MachineTripletList = [
    ("COMMENT_HEADER_MACHINE", _COMMENT_HEADER_SPEC, _process_comment_header),
    ("COMMENT_LINE_MACHINE", _COMMENT_LINE_SPEC, _process_comment_name),
]
