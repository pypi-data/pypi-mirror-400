"""Line matcher state machines for goals."""
from typing import TYPE_CHECKING

from raesl.compile.ast import components
from raesl.compile.machine_files import sub_clause, typing
from raesl.compile.machine_files.machine_parts import (
    get_argument_references_part,
    get_does_auxiliary_verb_part,
)

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_GOAL_HEADER_SPEC = """
goal_header:
    start initial;
    start -> s1 [GOAL_REQUIREMENT_KW] tag=goal_kind;
    start -> s1 [GOAL_CONSTRAINT_KW] tag=goal_kind;

    end accept=goal_header;
    s1 -> end [NL_TK];
"""


def _process_goal_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    goal_kind = tags["goal_kind"][0]
    builder.notify_new_section(goal_kind, False)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.new_goal_header(goal_kind)


_GOAL_MAIN_WITH_SUBS_SPEC = (
    """
goal_main_with_subs:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
    s2 -> s3 [NAME] tag=active_compname;
"""
    + get_does_auxiliary_verb_part("s3", ["s4"], tagname="doesaux")
    + """\
    s4 -> s5 [NAME] tag=verb;
"""
    + get_argument_references_part("s5", ["s7"], tagname="argument_name")
    + """\
    s7 -> s8 [NAME] tag=prepos;
    s8 -> s9 [NAME] tag=passive_compname;

    s9 -> s10 [WITH_KW];
    s10 -> s11 [SUB_CLAUSES_KW] tag=with_subclause;

    end accept=goal_main_with_subs;
    s11 -> end [NL_TK];
    s11 -> end [EOF_TK];
"""
)


def _process_goal_with_subs(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    label = tags["label"][0]
    active = tags["active_compname"][0]
    doesaux = tags["doesaux"][0]
    verb = tags["verb"][0]
    flows = [components.Flow(name_tok) for name_tok in tags["argument_name"]]
    prepos = tags["prepos"][0]
    passive = tags["passive_compname"][0]
    goal = components.Goal(label, active, doesaux, verb, flows, prepos, passive)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_goal(goal)


_GOAL_MAIN_NO_SUBS_SPEC = (
    """
goal_main_no_subs:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
    s2 -> s3 [NAME] tag=active_compname;
"""
    + get_does_auxiliary_verb_part("s3", ["s4"], tagname="doesaux")
    + """\
    s4 -> s5 [NAME] tag=verb;
"""
    + get_argument_references_part("s5", ["s7"], tagname="argument_name")
    + """\
    s7 -> s8 [NAME] tag=prepos;
    s8 -> s9 [NAME] tag=passive_compname;

    end accept=goal_main_no_subs;
    s9 -> end [NL_TK];
    s9 -> end [EOF_TK];
"""
)


def _process_goal_no_subs(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    label = tags["label"][0]
    active = tags["active_compname"][0]
    doesaux = tags["doesaux"][0]
    verb = tags["verb"][0]
    flows = [components.Flow(name_tok) for name_tok in tags["argument_name"]]
    prepos = tags["prepos"][0]
    passive = tags["passive_compname"][0]
    goal = components.Goal(label, active, doesaux, verb, flows, prepos, passive)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_goal(goal)


def _process_goal_subclause(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    sub = sub_clause.decode_subclause(tags)
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_goal_subclause(sub)


MACHINES: typing.MachineTripletList = [
    ("GOAL_HEADER_MACHINE", _GOAL_HEADER_SPEC, _process_goal_header),
    ("GOAL_MAIN_WITH_SUBS_MACHINE", _GOAL_MAIN_WITH_SUBS_SPEC, _process_goal_with_subs),
    ("GOAL_MAIN_NO_SUBS_MACHINE", _GOAL_MAIN_NO_SUBS_SPEC, _process_goal_no_subs),
    ("GOAL_SUB_CLAUSE_MACHINE", sub_clause.SUB_CLAUSE_SPEC, _process_goal_subclause),
]
