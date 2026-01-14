"""Line matcher state machines for relation instances."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import argument_list, typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_RELATION_HEADER_SPEC = """
relation_header:
    start initial;
    start -> s1 [RELATION_KW] tag=relation;

    end accept=relation_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_relinst_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["relation"][0], False)


_RELATION_INSTANCE_SPEC = """
relation_instance:
    start initial;
    start -> s1 [NAME] tag=relation_inst_name;
    s1 -> s2 [COLON_TK];
    s2 -> s3 [NAME] tag=relation_def_name;

    end accept=instance_line;
    s3 -> end [NL_TK];
    s3 -> end [EOF_TK];
"""


def _process_new_relinst(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.new_relinst(tags["relation_inst_name"][0], tags["relation_def_name"][0])


_RELATION_ARGUMENT_HEADER_SPEC = """
relation_argument_header:
    start initial;
    start -> s1 [REQUIRING_KW] tag=argtype;
    start -> s1 [RETURNING_KW] tag=argtype;
    start -> s1 [RELATING_KW] tag=argtype;

    s1 -> s2 [ARGUMENT_KW];

    end accept=header_argument_line;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def _process_relinst_argheader(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.relinst_argheader(tags["argtype"][0])


# Argument line processing.
def _process_instance_arguments(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    arguments = argument_list.process_argument_list_line(tags)
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_relinst_arguments(arguments)


MACHINES: typing.MachineTripletList = [
    ("RELATION_HEADER_MACHINE", _RELATION_HEADER_SPEC, _process_relinst_header),
    ("RELATION_INSTANCE_MACHINE", _RELATION_INSTANCE_SPEC, _process_new_relinst),
    (
        "RELATION_ARGUMENT_HEADER_MACHINE",
        _RELATION_ARGUMENT_HEADER_SPEC,
        _process_relinst_argheader,
    ),
    (
        "RELATION_ARGUMENT_MACHINE",
        argument_list.ARGUMENT_LINE_SPEC,
        _process_instance_arguments,
    ),
]
