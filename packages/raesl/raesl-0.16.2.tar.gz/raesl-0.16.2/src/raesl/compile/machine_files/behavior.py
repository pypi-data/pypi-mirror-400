"""Line matchers for the behavior section."""

from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast

from raesl.compile.ast import exprs
from raesl.compile.machine_files import machine_parts, sub_clause, typing, utils

if TYPE_CHECKING:
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder


_BEHAVIOR_HEADER_SPEC = """
behavior_header:
    start initial;

    start -> s1 [BEHAVIOR_REQUIREMENT_KW] tag=kind;
    start -> s1 [BEHAVIOR_CONSTRAINT_KW] tag=kind;

    end accept=behavior_header;
    s1 -> end [NL_TK];
"""


def _process_behavior_header(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    behave_kind = tags["kind"][0]
    builder.notify_new_section(behave_kind, False)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.new_behavior_header(behave_kind)


_BEHAVIOR_NAME_SPEC = """
behavior_name:
    start initial;

    start -> s1 [NAME] tag=label;
    s1 -> s2 [COLON_TK];

    end accept=behavior_name;
    s2 -> end [NL_TK];
"""


def _process_new_behavior_function(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    label = tags["label"][0]

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.new_behavior_function(label)


_BEHAVIOR_CASE_SPEC = """
behavior_case:
    start initial;

    start -> s1 [CASE_KW];
    s1 -> s2 [NAME] tag=case_name;
    s2 -> s3 [COLON_TK];

    end accept=behavior_case;
    s3 -> end [NL_TK];
"""


def _process_new_case(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    case_label = tags["case_name"][0]

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.behavior_case(case_label)


_BEHAVIOR_WHEN_SPEC = """
behavior_when:
    start initial;

    start -> s1 [WHEN_KW] tag=when;

    end accept=behavior_when;
    s1 -> end [NL_TK];
"""


def _process_normal_when_start(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.behavior_normal_when(tags["when"][0])


_BEHAVIOR_WHEN_OTHERWISE_SPEC = """
behavior_otherwise:
    start initial;

    start -> s1 [WHEN_KW] tag=when;
    s1 -> s2 [NO_KW];
    s2 -> s3 [OTHER_KW];
    s3 -> s4 [CASE_KW];
    s4 -> s5 [APPLIES_KW];

    end accept=behavior_when;
    s5 -> end [NL_TK];
"""


def _process_otherwise_when_start(
    tags: typing.TokensDict, _accept: str, builder: "AstBuilder"
) -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.behavior_default_when(tags["when"][0])


_BEHAVIOR_WHEN_CONDITION_SPEC = (
    """
when_condition:
    start initial;

    start -> s1 [STAR_TK];
    s1 -> s2 [NAME] tag=condition_name;
    s2 -> s3 [COLON_TK];
    s3 -> s4 [DOTTEDNAME] tag=first_var;
    s4 -> s5 [IS_KW] tag=is_aux;
"""
    + machine_parts.get_compare_op_part("s5", ["s6"], tagname="compare_op")
    + """\
    s6 -> s7 [NONCOMMA] tag=varvalue;
    s7 -> s8 [NONCOMMA] tag=unit;

    s7 -> s3 [OR_KW] tag=or;
    s8 -> s3 [OR_KW] tag=or;

    end accept=behavior_when;
    s7 -> end [NL_TK];
    s8 -> end [NL_TK];
"""
)


def _decode_when_comparisons(
    tags: Dict[str, List["Token"]]
) -> Union[exprs.Disjunction, exprs.RelationComparison]:
    """Decode the expression expressed in the tags from _BEHAVIOR_WHEN_CONDITION_SPEC.

    Much inspired by 'machine_files.decode_disjunctive_comparisons', but this is
    less generic due to lack of 'aux' and objectives.

    Arguments:
        tags: Key pieces of text found in the input.

    Returns:
        The equivalent expression.
    """
    split_offsets = (
        cast(List[Optional[int]], [None]) + [tok.offset for tok in tags.get("or", [])] + [None]
    )
    equations = []

    unit_tags = tags.get("unit", [])
    for index in range(1, len(split_offsets)):
        start_offset = split_offsets[index - 1]
        end_offset = split_offsets[index]

        first_var = utils.get_one(tags["first_var"], start_offset, end_offset)
        lhs = exprs.VariableValue(first_var)

        is_aux = utils.get_one(tags["is_aux"], start_offset, end_offset)
        compare_op = utils.get_one(tags["compare_op"], start_offset, end_offset)
        varvalue = utils.get_one(tags["varvalue"], start_offset, end_offset)
        unit = utils.get_optional(unit_tags, start_offset, end_offset)
        rhs: exprs.DataValue
        if unit is None and sub_clause.guess_is_var(varvalue):
            rhs = exprs.VariableValue(varvalue)
        else:
            rhs = exprs.Value(varvalue, unit)

        comp = exprs.RelationComparison(True, lhs, is_aux, compare_op, rhs)
        equations.append(comp)

    if len(equations) == 1:
        return equations[0]
    else:
        return exprs.Disjunction(equations)


def _process_when_condition(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    name_tok = tags["condition_name"][0]
    expr = _decode_when_comparisons(tags)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.behavior_when_condition(name_tok, expr)


_BEHAVIOR_THEN_SPEC = """
behavior_then:
    start initial;

    start -> s1 [THEN_KW] tag=then;

    end accept=behavior_then;
    s1 -> end [NL_TK];
"""


def _process_then_start(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.behavior_normal_then(tags["then"][0])


_BEHAVIOR_THEN_RESULT_SPEC = (
    """
then_result:
    start initial;

    start -> s1 [STAR_TK];
    s1 -> s2 [NAME] tag=result_name;
    s2 -> s3 [COLON_TK];

    s3 -> s4 [DOTTEDNAME] tag=first_var;
"""
    + machine_parts.get_is_auxiliary_verb_part("s4", ["s5"], tagname="is_aux")
    + """\
    s5 -> s8 [MAXIMIZED_KW] tag=objective;
    s5 -> s8 [MINIMIZED_KW] tag=objective;
"""
    + machine_parts.get_compare_op_part("s5", ["s6"], tagname="compare_op")
    + """\
    s6 -> s7 [NONCOMMA] tag=varvalue;
    s7 -> s8 [NONCOMMA] tag=unit;

    end accept=behavior_then;
    s7 -> end [NL_TK];
    s7 -> end [EOF_TK];
    s8 -> end [NL_TK];
    s8 -> end [EOF_TK];
"""
)


def _decode_result(tags: Dict[str, List["Token"]]) -> exprs.Comparison:
    """Decode a result line from collected tags by matching _BEHAVIOR_THEN_RESULT_SPEC.

    Much inspired by 'machine_files.decode_disjunctive_comparisons', but this is
    simpler as there is no 'or', splitting is thus not needed.

    Arguments:
        tags: Key pieces of text found in the input.

    Returns:
        The expression equivalent to the matched text.
    """
    lhs = exprs.VariableValue(tags["first_var"][0])
    is_aux = tags["is_aux"][0]
    is_constraint = is_aux.tok_text == "is"

    compare_op = tags.get("compare_op")
    if compare_op is not None:
        varvalue = tags["varvalue"][0]
        units = tags.get("unit")
        rhs: exprs.DataValue
        if units is None:
            if sub_clause.guess_is_var(varvalue):
                rhs = exprs.VariableValue(varvalue)
            else:
                rhs = exprs.Value(varvalue, None)
        else:
            rhs = exprs.Value(varvalue, units[0])

        return exprs.RelationComparison(is_constraint, lhs, is_aux, compare_op[0], rhs)

    else:
        objective = tags["objective"][0]
        return exprs.ObjectiveComparison(lhs, is_aux, objective.tok_type == "MAXIMIZED_KW")


def _process_then_result(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    name_tok = tags["result_name"][0]
    expr = _decode_result(tags)

    current_comp = builder.compdef_builder.current_component
    assert current_comp is not None
    current_comp.behavior_then_result(name_tok, expr)


MACHINES: typing.MachineTripletList = [
    ("BEHAVIOR_HEADER_MACHINE", _BEHAVIOR_HEADER_SPEC, _process_behavior_header),
    ("BEHAVIOR_NAME_MACHINE", _BEHAVIOR_NAME_SPEC, _process_new_behavior_function),
    ("BEHAVIOR_CASE_MACHINE", _BEHAVIOR_CASE_SPEC, _process_new_case),
    ("BEHAVIOR_WHEN_MACHINE", _BEHAVIOR_WHEN_SPEC, _process_normal_when_start),
    (
        "BEHAVIOR_WHEN_OTHERWISE_MACHINE",
        _BEHAVIOR_WHEN_OTHERWISE_SPEC,
        _process_otherwise_when_start,
    ),
    (
        "BEHAVIOR_WHEN_CONDITION_MACHINE",
        _BEHAVIOR_WHEN_CONDITION_SPEC,
        _process_when_condition,
    ),
    ("BEHAVIOR_THEN_MACHINE", _BEHAVIOR_THEN_SPEC, _process_then_start),
    ("BEHAVIOR_THEN_RESULT_MACHINE", _BEHAVIOR_THEN_RESULT_SPEC, _process_then_result),
]
