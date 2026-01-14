"""Type checking.

Type compatibility
------------------
Type 'sub_type' is compatible with type 'super_type' if
- Type 'sub_type' is (possibly indirectly) derived from 'super_type'.
- Type 'sub_type' has no additional value constraints in the form of enumerations,
  upper or lower limits, or constants relative to 'super_type'.

The former condition ensures the values are fundamentally compatible. This
condition should always hold, the latter condition ensures that all possible
values of 'super_type' can also be expressed in 'sub_type'. This is particularly
relevant if 'sub_type' may receive data from the element with 'super_type'. If
data flow is in the other direction only, the second condition seems less
relevant.

Note that units are not relevant in this context. If the sub_type is a subtype of
of 'super_type', the former always has all units of the latter.

Relevant code type-classes
--------------------------
Several classes have or use types, or represent data of some type. These classes are

- raesl.compile.ast.types.ElementaryType (type of a single value).
- raesl.compile.ast.types.Compound (type of a bundle of values).
- raesl.compile.ast.nodes.ElementaryVarNode (data of an elementary type).
- raesl.compile.ast.nodes.CompoundVarNode (data of a bundle).
- raesl.compile.ast.nodes.GroupNode (data of a variable group).

where an ElementaryVarNode contains an ElementaryType, a CompoundVarNode
contains a Compound (type), and GroupNode eventually always points at
ElementaryVarNode or CompoundVarNode instances.

The entry_point 'check_type' accepts all the above kinds of objects.
"""

from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from raesl.compile import diagnostics
from raesl.compile.ast.nodes import CompoundVarNode, ElementaryVarNode, GroupNode, Node
from raesl.compile.ast.types import BaseType, Compound, ElementaryType

if TYPE_CHECKING:
    from raesl.compile.scanner import Token

TypeValue = Union[Node, BaseType]


class TypeData:
    """Tuple-like class to keep type data from one side together.

    Arguments:
        name_tok: Initial name of the value in the source, and point of use of the type.
        suffixes: Child texts after the initial name to indicate the subtype value
            being examined. See 'get_name' for a description of the suffixes.
        value: Type or node value being examined.
    """

    def __init__(self, name_tok: "Token", suffixes: List[str], value: TypeValue):
        self.name_tok = name_tok
        self.suffixes = suffixes
        self.value = value

    def get_name(self) -> str:
        """Construct a human-readable name of the point being examined.

        It consists of the initial name followed by zero or more suffixes, where
        a suffix can be one of the following
        - ".<childname>" for a child field in a bundle, or
        - "[<1-based index>]" for a variable in a variable group.

        Returns:
            The constructed name.
        """
        return self.name_tok.tok_text + "".join(self.suffixes)

    def drop_to_type(self):
        """For nodes, drop down to its type."""
        if isinstance(self.value, ElementaryVarNode):
            return TypeData(self.name_tok, self.suffixes, self.value.the_type)
        elif isinstance(self.value, CompoundVarNode):
            return TypeData(self.name_tok, self.suffixes, self.value.the_type)
        else:
            return self

    def expand(self):
        """Expand a sequence of values in 'self.value' to a sequence of child TypeData
        instances.
        """
        if isinstance(self.value, Compound):
            childs = []
            for field in self.value.fields:
                child_suffixes = self.suffixes + [".{}".format(field.name.tok_text)]
                child = TypeData(self.name_tok, child_suffixes, field.type)
                childs.append(child)
            return childs

        else:
            assert isinstance(self.value, GroupNode)
            childs = []
            for i, child_node in enumerate(self.value.child_nodes):
                child_suffixes = self.suffixes + ["[{}]".format(i + 1)]
                child = TypeData(self.name_tok, child_suffixes, child_node)
                childs.append(child)
            return childs


def check_type(
    subtype: Tuple["Token", TypeValue],
    supertype: Tuple["Token", TypeValue],
    allow_subtype_limits: bool = False,
) -> Optional[diagnostics.EslDiagnostic]:
    """Like 'check_type_unpacked', except the subtype and super-type data is packed in
    tuples.
    """
    subtok, subval = subtype
    supertok, superval = supertype
    return check_type_unpacked(subtok, subval, supertok, superval, allow_subtype_limits)


