"""Line matching state machines for groups."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import argument_list, typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_GROUP_SECTION_HEADER_SPEC = """
group_section_header:
    start initial;
    start -> s1 [VARIABLE_GROUP_KW] tag=vargroup;

    end accept=group_section_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_vargroup_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["vargroup"][0], False)


_GROUP_START_SPEC = """
group_start:
    start initial;
    start -> s1 [NAME] tag=group_name;
    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [GROUP_KW];
    s4 -> s5 [OF_KW];

    end accept=group_start;
    s5 -> end [NL_TK];
    s5 -> end [EOF_TK];
"""


def _process_new_vargroup(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.new_vargroup(tags["group_name"][0])


def _process_arguments(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    names = argument_list.process_argument_list_line(tags)
    current_comp.vgroup_add_vars(names)


MACHINES: typing.MachineTripletList = [
    (
        "GROUP_SECTION_HEADER_MACHINE",
        _GROUP_SECTION_HEADER_SPEC,
        _process_vargroup_header,
    ),
    ("GROUP_START_MACHINE", _GROUP_START_SPEC, _process_new_vargroup),
    (
        "GROUP_ARGUMENT_LINE_MACHINE",
        argument_list.ARGUMENT_LINE_SPEC,
        _process_arguments,
    ),
]
