"""Library with common parts of line matchers."""
from typing import List

from raesl.compile.machine_files.utils import make_loc_names


def get_auxiliary_verb_part(start_loc: str, end_1locs: List[str], tagname: str) -> str:
    """Part implementing the 'auxiliary-verb' rule.

    auxiliary-verb ::=
        "shall" | "must" | "should" | "could" | "won't"
    """
    assert len(end_1locs) == 1

    text = """\
        {start} -> {end} [SHALL_KW] tag={tagname};
        {start} -> {end} [MUST_KW] tag={tagname};
        {start} -> {end} [SHOULD_KW] tag={tagname};
        {start} -> {end} [COULD_KW] tag={tagname};
        {start} -> {end} [WONT_KW] tag={tagname};
    """
    return text.format(start=start_loc, end=end_1locs[0], tagname=tagname)


def get_does_auxiliary_verb_part(start_loc: str, end_1locs: List[str], tagname: str) -> str:
    """State machine part that implements:

    "does" | auxiliary-verb
    """
    assert len(end_1locs) == 1

    text = """\
        {start} -> {end} [DOES_KW] tag={tagname};
    """ + get_auxiliary_verb_part(
        start_loc, [end_1locs[0]], tagname
    )

    return text.format(start=start_loc, end=end_1locs[0], tagname=tagname)


def get_is_auxiliary_verb_part(
    start_loc: str, end_1locs: List[str], tagname: str, prefix: str = ""
) -> str:
    """State machine part implementing:

    "is" | auxiliary-verb "be"
    """
    assert len(end_1locs) == 1

    locs = {"start": start_loc, "end": end_1locs[0], "tagname": tagname}
    locs.update(make_loc_names(prefix, "isauxloc", 1))

    text = """\
        {isauxloc1};

        {start} -> {end} [IS_KW] tag={tagname};
        {isauxloc1} -> {end} [BE_KW];
    """ + get_auxiliary_verb_part(
        start_loc, [locs["isauxloc1"]], tagname
    )

    return text.format(**locs)


def get_argument_references_part(
    start_loc: str, end_1locs: List[str], tagname: str, prefix: str = ""
) -> str:
    """State machine part implementing the 'argument-references' rule.

    argument-references ::=
        argument-name { and-connector argument-name } \n

    and-connector ::=
        "and" | "," | "," "and"
    """
    assert len(end_1locs) == 1

    locs = {"start": start_loc, "end": end_1locs[0], "tagname": tagname}
    locs.update(make_loc_names(prefix, "argrefs", 1))

    text = """\
        {argrefs1};

        {start}    -> {end}      [DOTTEDNAME] tag={tagname};
        {end}      -> {start}    [AND_KW];
        {end}      -> {argrefs1} [COMMA_TK];
        {argrefs1} -> {end}      [DOTTEDNAME] tag={tagname};
        {argrefs1} -> {start}    [AND_KW];
    """

    return text.format(**locs)


def get_compare_op_part(
    start_loc: str, end_1locs: List[str], tagname: str, prefix: str = ""
) -> str:
    """State machine part implementing the 'compare-op' rule.

    compare-op ::=
        "smaller" "than" | "greater" "than" | "not" "equal" "to" |
        "equal" "to" | "at" "least" | "at" "most" | "approximately"
    """
    assert len(end_1locs) == 1

    locs = {"start": start_loc, "end": end_1locs[0], "tagname": tagname}
    locs.update(make_loc_names(prefix, "cmp", 5))

    text = """\
        cmp1; cmp2; cmp3; cmp4; cmp5;

        {start} -> cmp1 [SMALLER_KW] tag={tagname};
        {start} -> cmp1 [GREATER_KW] tag={tagname};
            cmp1 -> {end} [THAN_KW];
        {start} -> cmp2 [EQUAL_KW] tag={tagname};
            cmp2 -> {end} [TO_KW];
        {start} -> cmp3 [NOT_KW] tag={tagname};
            cmp3 -> cmp4 [EQUAL_KW];
            cmp4 -> {end} [TO_KW];
        {start} -> cmp5 [AT_KW];
            cmp5 -> {end} [LEAST_KW] tag={tagname};
            cmp5 -> {end} [MOST_KW] tag={tagname};
        {start} -> {end} [APPROXIMATELY_KW] tag={tagname};
    """

    return text.format(**locs)


def get_disjunctive_comparison_part(start_loc: str, end_2locs: List[str], prefix: str = "") -> str:
    """State machine part implementing the 'comparison-rule-line' comparisons.

    comparison-rule-line ::=
        comparison { "or" comparison }

    comparison ::=
        argument-name ( constraint-rule-literal | requirement-rule-literal )

    constraint-rule-literal ::=
        "is" compare-op bound

    requirement-rule-literal ::=
        auxiliary-verb "be" ( compare-op bound | objective )

    compare-op ::=
        "smaller" "than" | "greater" "than" | "not" "equal" "to" |
        "equal" "to" | "at" "least" | "at" "most" | "approximately"

    bound ::=
        argument-name | VALUE [ UNIT ] | "t.b.d." [ UNIT ]

    objective ::=
        "maximized" | "minimized"
    """
    assert len(end_2locs) == 2

    locs = {"start": start_loc, "end1": end_2locs[0], "end2": end_2locs[1]}
    locs.update(make_loc_names(prefix, "dis", 3))

    text = (
        """\
        {dis1}; {dis2}; {dis3};

        {start} -> {dis1} [DOTTEDNAME] tag=first_var;
    """
        + get_is_auxiliary_verb_part(locs["dis1"], [locs["dis2"]], tagname="is_aux")
        + """\
        {dis2} -> {end2} [MAXIMIZED_KW] tag=objective;
        {dis2} -> {end2} [MINIMIZED_KW] tag=objective;
    """
        + get_compare_op_part(locs["dis2"], [locs["dis3"]], tagname="compare_op")
        + """\
        {dis3} -> {end1} [NONCOMMA] tag=varvalue;
        {end1} -> {end2} [NONCOMMA] tag=unit;

        {end1} -> {start} [OR_KW] tag=or;
        {end2} -> {start} [OR_KW] tag=or;
    """
    )

    return text.format(**locs)
