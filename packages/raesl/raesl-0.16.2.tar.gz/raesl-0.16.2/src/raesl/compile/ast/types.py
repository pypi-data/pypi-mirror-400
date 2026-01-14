"""AST storage of types."""
from typing import TYPE_CHECKING, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from raesl.compile.ast.exprs import Value
    from raesl.compile.scanner import Token


class BaseType:
    """Base class of a type."""

    def get_units(self) -> Optional[Set[str]]:
        """Retrieve the units that may be used with values of the type.

        Returns:
            Set of unit names, set(['-']) if it has no units specified, or None if the
                type doesn't support units.
        """
        raise NotImplementedError("Implement me in {}.".format(repr(self)))


class ElementaryType(BaseType):
    """A type of a singular value in ESL. The allowed values in a parent type always
    have priority over the allowed values in a child type.

    Arguments:
        parent: Parent elementary type if specified.
        units: Allowed units of the type, should not have square brackets around the
            text.
        intervals: Disjunction of allowed ranges of the type, pairs of (lowerbound,
            upperbound) where one of the bounds may be None. Constants and enumerations
            are expressed as intervals with the same lower and upper bound.
    """

    def __init__(
        self,
        parent: Optional["ElementaryType"],
        units: List["Token"],
        intervals: Optional[List[Tuple[Optional["Value"], Optional["Value"]]]],
    ):
        super(ElementaryType, self).__init__()
        self.parent = parent
        self.units = units
        self.intervals = intervals

        assert parent is None or isinstance(parent, ElementaryType)

    def get_units(self):
        avail_units = set()
        etp = self
        while etp is not None:
            avail_units.update((unit.tok_text for unit in etp.units))
            etp = etp.parent

        if not avail_units:
            avail_units.add("-")
        return avail_units


class TypeDef:
    """A named type.

    Arguments:
        name: Name of the type definition.
        the_type: Type associated with the name.
    """

    def __init__(self, name: "Token", the_type: BaseType):
        self.name = name
        self.type = the_type


class CompoundField:
    """A named field in a Compound.

    Arguments:
        name: Name of the compound field.
        the_type: Type of the compound field.
    """

    def __init__(self, name: "Token", the_type: BaseType):
        self.name = name
        self.type = the_type


class Compound(BaseType):
    """A collection of named typed values. Note that a Compound cannot have parents,
    units, or intervals.

    Arguments:
        fields: Fields of the compound.
    """

    def __init__(self, fields: List[CompoundField]):
        super(Compound, self).__init__()
        self.fields = fields

    def get_units(self):
        return None
