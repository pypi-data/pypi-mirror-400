"""Line matcher state machines for transformations."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_DEFINE_COMPONENT_SPEC = """
define_component:
    start initial;
    start -> s1 [DEFINE_KW];
        s1 -> s2 [COMPONENT_KW];
        s2 -> s3 [NAME] tag=comp_name;
    start -> s3 [WORLD_KW] tag=world;

    end accept=define_component;
    s3 -> end [NL_TK];
    s3 -> end [EOF_TK];
"""


def _process_compdef(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    if "world" in tags:
        pos_tok = tags["world"][0]
        name_tok = None
    else:
        name_tok = tags["comp_name"][0]
        pos_tok = name_tok

    builder.notify_new_section(pos_tok, True)
    builder.compdef_builder.new_componentdef(pos_tok, name_tok)


_EMPYTY_SPEC = """
empty_component:
    start initial;
    start -> s1 [EMPTY_KW];

    end accept=empty_component;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""

# No processing function needed for _EMPYTY_SPEC lines.

MACHINES: typing.MachineTripletList = [
    ("DEFINE_COMPONENT_MACHINE", _DEFINE_COMPONENT_SPEC, _process_compdef),
    ("EMPTY_MACHINE", _EMPYTY_SPEC, None),
]
