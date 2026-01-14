"""Code for collecting and adding behavior sections to component definitions."""
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from raesl.compile import diagnostics
from raesl.compile.ast import components
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.expr_checker import ExprChecker

if TYPE_CHECKING:
    from raesl.compile.ast.components import ComponentDefinition
    from raesl.compile.ast.exprs import Comparison, Disjunction, RelationComparison
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class ParsedBehavior:
    """Temporary storage of a behavior. This allows catching multiple default cases
    (these cannot be expressed in the AST). Also, it allows checking for receiving a
    sane order of calls from the parser.
    """

    def __init__(self, name: "Token", kind: str, cases: List["ParsedCase"]):
        self.name = name
        self.kind = kind
        self.cases = cases


# A case in behavior. The 'when_tok' and 'then_tok' can be set once for each case.
WhensType = List[Tuple["Token", Union["Disjunction", "RelationComparison"]]]
ThensType = List[Tuple["Token", "Comparison"]]


class ParsedCase:
    """Temporary storage for storing a case in a behavior while collecting the cases.

    Arguments:
        name: Name of the case.
        when_tok: Position of the 'when' line.
        then_tok: Position of the 'then' line.
        whens: Collected conditions. Will be empty for the default behavior. None
            means the variable should not be accessed at all.
        thens: Collected results.
    """

    def __init__(
        self,
        name: "Token",
        when_tok: Optional["Token"],
        then_tok: Optional["Token"],
        whens: WhensType,
        thens: ThensType,
    ):
        self.name = name
        self.when_tok = when_tok
        self.then_tok = then_tok
        self.whens: Optional[WhensType] = whens
        self.thens = thens


