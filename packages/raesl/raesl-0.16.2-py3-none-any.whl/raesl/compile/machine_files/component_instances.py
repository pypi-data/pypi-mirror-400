"""Line matchers for component instances within world or a component definition."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import argument_list, typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_COMPONENT_HEADER_SPEC = """
component_header:
    start initial;
    start -> s1 [COMPONENT_KW] tag=component;

    end accept=component_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_component_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["component"][0], False)


_COMPONENT_INSTANCE_NO_ARGS_SPEC = """
component_instance:
    start initial;
    start -> s1 [NAME] tag=component_instance;
    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [NAME] tag=component_def;

    end accept=component_instance_no_arguments;
    s4 -> end [NL_TK];
    s4 -> end [EOF_TK];
"""


def _process_instance_no_args(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    instance_tok = tags["component_instance"][0]
    definition_tok = tags["component_def"][0]
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_compinst(instance_tok, definition_tok, False)


_COMPONENT_INSTANCE_WITH_ARGS_SPEC = """
component_instance:
    start initial;
    start -> s1 [NAME] tag=component_instance;
    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [NAME] tag=component_def;

    s4 -> s5 [WITH_KW];
    s5 -> s6 [ARGUMENT_KW];

    end accept=component_instance_with_arguments;
    s6 -> end [NL_TK];
"""


def _process_instance_with_args(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    instance_tok = tags["component_instance"][0]
    definition_tok = tags["component_def"][0]
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_compinst(instance_tok, definition_tok, True)


# Argument line processing.
def _process_instance_arguments(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    arguments = argument_list.process_argument_list_line(tags)
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_compinst_arguments(arguments)


MACHINES: typing.MachineTripletList = [
    ("COMPONENT_HEADER_MACHINE", _COMPONENT_HEADER_SPEC, _process_component_header),
    (
        "COMPONENT_INSTANCE_NO_ARGS_MACHINE",
        _COMPONENT_INSTANCE_NO_ARGS_SPEC,
        _process_instance_no_args,
    ),
    (
        "COMPONENT_INSTANCE_WITH_ARGS_MACHINE",
        _COMPONENT_INSTANCE_WITH_ARGS_SPEC,
        _process_instance_with_args,
    ),
    (
        "COMPONENT_ARGUMENT_MACHINE",
        argument_list.ARGUMENT_LINE_SPEC,
        _process_instance_arguments,
    ),
]
