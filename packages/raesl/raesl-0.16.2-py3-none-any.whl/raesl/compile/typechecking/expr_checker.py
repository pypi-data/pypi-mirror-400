"""Check that expressions comply with the language requirements."""
from typing import TYPE_CHECKING, Dict, Optional, Set, Tuple, Union

from raesl.compile import diagnostics
from raesl.compile.ast import components
from raesl.compile.ast.exprs import (
    Disjunction,
    ObjectiveComparison,
    RelationComparison,
    Value,
    VariableValue,
)
from raesl.compile.ast.nodes import VarNode
from raesl.compile.ast.types import Compound
from raesl.compile.typechecking.type_checker import check_type
from raesl.compile.typechecking.utils import resolve_var_param_node

if TYPE_CHECKING:
    from raesl.compile.ast.exprs import DataValue, Expression
    from raesl.compile.ast.types import BaseType
    from raesl.compile.scanner import Token


class ExprChecker:
    """Class for checking expressions.

    Arguments:
        vps: Variables and parameters defined in the expression context.
        diag_store: Storage for found diagnostics.

    Attributes:
        reported_names: Names of variables and variable parts that have been reported
            as error, to avoid duplicate error messages.
    """

    def __init__(
        self,
        vps: Dict[str, Union[components.VarParam]],
        diag_store: diagnostics.DiagnosticStore,
    ):
        self.vps = vps
        self.diag_store = diag_store
        self.reported_names: Set[str] = set()

    def check_expr(self, expr: "Expression") -> bool:
        """Check whether the expression follows all rules of the ESL language.

        Arguments:
            expr: Expression to check.

        Returns:
            Whether the expression is considered to be sufficiently correct to continue
                checking other parts of the construct around the expression.
        """
        is_ok = True
        notdone = [expr]
        while notdone:
            expr = notdone.pop()

            if isinstance(expr, Disjunction):
                # Break the disjunction down to checking its set of child expressions.
                notdone.extend(expr.childs)
                continue

            elif isinstance(expr, RelationComparison):
                if not self.check_relation_comparison(expr):
                    is_ok = False

                continue

            elif isinstance(expr, ObjectiveComparison):
                if not self._check_variable(expr.lhs_var):
                    is_ok = False
                continue

            assert False, "Unexpected expression '{}' found.".format(repr(expr))

        return is_ok

    def check_relation_comparison(self, expr: RelationComparison) -> bool:
        """Check the provided relation comparison.

        Arguments:
            expr: Relation comparison to check.

        Returns:
            Whether the expression is considered to be sufficiently correct.
        """
        # Check both sides.
        left_side = self._check_relation_side(expr.lhs_var)
        right_side = self._check_relation_side(expr.rhs_varval)

        if left_side is None or right_side is None:
            return False

        lhs_pos, lhs_type, lhs_units = left_side
        rhs_pos, rhs_type, rhs_units = right_side

        assert lhs_units is None or len(lhs_units) > 0, "lhs var {} has wrong units '{}'".format(
            expr.lhs_var, lhs_units
        )
        assert rhs_units is None or len(rhs_units) > 0, "rhs varval {} has wrong units '{}'".format(
            expr.rhs_varval, rhs_units
        )

        if isinstance(lhs_type, Compound) or isinstance(
            rhs_type, Compound
        ):  # or rhs_type is Compound:
            self.diag_store.add(
                diagnostics.E228(
                    lhs_pos.get_location(),
                    rhs_pos.get_location(),
                    "contains one or more bundles",
                )
            )

        # Check type compatibility.
        if lhs_type and rhs_type:
            # The lhs and rhs must be compatible in left -> right or in
            # right -> left direction. Additional subtype limits isn't a
            # problem, although it may result in a comparison that can
            # never hold.
            lhs_input = (lhs_pos, lhs_type)
            rhs_input = (rhs_pos, rhs_type)
            diagnostic = check_type(
                supertype=lhs_input, subtype=rhs_input, allow_subtype_limits=True
            )
            if diagnostic:
                diagnostic = check_type(
                    supertype=rhs_input, subtype=lhs_input, allow_subtype_limits=True
                )

                if diagnostic:
                    # A problem in both direction, lhs an rhs cannot be compared.
                    self.diag_store.add(
                        diagnostics.E210(
                            lhs_pos.get_location(),
                            rhs_pos.get_location(),
                            "are not compatible",
                        )
                    )

        # Both sets empty is ok ([-] vs [-])
        if lhs_units or rhs_units:
            # Or if at least one unit is listed anywhere, it must have a common unit.
            lhs_units = set() if lhs_units is None else lhs_units
            rhs_units = set() if rhs_units is None else rhs_units
            if not lhs_units.intersection(rhs_units):
                lhs_loc = lhs_pos.get_location()
                rhs_loc = rhs_pos.get_location()
                self.diag_store.add(
                    diagnostics.E210(lhs_loc, rhs_loc, reason="have no shared unit")
                )

        return True

    def _check_relation_side(
        self, side: "DataValue"
    ) -> Optional[Tuple["Token", Optional["BaseType"], Optional[Set[str]]]]:
        """Check one side in a relation comparison.

        Arguments:
            side: Side to check.

        Returns:
            Information about the checked side. None means an error has been reported,
                otherwise a triplet of token, type, and supported units is returned
                for as far as the side supports each notion.
        """
        if isinstance(side, Value):
            units = side.get_units()
            assert units is None or len(units) > 0, "Value {} has wrong units '{}'".format(
                side, units
            )
            return side.value, None, units

        else:
            assert isinstance(side, VariableValue)
            if not self._check_variable(side):
                return None

            assert isinstance(side.var_node, VarNode)
            typ = side.var_node.the_type
            units = typ.get_units()
            assert units is None or len(units) > 0, "Type {} has wrong units '{}'".format(
                typ, units
            )

            return side.var_tok, typ, units

    def _check_variable(self, var: VariableValue) -> bool:
        """Check that the variable exists in the context.

        Arguments:
            var: Variable to check.

        Returns:
            Whether the variable was found.
        """
        var_node = resolve_var_param_node(
            var.var_tok, self.vps, self.reported_names, self.diag_store
        )
        if var_node is None:
            return False

        var.var_node = var_node
        return True
