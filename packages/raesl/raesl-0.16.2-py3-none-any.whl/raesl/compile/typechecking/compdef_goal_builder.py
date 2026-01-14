"""Code for collecting and adding goals to component definitions."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from raesl.compile.ast import components
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.expr_checker import ExprChecker
from raesl.compile.typechecking.goal_transform_base import GoalTransformBaseBuilder

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CompDefGoalBuilder(GoalTransformBaseBuilder):
    """Collect goals of a component from the parser, check them, and eventually add them
    to the surrounding component definition.

    Arguments:
        comp_child_builders: Child builders as retrieved from the parser.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        super(CompDefGoalBuilder, self).__init__(comp_child_builders.diag_store)
        self.goals: List[components.Goal] = []
        self.comp_child_builders = comp_child_builders
        self.goal_kind: Optional[str] = None

    def new_goal_header(self, goal_kind: "Token"):
        """New goal header line found.

        Arguments:
            goal_kind: Kind of goals that will follow.
        """
        if goal_kind.tok_type == "GOAL_REQUIREMENT_KW":
            self.goal_kind = components.REQUIREMENT
        else:
            assert goal_kind.tok_type == "GOAL_CONSTRAINT_KW"
            self.goal_kind = components.CONSTRAINT

    def add_goal(self, goal: components.Goal):
        """New goal has been found by the parser, add it to the found goals.

        Arguments:
            goal: Goal to add.
        """
        assert self.goal_kind is not None
        goal.goal_kind = self.goal_kind
        self.goals.append(goal)

    def add_goal_subclause(self, sub_clause: components.SubClause):
        """Subclause of the last goal has been found, add it to the last goal."""
        self.goals[-1].sub_clauses.append(sub_clause)

    def finish_comp(self, comp_def: components.ComponentDefinition, spec: "Specification"):
        """Check the found goals, and add them to the component."""
        vps = utils.construct_var_param_map(comp_def)
        cinsts = utils.construct_comp_instances_map(comp_def)
        vpps = utils.construct_verb_prepos_combis(spec)

        expr_checker = ExprChecker(vps, self.diag_store)

        # Verify all goals in the component.
        good_goals = []  # Goals without fatal error.
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for goal in self.goals:
            is_good = True
            assert goal.goal_kind is not None
            self.check_form("goal", goal.goal_kind, goal.doesaux, goal.sub_clauses)

            # Check existence of active and passive components.
            goal.active_comp = self.resolve_component(goal.active, cinsts)
            goal.passive_comp = self.resolve_component(goal.passive, cinsts)
            if not goal.active_comp or not goal.passive_comp:
                is_good = False

            # Store goal on its label for duplicate label detection.
            elements_by_label[goal.label_tok.tok_text].append(goal)

            if not self.verify_flows(goal.flows, vps):
                is_good = False

            self.verify_verb_prepos(goal.verb, goal.prepos, vpps)

            # Verify subclauses.
            for sub in goal.sub_clauses:
                if not expr_checker.check_expr(sub.expr):
                    is_good = False

            if is_good:
                good_goals.append(goal)

        comp_def.goals = good_goals
