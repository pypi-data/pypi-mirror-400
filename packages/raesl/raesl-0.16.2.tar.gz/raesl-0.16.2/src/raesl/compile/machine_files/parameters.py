"""Line matcher state machines for parameters."""
from typing import TYPE_CHECKING

from raesl.compile.ast.components import VarParam
from raesl.compile.machine_files import typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_PARAMETER_HEADER_SPEC = """
parameter_header:
    start initial;
    start -> s1 [PARAMETER_KW] tag=parameter;

    end accept=parameter_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_paramheader(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    token = tags["parameter"][0]
    builder.notify_new_section(token, False)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.notify_parameter_section(token)


_PARAMETER_LINE_SPEC = """
parameter_line:
    start initial;
    start -> s1 [NAME] tag=paramname;
    s1 -> start [COMMA_TK];

    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [NAME] tag=typename;

    end accept=parameter_line;
    s4 -> end [NL_TK];
    s4 -> end [EOF_TK];

    s4 -> s5 [PROPERTY_KW] tag=is_property;
    s5 -> end [NL_TK];
    s5 -> end [EOF_TK];
"""


def _process_paramline(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    paramnames = tags["paramname"]
    typename = tags["typename"][0]
    is_property = "is_property" in tags
    parameters = [VarParam(False, vname, typename, is_property) for vname in paramnames]
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_parameters(parameters)


MACHINES: typing.MachineTripletList = [
    ("PARAMETER_HEADER_MACHINE", _PARAMETER_HEADER_SPEC, _process_paramheader),
    ("PARAMETER_LINE_MACHINE", _PARAMETER_LINE_SPEC, _process_paramline),
]
