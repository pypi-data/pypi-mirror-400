"""Expressions to store and reason about values and boundaries."""

from typing import TYPE_CHECKING, Optional, Sequence, Set

if TYPE_CHECKING:
    from raesl.compile.ast.nodes import VarNode
    from raesl.compile.scanner import Token
    from raesl.types import Location


class DataValue:
    """Some kind of data value. Do not use this, but use a derived class instead."""

    def get_units(self) -> Optional[Set[str]]:
        """Obtain the units of the value. Gives a set of names without square brackets
        where lack of units results in the empty set, and not supporting units gives
        None.

        Returns:
            Names of the available units without square brackets or None.
        """
        raise NotImplementedError("Implement me in {}".format(repr(self)))


class Value(DataValue):
    """A value with an optional unit. Don't modify these objects in-place, create a new
    object instead.

    Arguments:
        value: Stored value as text.
        unit: Either None or text describing the unit. Treat as read-only, as changing
            it may break the cache.

    Attributes:
        _unit_cache: Units of the literal after normalizing self.unit. Computed on
            demand.
    """

    def __init__(self, value: "Token", unit: Optional["Token"] = None):
        super(Value, self).__init__()
        self.value = value
        self.unit = unit
        self._unit_cache: Optional[Set[str]] = None  # Lazily computed.

        assert self.unit is None or self.unit.tok_text not in ("", "[]")

    def get_units(self) -> Optional[Set[str]]:
        # Updates self._unit_cache on first call.
        if self._unit_cache is None:
            if self.unit is None:
                self._unit_cache = set(["-"])
            elif self.unit.tok_text.startswith("[") and self.unit.tok_text.endswith("]"):
                self._unit_cache = set([self.unit.tok_text[1:-1]])
            else:
                self._unit_cache = set([self.unit.tok_text])

        return self._unit_cache

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        if self.value.tok_text != other.value.tok_text:
            return False
        if self.unit is None and other.unit is None:
            return True
        if self.unit is not None and other.unit is not None:
            return self.unit.tok_text == other.unit.tok_text
        return False

    def __repr__(self):
        if self.unit is None:
            return "Value({})".format(self.value.tok_text)
        return "Value({}, {})".format(self.value.tok_text, self.unit.tok_text)


class VariableValue(DataValue):
    """Class representing a variable or parameter as value.

    Arguments:
        var_tok: Token stating the possibly dotted name of the variable.

    Attributes:
        var_node: If not None, the node represented by the object. Set during type checking.
    """

    def __init__(self, var_tok: "Token"):
        self.var_tok = var_tok

        self.var_node: Optional["VarNode"] = None

    def get_units(self) -> Optional[Set[str]]:
        assert self.var_node is not None
        return self.var_node.the_type.get_units()


class Expression:
    """Base class of an expression."""


class Comparison(Expression):
    """Class storing a comparison.

    Arguments:
        is_constraint: Whether the comparison is considered to be a constraint rather
            than a requirement.
    """

    def __init__(self, is_constraint: bool):
        super(Comparison, self).__init__()
        self.is_constraint = is_constraint


_MATH_OP_TRANSLATE = {
    "LEAST_KW": ">=",
    "MOST_KW": "<=",
    "EQUAL_KW": "==",
    "NOT_KW": "!=",
    "SMALLER_KW": "<",
    "GREATER_KW": ">",
    "APPROXIMATELY_KW": "~",
}


class RelationComparison(Comparison):
    """A relation between a variable and either a value or a variable.

    Arguments:
        is_constraint: Whether the comparison is considered to be a constraint rather
            than a requirement.
        lhs_var: Left hand side variable being compared.
        isaux_tok: 'is' for a constraint, else the aux word for expressing strength
            of the comparison.
        cmp_tok: One of the key words that expression the comparison to perform.
        rhs_varval: Right hand side variable or value.

    Attributes:
        math_compare: Translated 'cmp_tok', with the ascii math text.
    """

    def __init__(
        self,
        is_constraint: bool,
        lhs_var: VariableValue,
        isaux_tok: "Token",
        cmp_tok: "Token",
        rhs_varval: DataValue,
    ):
        super(RelationComparison, self).__init__(is_constraint)
        self.lhs_var = lhs_var
        self.isaux_tok = isaux_tok
        self.cmp_tok = cmp_tok
        self.math_compare = _MATH_OP_TRANSLATE[cmp_tok.tok_type]
        self.rhs_varval = rhs_varval

    def get_location(self) -> "Location":
        """Return a location to point at the comparison for error reporting purposes."""
        return self.isaux_tok.get_location()


class ObjectiveComparison(Comparison):
    """An intended direction for a variable. Note that the 'maximize' parameter
    controls both the 'maximize' and 'minimize' desires.

    Arguments:
        lhs_var: Variable with the objective.
        aux_tok: One of the auxiliary verbs expressing strength of the objective.
        maximize: If set the comparison expresses the desire to maximize the variable.

    Attributes:
        minimize: Opposite of maximize.
    """

    def __init__(self, lhs_var: VariableValue, aux_tok: "Token", maximize: bool):
        super(ObjectiveComparison, self).__init__(False)
        self.lhs_var = lhs_var
        self.aux_tok = aux_tok
        self.maximize = maximize

    def get_location(self) -> "Location":
        """Return a location to point at the comparison for error reporting purposes."""
        return self.aux_tok.get_location()

    @property
    def minimize(self) -> bool:
        return not self.maximize


class Disjunction(Expression):
    """Disjunctive expression (also known as 'or' expression).
    It is true iff at least one of it child expressions is true.

    Arguments:
        childs: Child expressions of the disjunction. It is recommended to have at
            least two children in an object.
    """

    def __init__(self, childs: Sequence[Expression]):
        self.childs = childs
