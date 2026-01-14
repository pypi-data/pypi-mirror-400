"""Line matcher for sub-clause lines."""
import re
import string
from typing import TYPE_CHECKING, Dict, List, Optional, cast

from raesl.compile.ast import components, exprs
from raesl.compile.machine_files.machine_parts import get_disjunctive_comparison_part
from raesl.compile.machine_files.utils import get_one, get_optional

if TYPE_CHECKING:
    from raesl.compile.scanner import Token


SUB_CLAUSE_SPEC = (
    """
sub_clause:
    start initial;
    start -> s1 [STAR_TK];
    s1 -> s2 [NAME] tag=subclause_label;
    s2 -> s3 [COLON_TK];
"""
    + get_disjunctive_comparison_part("s3", ["s4", "s5"])
    + """\
    finish accept=sub_clause;
    s4 -> finish [NL_TK];
    s4 -> finish [EOF_TK];
    s5 -> finish [NL_TK];
    s5 -> finish [EOF_TK];
"""
)


def guess_is_var(varvalue: "Token") -> bool:
    """Guess whether the provided token is a variable or a value.
    (Answer: If it is not "t.b.d." and starts with a letter it's a variable.)
    """
    text = varvalue.tok_text
    if re.fullmatch("[tT]\\.[Bb]\\.[dD]\\.", text):
        # Some form of TBD is not a variable.
        return False

    first = text[0]
    return first in string.ascii_lowercase or first in string.ascii_uppercase


def decode_disjunctive_comparisons(tags: Dict[str, List["Token"]]) -> exprs.Expression:
    """Decode tags of a matched 'machine_parts.get_disjunctive_comparison_part' part
    to an disjunction with comparisons.

    Arguments:
        tags: Extracted data from a match of the machine defined in
            'machine_parts.get_disjunctive_comparison_part'.

    Returns:
        The expression equivalent to the matched text.
    """
    split_offsets = (
        cast(List[Optional[int]], [None]) + [tok.offset for tok in tags.get("or", [])] + [None]
    )
    equations: List[exprs.Expression] = []

    unit_tags = tags.get("unit", [])
    compare_tags = tags.get("compare_op", [])
    for index in range(1, len(split_offsets)):
        start_offset = split_offsets[index - 1]
        end_offset = split_offsets[index]

        first_var = get_one(tags["first_var"], start_offset, end_offset)
        lhs = exprs.VariableValue(first_var)

        is_aux = get_one(tags["is_aux"], start_offset, end_offset)
        is_constraint = is_aux.tok_text == "is"

        comp: exprs.Comparison
        compare_op = get_optional(compare_tags, start_offset, end_offset)
        if compare_op is not None:
            varvalue = get_one(tags["varvalue"], start_offset, end_offset)
            unit = get_optional(unit_tags, start_offset, end_offset)

            rhs: exprs.DataValue
            if unit is None and guess_is_var(varvalue):
                rhs = exprs.VariableValue(varvalue)
            else:
                rhs = exprs.Value(varvalue, unit)

            comp = exprs.RelationComparison(is_constraint, lhs, is_aux, compare_op, rhs)
            equations.append(comp)

        else:
            objective = get_one(tags["objective"], start_offset, end_offset)

            comp = exprs.ObjectiveComparison(lhs, is_aux, objective.tok_type == "MAXIMIZED_KW")
            equations.append(comp)

    if len(equations) == 1:
        return equations[0]
    else:
        return exprs.Disjunction(equations)


def decode_subclause(tags: Dict[str, List["Token"]]) -> components.SubClause:
    """Decode tags of a matched subclauses line to one or more disjunctive equations.

    Arguments:
        tags: Extracted data from a match of the machine defined in SUB_CLAUSE_SPEC.

    Returns:
        The found subclause.
    """
    label = tags["subclause_label"][0]
    condition = decode_disjunctive_comparisons(tags)
    return components.SubClause(label, condition)
