"""Line matcher state machines needs."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_NEED_HEADER_SPEC = """
needs_header:
    start initial;
    start -> s1 [NEED_KW] tag=need;

    end accept=need_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_need_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["need"][0], False)


_NEED_LINE_SPEC = """
needs_line:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
    s2 -> s3 [DOTTEDNAME] tag=subject;
    s3 -> s4 [NONSPACE] tag=description;

    s4 -> s4 [NONSPACE] tag=description;

    end accept=need_line;
    s4 -> end [NL_TK];
    s4 -> end [EOF_TK];
"""


def _process_need(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    label_tok = tags["label"][0]
    subject_tok = tags["subject"][0]
    description = " ".join(tag.tok_text for tag in tags["description"])

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_need(label_tok, subject_tok, description)


MACHINES: typing.MachineTripletList = [
    ("NEED_HEADER_MACHINE", _NEED_HEADER_SPEC, _process_need_header),
    ("NEED_LINE_MACHINE", _NEED_LINE_SPEC, _process_need),
]
