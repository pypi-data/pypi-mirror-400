"""American English localization implementation."""

# Ignore line length errors for translation strings.
# ruff: noqa: E501

from collections.abc import Iterable

from raesl.l10n.abc import LocaleAbc


class EnUs(LocaleAbc):
    """American English rules."""

    def locale_id(self) -> str:
        return "en-US"

    # GENERIC SECTION INTRODUCTION

    def section_intro(self, subject: str) -> str:
        """Translation: 'This section describes {subject}.'"""
        return f"This section describes {subject}."

    # FIGURE CAPTIONS

    def dsm_kind_caption(self, kind: str, level: int) -> str:
        return f"The {kind} dependency matrix of decomposition level {level}."

    def dsm_ref(self, reference: str) -> str:
        return f"The associated dependency structure matrix (DSM) is shown in {reference}."

    def dsm_level_intro(self) -> str:
        return "The DSM shows the dependencies between the elements that are relevant to this decomposition level."

    def mdm_description(self) -> str:
        return "The multi-domain-matrix (MDM) shows the dependencies between the components, function specifications and the combinations thereof that are relevant to this decomposition level."

    # SCOPE / PATH

    def world(self) -> str:
        return "world"

    def scope(self) -> str:
        return "scope"

    def path(self) -> str:
        return "path"

    # COMPONENT HIERARCHY AND PROPERTIES

    def component(self, plural: bool) -> str:
        return "components" if plural else "component"

    def announce_decomposition_level(self, level, n_components):
        return super().announce_decomposition_level(level, n_components)

    def announce_first_decomposition_level(self, n_components: int) -> str:
        return f"This chapter describes the system of interest at the first {self.decomposition_level()}. That is, it describes {self.amount('component', n_components)} which play a role within the environment in which the system must operate and the (functional) interactions between those components."

    def announce_subsequent_decomposition_level(self, level: int, n_components: int) -> str:
        return f"This chapter describes the system at {self.decomposition_level()} {self.numeral(level)} and introduces {self.amount('component', n_components)}."

    def decomposition_level(self) -> str:
        return "decomposition level"

    def subcomponent(self, plural: bool) -> str:
        return "sub-components" if plural else "sub-component"

    def local_component_tree(self) -> str:
        return "local component tree"

    def dependency_structure(self) -> str:
        return "dependency structure"

    def is_a_subcomponent_of(self, parent: str) -> str:
        return f"This component is a {self.subcomponent(False)} of {parent}."

    def subcomponents_defined_within(self, parent: str, count: int) -> str:
        plural = count != 1
        subs = self.amount(self.subcomponent(False), count)
        is_are = "are" if plural else "is"
        return f"The following {subs} {is_are} defined within {parent}:"

    def following_properties_for(self, subject: str, plural: bool) -> str:
        return f"The following {self.property(plural)} {'are' if plural else 'is'} specified for {subject}:"

    # FUNCTIONS AND REQUIREMENTS

    def constraint(self, plural: bool) -> str:
        return "constraints" if plural else "constraint"

    def requirement(self, plural: bool) -> str:
        return "requirements" if plural else "requirement"

    def with_subclause(self, plural: bool) -> str:
        return "with subclauses" if plural else "with subclause"

    def design_rule_line(
        self,
        subject: str,
        aux: str,
        comparison: str,
        bound: str | None = None,
        unit: str | None = None,
    ) -> str:
        if comparison == "maximized" or comparison == "minimized":
            return f"{subject} {aux} {comparison}"
        elif unit is None:
            return f"{subject} {aux} {comparison} {bound}"
        else:
            return f"{subject} {aux} {comparison} {bound} {unit}"

    def subordinate_function(self, plural: bool) -> str:
        return (
            "subordinate function specifications"
            if plural
            else "subordinate function specification"
        )

    # GOAL FUNCTIONS

    def goal_constraint(self, plural: bool) -> str:
        return f"goal {self.constraint(plural)}"

    def goal_requirement(self, plural: bool) -> str:
        return f"goal {self.requirement(plural)}"

    def goal_clause(
        self, active: str, aux: str, verb: str, flows: str, prep: str, passive: str
    ) -> str:
        return f"{active} {aux} {verb} {flows} {prep} {passive}"

    def goal_constraint_migrated_from(self, reference: str) -> str:
        return f"This goal function constraint automatically migrated from {reference}."

    def goal_requirement_migrated_from(self, reference: str) -> str:
        return f"This goal function requirement automatically migrated from {reference}."

    # TRANSFORMATION FUNCTIONS

    def transformation_constraint(self, plural: bool) -> str:
        return f"transformation {self.constraint(plural)}"

    def transformation_requirement(self, plural: bool) -> str:
        return f"transformation {self.requirement(plural)}"

    def transformation_clause(
        self, comp: str, aux: str, verb: str, in_flows: str, prep: str, out_flows: str
    ) -> str:
        return f"{comp} {aux} {verb} {in_flows} {prep} {out_flows}"

    # BEHAVIOR FUNCTIONS

    def behavior_constraint(self, plural: bool) -> str:
        return f"behavior {self.constraint(plural)}"

    def behavior_requirement(self, plural: bool) -> str:
        return f"behavior {self.requirement(plural)}"

    def behavior_case(self, plural: bool) -> str:
        return "cases" if plural else "case"

    def behavior_default(self) -> str:
        return "default"

    def behavior_when(self) -> str:
        return "when"

    def behavior_when_default(self) -> str:
        return "when no other case applies"

    def behavior_then(self) -> str:
        return "then"

    # DESIGN CONSTRAINTS/REQUIREMENTS

    def design_constraint(self, plural: bool) -> str:
        return f"quantitative design {self.constraint(plural)}"

    def design_requirement(self, plural: bool) -> str:
        return f"quantitative design {self.requirement(plural)}"

    def global_design_constraint(self, plural: bool) -> str:
        return f"global quantitative design {self.constraint(plural)}"

    def global_design_requirement(self, plural: bool) -> str:
        return f"global quantitative design {self.requirement(plural)}"

    def unlinked_needs_designs_heading(self) -> str:
        return "global qualitative and quantitative specifications"

    def unlinked_needs_designs_intro(self) -> str:
        return f"This section lists all {self.unlinked_needs_designs_heading()} that are not linked to a specific component."

    # NEEDS

    def need(self, plural: bool) -> str:
        return f"qualitative design {self.requirement(plural)}"

    def global_need(self, plural: bool) -> str:
        return f"global {self.need(plural)}"

    # RELATIONS

    def relation(self, plural: bool) -> str:
        return "equations and models" if plural else "model"

    def required_variable(self, plural: bool) -> str:
        return f"required {self.variable(plural)}"

    def returned_variable(self, plural: bool) -> str:
        return f"returned {self.variable(plural)}"

    def related_variable(self, plural: bool) -> str:
        return f"related {self.variable(plural)}"

    # TYPES

    def type(self, plural: bool) -> str:
        return "types" if plural else "type"

    def definition(self, plural: bool) -> str:
        return "definitions" if plural else "definition"

    def interval(self, plural: bool) -> str:
        return "intervals" if plural else "intervals"

    def enumeration_of(self) -> str:
        return "enumeration of"

    def unit(self, plural: bool) -> str:
        return "units" if plural else "unit"

    def domain(self, plural: bool) -> str:
        return "domains" if plural else "domain"

    def lower_bound_equals(self, value: str) -> str:
        return f"the lower bound equals {value}"

    def upper_bound_equals(self, value: str) -> str:
        return f"the upper bound equals {value}"

    def is_a_bundle_of(self) -> str:
        return "is a bundle of"

    def are_bundles_of(self) -> str:
        return "are bundles of"

    def bundle_clarification(self, bundles: Iterable[str]) -> str:
        bundles = list(bundles)
        is_bof = self.is_a_bundle_of() if len(bundles) == 1 else self.are_bundles_of()
        return f"Here, {self.enumeration(bundles)} {is_bof} which the following {self.variable(True)} are used:"

    # VARIABLES

    def variable(self, plural: bool) -> str:
        return "variables" if plural else "variable"

    def property(self, plural: bool) -> str:
        return "properties" if plural else "property"

    def full_variable_name(self, name: str, path: str) -> str:
        return f"The full name of variable {name} is {path}."

    def list_of_variables(self) -> str:
        return f"list of {self.variable(True)}"

    def variable_reference_list(self) -> str:
        return f"{self.variable(False)} reference list"

    # COMMENTS

    def comments(self) -> str:
        return "comments"

    def clarification(self) -> str:
        return "clarification"

    # LINGUISTIC HELPERS

    def amount(self, item: str, count: int, pluralized: str | None = None) -> str:
        """Return a pluralized number of items."""
        num = self.numeral(count)
        if count != 1:
            if pluralized is None:
                if item.endswith("y") and item[-2] in {c for c in "qwfpbjlrstgmnzxcdvkh"}:
                    item = f"{item[:-1]}ies"
                elif (
                    item.endswith("s")
                    or item.endswith("sh")
                    or item.endswith("ch")
                    or item.endswith("x")
                ):
                    item = f"{item}es"
                elif item.endswith("f"):
                    item = f"{item[:-1]}ves"
                elif item.endswith("fe"):
                    item = f"{item[:-2]}ves"

                else:
                    item = f"{item}s"
            else:
                item = pluralized
        return f"{num} {item}"

    def numeral(self, num: int) -> str:
        try:
            return [
                "zero",
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
                "ten",
            ][num]
        except IndexError:
            return str(num)

    def enum_and(self) -> str:
        return "and"

    def enumeration(self, items: Iterable[str], oxford: bool = True) -> str:
        items = list(items)
        match len(items):
            case 0:
                return ""
            case 1:
                return items[0]
            case 2:
                return f"{items[0]} {self.enum_and()} {items[1]}"
            case _:
                return "{}{} {} {}".format(
                    ", ".join(x for x in items[:-1]),
                    "," if oxford else "",
                    self.enum_and(),
                    items[-1],
                )

    def options(self, items: Iterable[str]) -> str:
        return " or ".join(items)

    def possessive_of(self) -> str:
        return "of"

    def related_to(self) -> str:
        return "related to"

    def where_respectively(self) -> str:
        return "where, respectively"
