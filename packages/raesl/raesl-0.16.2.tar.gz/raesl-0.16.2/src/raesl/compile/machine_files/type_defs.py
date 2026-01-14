"""Line matcher state machines for type definitions."""
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, cast

from raesl.compile.ast import exprs
from raesl.compile.machine_files import typing
from raesl.compile.machine_files.utils import get_one, get_optional, make_loc_names

if TYPE_CHECKING:
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder


def get_unit_specification_part(start_loc: str, end_1locs: List[str], prefix: str = "") -> str:
    """State machine part implementing the 'unit-specification' rule.

    unit-specification ::=
        "with" ( "unit" | "units" ) UNIT-NAME { "," UNIT-NAME }
    """
    assert len(end_1locs) == 1

    locs = {
        "start": start_loc,
        "end": end_1locs[0],
    }
    locs.update(make_loc_names(prefix, "uspec", 2))

    text = """\
        {uspec1}; {uspec2};

        {start} -> {uspec1} [WITH_KW];
        {uspec1} -> {uspec2} [UNIT_KW] tag=has_unit_spec;
        {uspec2} -> {end} [NONCOMMA] tag=unit_name;
        {end} -> {uspec2} [COMMA_TK];
    """
    return text.format(**locs)


def _convert_unit_spec(tags: Dict[str, List["Token"]]) -> Optional[List["Token"]]:
    """Convert a unit specification to a list of unit names, if it exists."""
    if "has_unit_spec" not in tags:
        return None

    return tags["unit_name"]


def get_enumeration_specification_part(
    start_loc: str, end_2locs: List[str], prefix: str = ""
) -> str:
    """State machine part implementing the 'enumeration-specification' rule.

    enumeration-specification ::=
        "is" "an" "enumeration" "of" VALUE [ UNIT ] { "," VALUE [ UNIT ]}
    """
    assert len(end_2locs) == 2

    lenum_locs = make_loc_names(prefix, "lenum", 2)
    locs = {
        "start": start_loc,
        "end": lenum_locs["lenum2"],
    }
    locs.update(lenum_locs)

    text = """
        {lenum1}; {lenum2};

        {start} -> {lenum1} [IS_KW];
        {lenum1} -> {end} [A_KW];
    """
    text = text.format(**locs)
    return text + get_short_enumeration_specification_part(locs["end"], end_2locs, prefix)


def get_short_enumeration_specification_part(
    start_loc: str, end_2locs: List[str], prefix: str = ""
) -> str:
    """State machine part implementing the short 'enumeration-specification' rule.

    short-enumeration-specification ::=
        "enumeration" "of" VALUE [ UNIT ] { "," VALUE [ UNIT ]}
    """
    assert len(end_2locs) == 2

    locs = {
        "start": start_loc,
        "end1": end_2locs[0],
        "end2": end_2locs[1],
    }
    locs.update(make_loc_names(prefix, "enum", 2))

    text = """\
        {enum1}; {enum2};

        {start} -> {enum1} [ENUMERATION_KW] tag=has_enum_spec;
        {enum1} -> {enum2} [OF_KW];
        {enum2} -> {end1} [NONCOMMA] tag=enum_value;
        {end1} -> {end2} [NONCOMMA] tag=enum_unit;

        {end1} -> {enum2} [COMMA_TK];
        {end2} -> {enum2} [COMMA_TK];
    """
    return text.format(**locs)


def _convert_enum_spec(tags: Dict[str, List["Token"]]) -> Optional[List[exprs.Value]]:
    """Convert an enumeration specification to a number of values if it exists in the
    given tags.

    Arguments:
        tags: Tags from the matched line.

    Returns:
        Values of the enumeration.
    """
    if "has_enum_spec" not in tags:
        return None

    offsets = cast(List[Optional[int]], [tok.offset for tok in tags["enum_value"]]) + [None]

    values = []
    unit_tags = tags.get("enum_unit", [])
    for i, val in enumerate(tags["enum_value"]):
        unit = get_optional(unit_tags, val.offset, offsets[i + 1])
        values.append(exprs.Value(val, unit))
    return values


