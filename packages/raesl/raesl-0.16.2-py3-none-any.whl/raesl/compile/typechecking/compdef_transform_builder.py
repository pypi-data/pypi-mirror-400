"""Code for collecting and type checking of transformations."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from raesl.compile.ast import components
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.expr_checker import ExprChecker
from raesl.compile.typechecking.goal_transform_base import GoalTransformBaseBuilder

if TYPE_CHECKING:
    from raesl.compile.ast.components import ComponentDefinition, SubClause
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CompDefTransformBuilder(GoalTransformBaseBuilder):
    """Collect transformations of a component from the parser, check them, and add them
    to the component definition.

    Arguments:
        comp_child_builders: Storage of child builders for a component definition.

    Attributes:
        transforms: Collected transformations.
        transform_kind: Last found kind of transformation kind, either 'requirement' or
            'constraint'.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        super(CompDefTransformBuilder, self).__init__(comp_child_builders.diag_store)
        self.transforms: List[components.Transformation] = []
        self.comp_child_builders = comp_child_builders
        self.transform_kind: Optional[str] = None

    def new_transform_header(self, transform_kind: "Token"):
        """New transform section line found.

        Arguments:
            transform_kind: Kind of transformations that will follow.
        """
        if transform_kind.tok_type == "TRANSFORM_REQUIREMENT_KW":
            self.transform_kind = components.REQUIREMENT
        else:
            assert transform_kind.tok_type == "TRANSFORM_CONSTRAINT_KW"
            self.transform_kind = components.CONSTRAINT

    def add_transform(self, transform: components.Transformation):
        """A new transformation has been found, add it to the collection.

        Arguments:
            transform: Transformation to add.
        """
        assert self.transform_kind is not None
        transform.transform_kind = self.transform_kind
        self.transforms.append(transform)

    def add_transform_subclause(self, sub_clause: "SubClause"):
        """Add a found subclause that belongs to the last transformation."""
        self.transforms[-1].sub_clauses.append(sub_clause)

    def finish_comp(self, comp_def: "ComponentDefinition", spec: "Specification"):
        """Check the found transformations, and add them to the component.

        Arguments:
            comp_def: Component definition to extend with the found relation instances.
                Also a source of available variables, parameters, and variable groups.
            spec: Specification being constructed. Source for types and relation
                definitions processed previously.
        """
        vps = utils.construct_var_param_map(comp_def)
        vpps = utils.construct_verb_prepos_combis(spec)

        expr_checker = ExprChecker(vps, self.diag_store)

        # Verify all transformations in the component.
        good_transforms = []  # Transformations to add to the component.
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for trans in self.transforms:
            is_good = True
            assert trans.transform_kind is not None
            self.check_form(
                "transformation",
                trans.transform_kind,
                trans.doesaux_tok,
                trans.sub_clauses,
            )

            # Store transformation on its label for duplicate label detection.
            elements_by_label[trans.label_tok.tok_text].append(trans)

            if not self.verify_flows(trans.in_flows, vps):
                is_good = False
            if not self.verify_flows(trans.out_flows, vps):
                is_good = False

            self.verify_verb_prepos(trans.verb_tok, trans.prepos_tok, vpps)

            # Verify subclauses.
            for sub in trans.sub_clauses:
                if not expr_checker.check_expr(sub.expr):
                    is_good = False

            if is_good:
                good_transforms.append(trans)

        comp_def.transforms = good_transforms
