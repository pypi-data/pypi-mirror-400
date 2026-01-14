"""Line matcher state machines for variable declarations."""
from typing import TYPE_CHECKING

from raesl.compile.ast.components import VarParam
from raesl.compile.machine_files import typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_VARIABLE_HEADER_SPEC = """
variable_header:
    start initial;
    start -> s1 [VARIABLE_KW] tag=variable;

    end accept=variable_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_varheader(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["variable"][0], False)


_VARIABLE_LINE_SPEC = """
variable_line:
    start initial;
    start -> s1 [NAME] tag=varname;
    s1 -> start [COMMA_TK];

    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [NAME] tag=typename;

    end accept=variable_line;
    s4 -> end [NL_TK];
    s4 -> end [EOF_TK];
"""


def _process_varline(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    varnames = tags["varname"]
    typename = tags["typename"][0]
    variables = [VarParam(True, vname, typename) for vname in varnames]
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_variables(variables)


MACHINES: typing.MachineTripletList = [
    ("VARIABLE_HEADER_MACHINE", _VARIABLE_HEADER_SPEC, _process_varheader),
    ("VARIABLE_LINE_MACHINE", _VARIABLE_LINE_SPEC, _process_varline),
]