def get_interval_specification_part(start_loc: str, end_4locs: List[str], prefix: str = "") -> str:
    """State machine part implementing the 'interval-specification' rule.

    interval-specification ::=
        "of" interval { "or" interval }
    """
    assert len(end_4locs) == 4

    locs = {
        "start": start_loc,
        "end1": end_4locs[0],
        "end2": end_4locs[1],
        "end3": end_4locs[2],
        "end4": end_4locs[3],
    }
    locs.update(make_loc_names(prefix, "intval", 6))

    text = """\
        {intval1}; {intval2}; {intval3}; {intval4}; {intval5}; {intval6};

        {start} -> {intval1} [OF_KW] tag=has_intval_spec;

        {intval1} -> {intval2} [AT_KW];
        {intval2} -> {intval3} [LEAST_KW];
        {intval3} -> {end1}    [NONCOMMA] tag=lowerbound_value;
        {end1}    -> {end2}    [NONCOMMA] tag=lowerbound_unit;

        {end1}    -> {intval4} [AND_KW] tag=and;
        {end2}    -> {intval4} [AND_KW] tag=and;

        {intval4} -> {intval5} [AT_KW];
        {intval5} -> {intval6} [MOST_KW];
        {intval6} -> {end3}    [NONCOMMA] tag=upperbound_value;
        {end3}    -> {end4}    [NONCOMMA] tag=upperbound_unit;

        {intval2} -> {intval6} [MOST_KW]; # Skip 'at least'

        {end1}    -> {intval1} [OR_KW] tag=or; # 'or' after lower bound
        {end2}    -> {intval1} [OR_KW] tag=or;

        {end3}   -> {intval1}  [OR_KW] tag=or; # 'or' after upper bound
        {end4}   -> {intval1}  [OR_KW] tag=or;
    """
    return text.format(**locs)


def _convert_interval_spec(
    tags: Dict[str, List["Token"]]
) -> Optional[List[Tuple[Optional[exprs.Value], Optional[exprs.Value]]]]:
    """Convert an interval specification of a line to a (disjunctive) sequence of
    expressions, if such a specification exists in the given tags.
    """
    if "has_intval_spec" not in tags:
        return None

    ors = tags.get("or", [])
    offsets = cast(List[Optional[int]], [None]) + [tok.offset for tok in ors] + [None]

    boundaries = []
    low_vals = tags.get("lowerbound_value", [])
    low_units = tags.get("lowerbound_unit", [])
    high_vals = tags.get("upperbound_value", [])
    high_units = tags.get("upperbound_unit", [])
    for i in range(0, len(offsets) - 1):
        start_offset, end_offset = offsets[i], offsets[i + 1]
        low_val = get_optional(low_vals, start_offset, end_offset)
        low_unit = get_optional(low_units, start_offset, end_offset)
        high_val = get_optional(high_vals, start_offset, end_offset)
        high_unit = get_optional(high_units, start_offset, end_offset)
        assert low_val or high_val

        low_bound: Optional[exprs.Value]
        high_bound: Optional[exprs.Value]
        if low_val:
            low_bound = exprs.Value(low_val, low_unit)
        else:
            low_bound = None

        if high_val:
            high_bound = exprs.Value(high_val, high_unit)
        else:
            high_bound = None

        boundaries.append((low_bound, high_bound))

    return boundaries


def get_constant_specification_part(start_loc: str, end_2locs: List[str], prefix: str = "") -> str:
    """State machine part implementing the 'constant-specification' rule.

    constant-specification ::=
        "equal" "to" VALUE [ UNIT ]
    """
    assert len(end_2locs) == 2

    locs = {
        "start": start_loc,
        "end1": end_2locs[0],
        "end2": end_2locs[1],
    }
    locs.update(make_loc_names(prefix, "const", 4))

    text = """\
        {const1}; {const2};

        {start}  -> {const1} [EQUAL_KW] tag=has_constant_spec;
        {const1} -> {const2} [TO_KW];
        {const2} -> {end1} [NONCOMMA] tag=const_value;
        {end1}   -> {end2} [NONCOMMA] tag=const_unit;
    """
    return text.format(**locs)


def _convert_constant_spec(tags: Dict[str, List["Token"]]) -> Optional[exprs.Value]:
    """Convert a constant specification of a line to a Value if it exits."""
    if "has_constant_spec" not in tags:
        return None

    val = get_one(tags["const_value"], None, None)
    unit = get_optional(tags.get("const_unit", []), None, None)
    bound = exprs.Value(val, unit)
    return bound


_DEFINE_TYPE_SPEC = """
define_type:
    start initial;
    start -> s1 [DEFINE_KW] tag=define;
    s1 -> s2 [TYPE_KW];

    end accept=define_type;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def _process_define_type(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["define"][0], True)


_NEW_TYPE_SPEC = (
    """
new_type:
    start initial;
    end accept=new_type;

    start -> s1 [NAME] tag=new_type;
    s1 -> end [NL_TK];
    s1 -> end [EOF_TK];
"""
    + get_enumeration_specification_part("s1", ["s2", "s3"])
    + """\
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
    s3 -> end [NL_TK];
    s3 -> end [EOF_TK];
