"""Line matcher state machines for transformations."""
from typing import TYPE_CHECKING

from raesl.compile.ast import components
from raesl.compile.machine_files import sub_clause, typing
from raesl.compile.machine_files.machine_parts import (
    get_argument_references_part,
    get_does_auxiliary_verb_part,
)

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_TRANSFORM_HEADER_SPEC = """
trasform_header:
    start initial;
    start -> s1 [TRANSFORM_REQUIREMENT_KW] tag=transform_kind;
    start -> s1 [TRANSFORM_CONSTRAINT_KW] tag=transform_kind;

    end accept=transform_header;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""


def _process_transform_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    kind_tok = tags["transform_kind"][0]
    builder.notify_new_section(kind_tok, False)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.notify_transform_section(kind_tok)
    current_comp.new_transform_header(kind_tok)


_TRANSFORM_MAIN_NO_SUBS_SPEC = (
    """
transform_main_no_subs:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
"""
    + get_does_auxiliary_verb_part("s2", ["s4"], tagname="doesaux")
    + """\
    s4 -> s5 [NAME] tag=verb;
"""
    + get_argument_references_part("s5", ["s7"], tagname="from_argument_name", prefix="from")
    + """\
    s7 -> s8 [NAME] tag=prepos;
"""
    + get_argument_references_part("s8", ["s10"], tagname="to_argument_name", prefix="to")
    + """\
    end accept=transform_main_no_subs;
    s10 -> end [NL_TK];
    s10 -> end [EOF_TK];
"""
)


def _process_transform_no_subs(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    label_tok = tags["label"][0]
    doesaux_tok = tags["doesaux"][0]
    verb_tok = tags["verb"][0]
    in_flows = [components.Flow(name_tok) for name_tok in tags["from_argument_name"]]
    prepos_tok = tags["prepos"][0]
    out_flows = [components.Flow(name_tok) for name_tok in tags["to_argument_name"]]
    transform = components.Transformation(
        label_tok, doesaux_tok, verb_tok, in_flows, prepos_tok, out_flows
    )

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_transform(transform)


_TRANSFORM_MAIN_WITH_SUBS_SPEC = (
    """
transform_main_with_subs:
    start initial;
    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];
"""
    + get_does_auxiliary_verb_part("s2", ["s4"], tagname="doesaux")
    + """\
    s4 -> s5 [NAME] tag=verb;
"""
    + get_argument_references_part("s5", ["s7"], tagname="from_argument_name", prefix="from")
    + """\
    s7 -> s8 [NAME] tag=prepos;
"""
    + get_argument_references_part("s8", ["s10"], tagname="to_argument_name", prefix="to")
    + """\
    s10 -> s11 [WITH_KW];
    s11 -> s12 [SUB_CLAUSES_KW] tag=with_subclause;

    end accept=transform_main_with_subs;
    s12 -> end [NL_TK];
    s12 -> end [EOF_TK];
"""
)


def _process_transform_with_subs(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    label_tok = tags["label"][0]
    doesaux_tok = tags["doesaux"][0]
    verb_tok = tags["verb"][0]
    in_flows = [components.Flow(name_tok) for name_tok in tags["from_argument_name"]]
    prepos_tok = tags["prepos"][0]
    out_flows = [components.Flow(name_tok) for name_tok in tags["to_argument_name"]]
    transform = components.Transformation(
        label_tok, doesaux_tok, verb_tok, in_flows, prepos_tok, out_flows
    )

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_transform(transform)


def _process_transform_subclause(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    sub = sub_clause.decode_subclause(tags)
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.add_transform_subclause(sub)


MACHINES: typing.MachineTripletList = [
    ("TRANSFORM_HEADER_MACHINE", _TRANSFORM_HEADER_SPEC, _process_transform_header),
    (
        "TRANSFORM_MAIN_NO_SUBS_MACHINE",
        _TRANSFORM_MAIN_NO_SUBS_SPEC,
        _process_transform_no_subs,
    ),
    (
        "TRANSFORM_MAIN_WITH_SUBS_MACHINE",
        _TRANSFORM_MAIN_WITH_SUBS_SPEC,
        _process_transform_with_subs,
    ),
    (
        "TRANSFORM_SUB_CLAUSE_MACHINE",
        sub_clause.SUB_CLAUSE_SPEC,
        _process_transform_subclause,
    ),
]
