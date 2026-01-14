"""Code for collecting and type checking designs."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from raesl.compile.ast import components
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.expr_checker import ExprChecker

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CompDefDesignBuilder:
    """Class for collecting and type checking designs in a component definition."""

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.comp_child_builders = comp_child_builders
        self.designs: List[components.Design] = []
        self.design_kind: Optional[str] = None

    def new_design_header(self, kind: "Token"):
        """New design section started, store the kind stated in the header."""
        if kind.tok_type == "DESIGN_REQUIREMENT_KW":
            self.design_kind = components.REQUIREMENT
        else:
            assert kind.tok_type == "DESIGN_CONSTRAINT_KW"
            self.design_kind = components.CONSTRAINT

    def design_line(self, design: components.Design):
        """New design rule found, store it."""
        assert self.design_kind is not None
        design.design_kind = self.design_kind
        self.designs.append(design)

    def add_design_subclause(self, sub: components.SubClause):
        """Subclause of the last design has been found, append it to the last design."""
        self.designs[-1].sub_clauses.append(sub)

    def finish_comp(self, comp_def: components.ComponentDefinition, _spec: "Specification"):
        """Check the found designs in the context of 'comp_def', and add them after
        verification.

        Arguments:
            comp_def: Surrounding component definition supplying variables and
                parameters. Checked designs should be added to it after checking.
            _spec: Specification being constructed, source for types and verbs.
        """
        vps = utils.construct_var_param_map(comp_def)
        expr_checker = ExprChecker(vps, self.diag_store)

        good_designs = []  # Designs that can be added.
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for design in self.designs:
            is_good = True

            # Order by label for double use checking.
            elements_by_label[design.label_tok.tok_text].append(design)

            # Verify comparisons.
            if not expr_checker.check_expr(design.expr):
                is_good = False

            for sub in design.sub_clauses:
                if not expr_checker.check_expr(sub.expr):
                    is_good = False

            # Consider design good if no big issues found.
            if is_good:
                good_designs.append(design)

        comp_def.designs = good_designs
