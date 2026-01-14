"""Line matcher state machines for designs."""
from typing import TYPE_CHECKING

from raesl.compile.ast import components
from raesl.compile.machine_files import sub_clause, typing
from raesl.compile.machine_files.machine_parts import get_disjunctive_comparison_part

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_DESIGN_HEADER_SPEC = """
design_header:
    start initial;
    start -> s1 [DESIGN_REQUIREMENT_KW] tag=design;
    start -> s1 [DESIGN_CONSTRAINT_KW] tag=design;

    end accept=design_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_design_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    kind = tags["design"][0]
    builder.notify_new_section(kind, False)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.new_design_header(kind)


_DESIGN_WITH_SUBS_SPEC = (
    """
design_clause_with_sub:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
"""
    + get_disjunctive_comparison_part("s2", ["s3", "s4"])
    + """\
    s3 -> s5 [WITH_KW];
    s4 -> s5 [WITH_KW];
    s5 -> s6 [SUB_CLAUSES_KW] tag=with_subclause;

    finish accept=design_with_subs;
    s6 -> finish [NL_TK];
    s6 -> finish [EOF_TK];
"""
)


def _process_design_line(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    label = tags["label"][0]
    condition = sub_clause.decode_disjunctive_comparisons(tags)
    design = components.Design(label, condition)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.design_line(design)


_DESIGN_NO_SUBS_SPEC = (
    """
design_clause_no_sub:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
"""
    + get_disjunctive_comparison_part("s2", ["s3", "s4"])
    + """\
    finish accept=design_no_subs;
    s3 -> finish [NL_TK];
    s3 -> finish [EOF_TK];
    s4 -> finish [NL_TK];
    s4 -> finish [EOF_TK];
"""
)

# _DESIGN_NO_SUBS_SPEC also uses _process_design_line.


def _process_design_subclause(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    sub = sub_clause.decode_subclause(tags)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_design_subclause(sub)


MACHINES: typing.MachineTripletList = [
    ("DESIGN_HEADER_MACHINE", _DESIGN_HEADER_SPEC, _process_design_header),
    ("DESIGN_WITH_SUBS_MACHINE", _DESIGN_WITH_SUBS_SPEC, _process_design_line),
    ("DESIGN_NO_SUBS_MACHINE", _DESIGN_NO_SUBS_SPEC, _process_design_line),
    (
        "DESIGN_SUB_CLAUSE_MACHINE",
        sub_clause.SUB_CLAUSE_SPEC,
        _process_design_subclause,
    ),
]