class CompDefBehaviorBuilder:
    """Class for constructing and checking behavior functions.

    Arguments:
        comp_child_builders: Storage of child builders for a component definition.

    Attributes:
        behavior_kind: Last seen kind of behavior ('requirement' or 'constraint').
        expect_conds: Whether the builder should allow conditions to be received from
            the parser.
        expect_results: Whether the builder should allow results to be received from
            the parser.
        pbehaviors: Collected behaviors.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.comp_child_builders = comp_child_builders

        self.behavior_kind: Optional[str] = None
        self.expect_conds = False
        self.expect_results = False
        self.pbehaviors: List[ParsedBehavior] = []  # Using List[ParsedCase] for its 'case's.

    def new_behavior_header(self, kind_tok: "Token"):
        """A new 'behavior' section header was found."""
        if kind_tok.tok_type == "BEHAVIOR_REQUIREMENT_KW":
            self.behavior_kind = components.REQUIREMENT
        else:
            assert kind_tok.tok_type == "BEHAVIOR_CONSTRAINT_KW"
            self.behavior_kind = components.CONSTRAINT

        self.expect_conds = False
        self.expect_results = False

    def new_behavior_function(self, label_tok: "Token"):
        """A new behavior functionality was found.

        Arguments:
            label_tok: Name of the new behavior.
        """
        assert self.behavior_kind is not None
        parsed_beh = ParsedBehavior(label_tok, self.behavior_kind, [])
        self.pbehaviors.append(parsed_beh)

        self.expect_conds = False
        self.expect_results = False

    def behavior_case(self, case_label_tok: "Token"):
        """A new case of the last started behavior functionality was found.

        Arguments:
            case_label_tok: Name of the case.
        """
        parsed_case = ParsedCase(case_label_tok, None, None, [], [])
        self.pbehaviors[-1].cases.append(parsed_case)

        self.expect_conds = False
        self.expect_results = False

    def behavior_normal_when(self, when_tok: "Token"):
        """The start of a normal 'when' condition block was found.

        Arguments:
            when_tok: Position of the start of the new block.
        """
        assert self.pbehaviors[-1].cases[-1].when_tok is None
        self.pbehaviors[-1].cases[-1].when_tok = when_tok

        # No need to setup case[-1].whens, as behavior_case() already did that.
        self.expect_conds = True
        self.expect_results = False

    def behavior_default_when(self, when_tok: "Token"):
        """The start of a default condition block was found.

        Arguments:
            when_tok: Position of the start of the new block.
        """
        assert self.pbehaviors[-1].cases[-1].when_tok is None
        self.pbehaviors[-1].cases[-1].when_tok = when_tok

        # Ensure code will crash if you add 'whens'.
        self.pbehaviors[-1].cases[-1].whens = None

        # We don't expect more 'when', and we must see a 'then' first.
        self.expect_conds = False
        self.expect_results = False

    def behavior_when_condition(
        self, name_tok: "Token", condition: Union["Disjunction", "RelationComparison"]
    ):
        """A new condition was found, add it to the last 'when' block.

        Arguments:
            name_tok: Name of the condition.
            condition: Condition to add.
        """
        assert self.expect_conds
        assert self.pbehaviors[-1].cases[-1].whens is not None
        self.pbehaviors[-1].cases[-1].whens.append((name_tok, condition))

    def behavior_normal_then(self, then_tok: "Token"):
        """The start of a 'then' result block was found.

        Arguments:
            then_tok: Position of the start of the new block.
        """
        assert self.pbehaviors[-1].cases[-1].then_tok is None
        self.pbehaviors[-1].cases[-1].then_tok = then_tok

        # No need to setup case[-1].thens, as behavior_case() already did that.
        self.expect_conds = False
        self.expect_results = True

    def behavior_then_result(self, name_tok: "Token", result: "Comparison"):
        """A new result was found, add it to the last 'then' block.

        Arguments:
            name_tok: Name of the result.
            result: Result to add.
        """
        assert self.expect_results
        self.pbehaviors[-1].cases[-1].thens.append((name_tok, result))

    def finish_comp(self, comp_def: "ComponentDefinition", _spec: "Specification"):
        """Verify correctness of the collected behavior and store good behavior in
        :obj:`comp_def`.

        Arguments:
            comp_def: Surrounding component definition supplying variables and
                parameters. Checked designs should be added to it after checking.
            _spec: Specification being constructed, source for types and verbs.
        """
        vps = utils.construct_var_param_map(comp_def)
        expr_checker = ExprChecker(vps, self.diag_store)

        beh_funcs = []
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for pbeh in self.pbehaviors:
            # Store labels of functions for duplicate checking.
            elements_by_label[pbeh.name.tok_text].append(pbeh)

            beh_func = components.BehaviorFunction(pbeh.kind, pbeh.name)
            default_cases: List["Token"] = []  # Positions of default cases in this function.
            cases_ordered_by_label: Dict[str, List["Token"]] = defaultdict(list)
            for pcase in pbeh.cases:
                cases_ordered_by_label[pcase.name.tok_text].append(pcase.name)

                # Process conditions.
                if pcase.whens is None:
                    # Default case.
                    assert pcase.when_tok is not None
                    default_cases.append(pcase.when_tok)
                    conditions = None
                else:
                    # Normal case.
                    conditions = self._convert_conditions(pcase.whens, expr_checker)

                # Process results.
                results = self._convert_results(pcase.thens, expr_checker)

                # Add case to the function.
                if conditions is None:
                    # Bluntly assume this happens at most once. If not, 'default_cases'
                    # will detect it and give an error.
                    beh_func.default_results = results
                else:
                    beh_case = components.BehaviorCase(pcase.name, conditions, results)
                    beh_func.cases.append(beh_case)

            # Verify uniqueness of cases.
            for dup_cases in cases_ordered_by_label.values():
                if len(dup_cases) > 1:
                    # Duplicate case names.
                    self.diag_store.add(
                        diagnostics.E200(
                            dup_cases[0].tok_text,
                            "behavior case",
                            location=pbeh.name.get_location(),
                            dupes=[dupe.get_location() for dupe in dup_cases],
                        )
                    )

            # Check number of default cases.
            if len(default_cases) > 1:
                # Duplicate fallback cases.
                self.diag_store.add(
                    diagnostics.E200(
                        pbeh.name.tok_text,
                        "fallback case",
                        location=pbeh.name.get_location(),
                        dupes=[dupe.get_location() for dupe in default_cases],
                    )
                )

            beh_funcs.append(beh_func)

        comp_def.behaviors = beh_funcs

    def _convert_conditions(
        self, whens: WhensType, expr_checker: ExprChecker
    ) -> List[components.BehaviorCondition]:
        """Check the conditions of a case, and convert them to :obj:`BehaviorCondition`
        instances.
        """
        conditions = []
        when_ordered_by_label: Dict[str, List["Token"]] = defaultdict(list)
        for when in whens:
            name_tok, cond = when
            when_ordered_by_label[name_tok.tok_text].append(name_tok)

            if expr_checker.check_expr(cond):
                conditions.append(components.BehaviorCondition(name_tok, cond))

        for dupes in when_ordered_by_label.values():
            if len(dupes) > 1:
                first = dupes[0]
                locs = [dupe.get_location() for dupe in dupes]
                self.diag_store.add(
                    diagnostics.E200(
                        first.tok_text,
                        "behavior condition",
                        location=first.get_location(),
                        dupes=locs,
                    )
                )

        return conditions

    def _convert_results(
        self, thens: ThensType, expr_checker: ExprChecker
    ) -> List[components.BehaviorResult]:
        """Check the results of a case, and convert them to :obj:`BehaviorResult`
        instances.
        """
        results = []
        then_ordered_by_label: Dict[str, List["Token"]] = defaultdict(list)
        for then in thens:
            name_tok, result = then
            then_ordered_by_label[name_tok.tok_text].append(name_tok)

            if expr_checker.check_expr(result):
                results.append(components.BehaviorResult(name_tok, result))

        for dupes in then_ordered_by_label.values():
            if len(dupes) > 1:
                first = dupes[0]
                locs = [dupe.get_location() for dupe in dupes]
                self.diag_store.add(
                    diagnostics.E200(
                        first.tok_text,
                        "behavior result",
                        first.get_location(),
                        dupes=locs,
                    )
                )

        return results
