"""Line matcher state machines of relation definitions."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import typing
from raesl.compile.typechecking import reldef_builder

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_RELATION_DEF_SPEC = """
relation_def:
    start initial;
    start -> s1 [DEFINE_KW] tag=define;
    s1 -> s2 [RELATION_KW];

    end accept=define_relation;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def _process_reldef_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["define"][0], True)


_RELATION_NAME_LINE_SPEC = """
relation_name:
    start initial;
    start -> s1 [NAME] tag=rel_name;

    end accept=relation_name;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_reldef_new_relation(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    builder.add_reldef(tags["rel_name"][0])


_RELATION_PARAMETER_HEADER_SPEC = """
relation_param_header_spec:
    start initial;
    start -> s1 [REQUIRING_KW] tag=rel_requiring;
    start -> s1 [RETURNING_KW] tag=rel_returning;
    start -> s1 [RELATING_KW] tag=rel_relating;
    s1 -> s2 [PARAMETER_KW];

    end accept=relation_param_header;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def _process_reldef_param_header(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    if "rel_requiring" in tags:
        token = tags["rel_requiring"][0]
        direction = reldef_builder.INPUT
    elif "rel_returning" in tags:
        token = tags["rel_returning"][0]
        direction = reldef_builder.OUTPUT
    else:
        assert "rel_relating" in tags
        token = tags["rel_relating"][0]
        direction = reldef_builder.INPOUT

    builder.reldef_param_header(token, direction)


_RELATION_PARAMETER_LINE_SPEC = """
relation_param:
    start initial;
    start -> s1 [STAR_TK];
    s1 -> s5 [NAME] tag=param_name;

    s1 -> s2 [ONE_KW] tag=multi_param;
    s2 -> s3 [OR_KW];
    s3 -> s4 [MORE_KW];

    s4 -> s5 [NAME] tag=param_name;
    s5 -> s6 [IS_KW];
    s6 -> s7 [A_KW];
    s7 -> s8 [NAME] tag=param_type;

    end accept=relation_param;
    s8 -> end [NL_TK];
    s8 -> end [EOF_TK];
"""


def _process_reldef_param_entry(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    param_name = tags["param_name"][0]
    param_type = tags["param_type"][0]
    builder.reldef_add_param(param_name, param_type, "multi_param" in tags)


MACHINES: typing.MachineTripletList = [
    ("DEFINE_RELATION_MACHINE", _RELATION_DEF_SPEC, _process_reldef_header),
    (
        "RELATION_NAME_LINE_MACHINE",
        _RELATION_NAME_LINE_SPEC,
        _process_reldef_new_relation,
    ),
    (
        "RELATION_PARAMETER_HEADER_MACHINE",
        _RELATION_PARAMETER_HEADER_SPEC,
        _process_reldef_param_header,
    ),
    (
        "RELATION_PARAMETER_LINE_MACHINE",
        _RELATION_PARAMETER_LINE_SPEC,
        _process_reldef_param_entry,
    ),
]