"""
    + get_unit_specification_part("s1", ["s4"])
    + """\
    s4 -> end [NL_TK];
    s4 -> end [EOF_TK];
"""
    + get_interval_specification_part("s1", ["s5", "s6", "s7", "s8"])
    + """\
    s5 -> end [NL_TK];
    s5 -> end [EOF_TK];
    s6 -> end [NL_TK];
    s6 -> end [EOF_TK];
    s7 -> end [NL_TK];
    s7 -> end [EOF_TK];
    s8 -> end [NL_TK];
    s8 -> end [EOF_TK];
"""
    + get_constant_specification_part("s1", ["s9", "s10"])
    + """\
    s9 -> end [NL_TK];
    s9 -> end [EOF_TK];
    s10 -> end [NL_TK];
    s10 -> end [EOF_TK];
"""
)


def _process_new_type_def(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    new_type = tags["new_type"][0]
    enum_spec = _convert_enum_spec(tags)
    unit_spec = _convert_unit_spec(tags)
    ival_spec = _convert_interval_spec(tags)
    cons_spec = _convert_constant_spec(tags)
    builder.add_typedef(new_type, None, enum_spec, unit_spec, ival_spec, cons_spec)


_TYPE_IS_A_TYPE_SPEC = (
    """
type_is_type:
    start initial;
    end accept=type_is_type;

    start -> s1 [NAME] tag=new_type;
    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [NAME] tag=old_type;
    s4 -> end [NL_TK];
    s4 -> end [EOF_TK];
"""
    + get_unit_specification_part("s4", ["s5"])
    + """\
    s5 -> end [NL_TK];
    s5 -> end [EOF_TK];
"""
    + get_interval_specification_part("s4", ["s6", "s7", "s8", "s9"])
    + """\
    s6 -> end [NL_TK];
    s6 -> end [EOF_TK];
    s7 -> end [NL_TK];
    s7 -> end [EOF_TK];
    s8 -> end [NL_TK];
    s8 -> end [EOF_TK];
    s9 -> end [NL_TK];
    s9 -> end [EOF_TK];
"""
    + get_constant_specification_part("s4", ["s10", "s11"])
    + """\
    s10 -> end [NL_TK];
    s10 -> end [EOF_TK];
    s11 -> end [NL_TK];
    s11 -> end [EOF_TK];
"""
)


def _process_derived_type_def(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    new_type = tags["new_type"][0]
    exist_type = tags["old_type"][0]
    enum_spec = _convert_enum_spec(tags)
    unit_spec = _convert_unit_spec(tags)
    ival_spec = _convert_interval_spec(tags)
    cons_spec = _convert_constant_spec(tags)
    builder.add_typedef(new_type, exist_type, enum_spec, unit_spec, ival_spec, cons_spec)


_BUNDLE_TYPE_SPEC = """
bundle_type:
    start initial;
    start -> s1 [NAME] tag=bundle_name;
    s1 -> s2 [IS_KW];
    s2 -> s3 [A_KW];
    s3 -> s4 [BUNDLE_KW];
    s4 -> s5 [OF_KW];

    end accept=bundle_type;
    s5 -> end [NL_TK];
    s5 -> end [EOF_TK];
"""


def _process_bundle_type(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.new_bundle_type(tags["bundle_name"][0])


_BUNDLE_FIELD_SPEC = """
bundle_field:
    start initial;
    end accept=bundle_field;

    start -> s1 [STAR_TK];
    s1 -> s2 [NAME] tag=field_name;
    s2 -> s3 [IS_KW];
    s3 -> s4 [A_KW];

    s4 -> s5 [NAME] tag=field_type;

    s5 -> end [NL_TK];
    s5 -> end [EOF_TK];
"""


def _process_bundle_field(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    field_name = tags["field_name"][0]
    field_type = tags["field_type"][0]
    builder.add_bundle_field(field_name, field_type)


MACHINES: typing.MachineTripletList = [
    ("DEFINE_TYPE_MACHINE", _DEFINE_TYPE_SPEC, _process_define_type),
    ("NEW_TYPE_MACHINE", _NEW_TYPE_SPEC, _process_new_type_def),
    ("TYPE_IS_A_TYPE_MACHINE", _TYPE_IS_A_TYPE_SPEC, _process_derived_type_def),
    ("BUNDLE_TYPE_MACHINE", _BUNDLE_TYPE_SPEC, _process_bundle_type),
    ("BUNDLE_FIELD_MACHINE", _BUNDLE_FIELD_SPEC, _process_bundle_field),
]