def check_type_unpacked(
    sub_nametok: "Token",
    sub_value: TypeValue,
    super_nametok: "Token",
    super_value: TypeValue,
    allow_subtype_limits: bool = False,
) -> Optional[diagnostics.EslDiagnostic]:
    """Check whether sub_value is a subtype of super_value. Iff allow_subtype_limits
    holds, the sub_value may have additional value constraints. Returns None if the
    sub_value is indeed a subtype of super_value, possibly taking additional value
    constraints into account. Otherwise it returns a problem description
    of how it fails.

    Arguments:
        sub_nametok: Text in the input of the sub_value, usually a variable.
        sub_value: Type or node of the sub value.
        super_nametok: Text in the input of the super_value, usually a variable.
        super_value: Type or node of the super value.
        allow_subtype_limits: Whether sub_value may have additional value constraints
            relative to super_value.

    Returns:
        None if sub_value is a subtype of super_value taking allow_subtype_limits
            into account, else a problem description of how it fails to have the
            subtype relation.
    """
    # Do some paranoia checks to ensure checking code does not crash on invalid data.
    assert sub_nametok is not None
    assert super_nametok is not None
    assert isinstance(
        sub_value,
        (ElementaryVarNode, CompoundVarNode, GroupNode, ElementaryType, Compound),
    ), "Weird sub value '{}'".format(sub_value)
    assert isinstance(
        super_value,
        (ElementaryVarNode, CompoundVarNode, GroupNode, ElementaryType, Compound),
    ), "Weird super value '{}'".format(super_value)

    subtype = TypeData(sub_nametok, [], sub_value)
    supertype = TypeData(super_nametok, [], super_value)
    return _check_type(subtype, supertype, allow_subtype_limits)


def _check_type(
    subtype: TypeData, supertype: TypeData, allow_subtype_limits: bool = False
) -> Optional[diagnostics.EslDiagnostic]:
    # Switch subtype and/or supertype from ElementaryVarNode or CompoundVarNode to its
    # type.
    subtype = subtype.drop_to_type()
    supertype = supertype.drop_to_type()

    # Trivially equal?
    if subtype.value is supertype.value:
        return None

    # Handle elementary types
    if isinstance(subtype.value, ElementaryType):
        if not isinstance(supertype.value, ElementaryType):
            # Element does not match with a bundle or variable group.
            return diagnostics.E220(subtype.get_name(), "bundle or variable group")
        else:
            # Compare elementary types
            return _check_elementaries(subtype, supertype, allow_subtype_limits)
    else:
        if isinstance(supertype.value, ElementaryType):
            return diagnostics.E220(supertype.get_name(), "bundle or variable group")

    # Else both are non-elementary types. They must be either Compound or GroupNode

    sub_childs: List[TypeData] = subtype.expand()
    super_childs: List[TypeData] = supertype.expand()

    sub_length = len(sub_childs)
    super_length = len(super_childs)
    if sub_length != super_length:
        return diagnostics.E221(
            "bundle and/or variable group variable",
            sub_length,
            super_length,
            location=subtype.name_tok.get_location(),
            references=[supertype.name_tok.get_location()],
        )

    # Equal length, check pairwise.
    for sub, sup in zip(sub_childs, super_childs):
        diag = _check_type(sub, sup, allow_subtype_limits)
        if diag is not None:
            return diag
    return None


def _check_elementaries(
    subtype: TypeData, supertype: TypeData, allow_subtype_limits: bool = False
) -> Optional[diagnostics.EslDiagnostic]:
    """Check sub/super type relation between two elementary types.

    Returns:
        None if subtype is a subtype of supertype taking allow_subtype_limits into
            account, otherwise it returns a diagnostic describing why the relation does
            not hold.
    """
    sub_val: ElementaryType = subtype.value
    sup_val: ElementaryType = supertype.value
    while True:
        if sup_val is sub_val:
            return None

        # Not the same, sub_val may be a derived type with further limitations.
        # Bail out if not allowed.
        if not allow_subtype_limits and sub_val.intervals is not None:
            return diagnostics.E222(
                subtype.get_name(),
                supertype.get_name(),
                location=subtype.name_tok.get_location(),
                other_loc=supertype.name_tok.get_location(),
            )

        # Walk sub_val up to its direct parent, and check again, unless we run out of
        # parent types.
        if sub_val.parent is None:
            # No more parents!
            return diagnostics.E223(
                subtype.get_name(),
                supertype.get_name(),
                "subtype",
                location=subtype.name_tok.get_location(),
                other_loc=supertype.name_tok.get_location(),
            )

        sub_val = sub_val.parent
