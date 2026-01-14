"""Base class for goal and transformation processing to improve code sharing."""
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

from raesl.compile import diagnostics
from raesl.compile.ast import components, exprs
from raesl.compile.typechecking.utils import resolve_var_param_node

if TYPE_CHECKING:
    from raesl.compile.ast.components import ComponentInstance, Flow, SubClause, VarParam
    from raesl.compile.scanner import Token


class GoalTransformBaseBuilder:
    """Common base class for checking goals and transformations.

    Arguments:
        diag_store: Storage for found diagnostics.

    Attributes:
        reported_names: Names of flows with a reported error, to avoid duplicate error
            generation.
    """

    def __init__(self, diag_store: diagnostics.DiagnosticStore):
        self.diag_store = diag_store
        self.reported_names: Set[str] = set()

    def verify_verb_prepos(
        self, verb_tok: "Token", prepos_tok: "Token", vpps: Set[Tuple[str, str]]
    ):
        """Verify verb and pre-position and report an error if the combination does not
        exist.

        Arguments:
            verb_tok: Token holding the verb text.
            prepos_tok: Token holding the prepos text.
            vpps: Available combinations of verbs and prepositions.
        """
        vpp = (verb_tok.tok_text, prepos_tok.tok_text)
        if vpp not in vpps:
            loc = verb_tok.get_location()
            self.diag_store.add(diagnostics.E211(vpp[0], vpp[1], location=loc))

    def verify_flows(self, flows: List["Flow"], vps: Dict[str, "VarParam"]) -> bool:
        """Check that each flow exists as variable or parameter. Update the link
        in the Flow object to point to the matching variable or parameter.

        Arguments:
            flows: Flows to check.
            vps: Available variables and parameters in the component.

        Returns:
            Whether all flows can be matched to a variable or parameter.
        """
        is_good = True
        for flow in flows:
            node = resolve_var_param_node(flow.name_tok, vps, self.reported_names, self.diag_store)
            if node is None:
                is_good = False
            else:
                flow.flow_node = node

        return is_good

    def resolve_component(
        self, compinst_tok: "Token", cinsts: Dict[str, "ComponentInstance"]
    ) -> Optional["ComponentInstance"]:
        """Find a component instance with the provided instance name. If it exists,
        return it, else report an error and return None, indicating failure.
        """
        compinst = cinsts.get(compinst_tok.tok_text)
        if compinst is None:
            loc = compinst_tok.get_location()
            self.diag_store.add(
                diagnostics.E203("component instance", name=compinst_tok.tok_text, location=loc)
            )

        return compinst

    def check_form(
        self,
        sect_name: str,
        kind: str,
        doesaux: "Token",
        sub_clauses: List["SubClause"],
    ):
        """Check whether the requirement or constraint form of the text is correct with
        respect to the containing section.

        Arguments:
            sect_name: Name of the section (goal or transformation).
            kind: Kind of section containing the text (requirement or constraint).
            doesaux: Token in the formulation that is either 'does' or one of the
                auxiliary verbs.
            sub_clauses: Sub clauses belong to the requirement or constraint.
        """
        # None of the possible diagnostics is considered to be fatal, so nothing is
        # returned.

        # Verify uniqueness of subclause labels.
        subclauses_by_label: Dict[str, List["SubClause"]] = defaultdict(list)
        for sub in sub_clauses:
            subclauses_by_label[sub.label_tok.tok_text].append(sub)
        for clauses in subclauses_by_label.values():
            if len(clauses) > 1:
                locs = [sub.label_tok.get_location() for sub in clauses]
                name = clauses[0].label_tok.tok_text
                self.diag_store.add(
                    diagnostics.E200(name, "subclause label", location=locs[0], dupes=locs)
                )

        # Check kind-specific requirements.
        if kind == components.CONSTRAINT:
            if doesaux.tok_type != "DOES_KW":
                loc = doesaux.get_location()
                self.diag_store.add(
                    diagnostics.E212(
                        "constraint",
                        doesaux.tok_text,
                        "'does'",
                        name=sect_name,
                        location=loc,
                    )
                )

            for sub in sub_clauses:
                self._check_constraint_expr(sub.expr)

        else:
            assert kind == components.REQUIREMENT
            if doesaux.tok_type == "DOES_KW":
                loc = doesaux.get_location()
                self.diag_store.add(
                    diagnostics.E212(
                        "requirement",
                        doesaux.tok_text,
                        "one of 'must', 'shall', 'should', 'could', or 'won't'",
                        name=sect_name,
                        location=loc,
                    )
                )

            for sub in sub_clauses:
                self._check_requirement_expr(sub.expr)

    def _check_constraint_expr(
        self,
        expr: Union[exprs.Disjunction, exprs.RelationComparison, exprs.ObjectiveComparison],
    ):
        """Check whether the subclauses have the proper form for a constraint section.
        Report an error if something wrong is found.
        """
        if isinstance(expr, exprs.Disjunction):
            for child in expr.childs:
                self._check_constraint_expr(child)

        elif isinstance(expr, exprs.RelationComparison):
            if expr.isaux_tok.tok_type != "IS_KW":
                loc = expr.isaux_tok.get_location()
                self.diag_store.add(
                    diagnostics.E212("subclause", expr.isaux_tok.tok_text, "'is'", location=loc)
                )

            if expr.math_compare == "~":
                loc = expr.cmp_tok.get_location()
                self.diag_store.add(
                    diagnostics.E212("subclause", "approximately", "hard limits", location=loc)
                )

        elif isinstance(expr, exprs.ObjectiveComparison):
            loc = expr.aux_tok.get_location()
            if expr.maximize:
                obj_text = "maximize"
            else:
                assert expr.minimize
                obj_text = "minimize"
            self.diag_store.add(
                diagnostics.E212("subclause", obj_text, "hard limits", location=loc)
            )

        else:
            assert False, "Found unexpected expression node :" + repr(expr)

    def _check_requirement_expr(
        self,
        expr: Union[exprs.Disjunction, exprs.RelationComparison, exprs.ObjectiveComparison],
    ):
        """Check whether the subclauses have the proper form for a requirement section.
        Report an error if something wrong is found.
        """
        if isinstance(expr, exprs.Disjunction):
            for child in expr.childs:
                self._check_requirement_expr(child)

        elif isinstance(expr, exprs.RelationComparison):
            if expr.isaux_tok.tok_type == "IS_KW":
                loc = expr.isaux_tok.get_location()
                self.diag_store.add(
                    diagnostics.E212(
                        "subclause",
                        "is",
                        "'must/shall/should/could/won't be'",
                        location=loc,
                    )
                )

        elif isinstance(expr, exprs.ObjectiveComparison):
            pass  # Is OK in a requirement.

        else:
            assert False, "Found unexpected expression node :" + repr(expr)
