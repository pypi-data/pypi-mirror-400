from abc import ABC, abstractmethod
from collections.abc import Iterable


class LocaleAbc(ABC):
    """Locale to implement."""

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__

    @abstractmethod
    def locale_id(self) -> str:
        """Return the locale ID."""
        ...

    # GENERIC SECTION INTRODUCTION

    @abstractmethod
    def section_intro(self, subject: str) -> str:
        """Translation: 'This section describes {subject}.'"""
        ...

    # FIGURE CAPTIONS

    @abstractmethod
    def dsm_kind_caption(self, kind: str, level: str) -> str:
        """Translation of '{kind} dependency matrix of decomposition level {level}.'"""
        ...

    @abstractmethod
    def dsm_ref(self, reference: str) -> str:
        """Translation of 'The associated design-structure-matrix (DSM) is shown in {reference}.'"""
        ...

    @abstractmethod
    def dsm_level_intro(self) -> str:
        """Translation for 'The DSM shows the dependencies between the elements that are relevant to
        this decomposition level.'.
        """
        ...

    @abstractmethod
    def mdm_description(self) -> str:
        """Translation for 'The MDM shows the dependencies between the components,
        the function specifications and the combinations thereof that are relevant to
        this decomposition level.'.
        """
        ...

    # SCOPE / PATH

    @abstractmethod
    def world(self) -> str:
        """Terminology for the specification 'world' or context boundary."""
        ...

    @abstractmethod
    def scope(self) -> str:
        """Terminology for the 'scope' or context of a (partial) specification."""
        ...

    @abstractmethod
    def path(self) -> str:
        """Terminology for the hierarchical 'path' from the world to something."""
        ...

    # COMPONENT HIERARCHY AND PROPERTIES

    @abstractmethod
    def component(self, plural: bool) -> str:
        """Terminology for a 'component'."""
        ...

    @abstractmethod
    def announce_decomposition_level(self, level: int, n_components: int) -> str:
        """Announce a decomposition level of any depth."""
        if level == 1:
            return self.announce_first_decomposition_level(n_components)
        else:
            return self.announce_subsequent_decomposition_level(level, n_components)

    @abstractmethod
    def announce_first_decomposition_level(self, n_components: int) -> str:
        """Announce the top-most level of the decomposition."""
        ...

    @abstractmethod
    def announce_subsequent_decomposition_level(self, level: int, n_components: int) -> str:
        """Announce any decomposition level of any depth except the first."""
        ...

    @abstractmethod
    def decomposition_level(self) -> str:
        """Terminology for 'decomposition level'."""
        ...

    @abstractmethod
    def subcomponent(self, plural: bool) -> str:
        """Terminology for a single 'sub-component'."""
        ...

    @abstractmethod
    def local_component_tree(self) -> str:
        """Terminology for a 'local component tree'."""
        ...

    @abstractmethod
    def dependency_structure(self) -> str:
        """Terminology for 'dependency structure'."""
        ...

    @abstractmethod
    def is_a_subcomponent_of(self, parent: str) -> str:
        """Translation: 'This component is a sub-component of {parent}.'"""
        ...

    @abstractmethod
    def subcomponents_defined_within(self, parent: str, count: int) -> str:
        """Translation: The following {count} sub-components are defined within {parent}:"""
        ...

    @abstractmethod
    def following_properties_for(self, subject: str, plural: bool) -> str:
        """Translation for 'The following properties are specified for {subject}:"""
        ...

    # FUNCTIONS AND REQUIREMENTS

    @abstractmethod
    def constraint(self, plural: bool) -> str:
        """Terminology for a 'constraint'."""
        ...

    @abstractmethod
    def requirement(self, plural: bool) -> str:
        """Terminology for a 'requirement'."""
        ...

    @abstractmethod
    def with_subclause(self, plural: bool) -> str:
        """Translation for 'with subclause' or 'with subclauses'."""
        ...

    @abstractmethod
    def design_rule_line(
        self,
        subject: str,
        aux: str,
        comparison: str,
        bound: str | None = None,
        unit: str | None = None,
    ) -> str:
        """Format a design rule line, being a design constraint/requirement or subclause."""
        ...

    @abstractmethod
    def subordinate_function(self, plural: bool) -> str:
        """Terminology for 'subordinate function specifications'."""
        ...

    # GOAL FUNCTIONS

    @abstractmethod
    def goal_constraint(self, plural: bool) -> str:
        """Terminology for 'goal constraints'."""
        ...

    @abstractmethod
    def goal_requirement(self, plural: bool) -> str:
        """Terminology for 'goal requirements'."""
        ...

    @abstractmethod
    def goal_clause(
        self, active: str, aux: str, verb: str, flows: str, prep: str, passive: str
    ) -> str:
        """Format a goal main clause."""
        ...

    @abstractmethod
    def goal_requirement_migrated_from(self, reference: str) -> str:
        """Translation for
        'This goal function requirement automatically migrated from {reference}.'.
        """
        ...

    @abstractmethod
    def goal_constraint_migrated_from(self, reference: str) -> str:
        """Translation for
        'This goal function constraint automatically migrated from {reference}.'.
        """
        ...

    # TRANSFORMATION FUNCTIONS

    @abstractmethod
    def transformation_constraint(self, plural: bool) -> str:
        """Terminology for 'transformation constraints'."""
        ...

    @abstractmethod
    def transformation_requirement(self, plural: bool) -> str:
        """Terminology for 'transformation requirements'."""
        ...

    @abstractmethod
    def transformation_clause(
        self, comp: str, aux: str, verb: str, in_flows: str, prep: str, out_flows: str
    ) -> str:
        """Format a transformation main clause."""
        ...

    # BEHAVIOR FUNCTIONS

    @abstractmethod
    def behavior_constraint(self, plural: bool) -> str:
        """Translation for 'behavior constraints'."""
        ...

    @abstractmethod
    def behavior_requirement(self, plural: bool) -> str:
        """Translation for 'behavior requirements'."""
        ...

    @abstractmethod
    def behavior_case(self, plural: bool) -> str:
        """Terminology for a behavior requirement 'case' or scenario."""
        ...

    @abstractmethod
    def behavior_default(self) -> str:
        """Terminology for a behavior requirement 'default' case or fallback scenario."""
        ...

    @abstractmethod
    def behavior_when(
        self,
    ) -> str:
        """Terminology for a behavior case's 'when'."""
        ...

    @abstractmethod
    def behavior_when_default(
        self,
    ) -> str:
        """Translation for 'when no other case applies'."""
        ...

    @abstractmethod
    def behavior_then(
        self,
    ) -> str:
        """Terminology for a behavior case's 'then'."""
        ...

    # DESIGN CONSTRAINTS/REQUIREMENTS

    @abstractmethod
    def design_constraint(self, plural: bool) -> str:
        """Terminology for 'quantitative design constraints'."""
        ...

    @abstractmethod
    def design_requirement(self, plural: bool) -> str:
        """Terminology for 'quantitative design requirements'."""
        ...

    @abstractmethod
    def global_design_constraint(self, plural: bool) -> str:
        """Terminology for 'global quantitative design constraints'."""
        ...

    @abstractmethod
    def global_design_requirement(self, plural: bool) -> str:
        """Terminology for 'global quantitative design requirements'."""
        ...

    @abstractmethod
    def unlinked_needs_designs_heading(self) -> str:
        """Translation for 'unlinked qualitative and quantitative specifications'."""
        ...

    @abstractmethod
    def unlinked_needs_designs_intro(self) -> str:
        """Translation for 'This section lists all qualitative and quantitative design
        specifications that cannot be linked to a component'.
        """
        ...

    # NEEDS

    @abstractmethod
    def need(self, plural: bool) -> str:
        """Terminology for 'needs' or 'qualitative design requirements'."""
        ...

    @abstractmethod
    def global_need(self, plural: bool) -> str:
        """Terminology for 'global qualitative design requirements' or 'global needs'."""
        ...

    # RELATIONS

    @abstractmethod
    def relation(self, plural: bool) -> str:
        """Terminology for 'relations and models'."""
        ...

    @abstractmethod
    def required_variable(self, plural: bool) -> str:
        """Terminology for 'required variables' by a relation or model."""
        ...

    @abstractmethod
    def returned_variable(self, plural: bool) -> str:
        """Terminology for 'returned variables' by a relation or model."""
        ...

    @abstractmethod
    def related_variable(self, plural: bool) -> str:
        """Terminology for 'related variables' by a relation or model."""
        ...

    # TYPES

    @abstractmethod
    def type(self, plural: bool) -> str:
        """Terminology for 'type' as in variable type or its plural."""
        ...

    @abstractmethod
    def definition(self, plural: bool) -> str:
        """Terminology for 'definition' or its plural."""
        ...

    @abstractmethod
    def interval(self, plural: bool) -> str:
        """Translations for 'interval(s)'."""
        ...

    @abstractmethod
    def enumeration_of(self) -> str:
        """Translation for 'enumeration of'."""

    @abstractmethod
    def unit(self, plural: bool) -> str:
        """Translation for a variable or type's 'unit' or its plural."""
        ...

    @abstractmethod
    def domain(self, plural: bool) -> str:
        """Translation for 'domain' as in a variable's domain or its plural."""
        ...

    @abstractmethod
    def lower_bound_equals(self, value: str) -> str:
        """Translation for 'lower bound equals {}'."""
        ...

    @abstractmethod
    def upper_bound_equals(self, value: str) -> str:
        """Translation for 'upper bound equals {}'."""
        ...

    @abstractmethod
    def is_a_bundle_of(self) -> str:
        """Translation for 'is a bundle of'."""
        ...

    @abstractmethod
    def are_bundles_of(self) -> str:
        """Translation for 'are bundles of'"""
        ...

    @abstractmethod
    def bundle_clarification(self, bundles: list[str]) -> str:
        """Translation for 'Here, {} is/are bundles of which the following variables are used'."""
        ...

    # VARIABLES

    @abstractmethod
    def variable(self, plural: bool) -> str:
        """Terminology for 'variable' or its plural 'variables'."""
        ...

    @abstractmethod
    def property(self, plural: bool) -> str:
        """Terminology for 'property' of a component or its plural 'properties'."""
        ...

    @abstractmethod
    def full_variable_name(self, name: str, path: str) -> str:
        """Translation for 'The full name of variable {name} is {path}.'."""
        ...

    @abstractmethod
    def list_of_variables(self) -> str:
        """Translation: list of variables"""
        ...

    @abstractmethod
    def variable_reference_list(self) -> str:
        """Terminology for 'variable reference list'."""
        ...

    # COMMENTS

    @abstractmethod
    def comments(self) -> str:
        """Terminology for 'comments'."""
        ...

    @abstractmethod
    def clarification(self) -> str:
        """Terminology for 'clarification' of something. Used in headers for comments/tags."""
        ...

    # LINGUISTIC HELPERS

    @abstractmethod
    def amount(self, item: str, count: int, pluralized: str | None = None) -> str:
        """Return a pluralized number of items."""
        ...

    @abstractmethod
    def numeral(self, num: int) -> str:
        """Return a numeral description. Words for <=10, numbers thereafter."""
        ...

    @abstractmethod
    def enum_and(self) -> str:
        """The 'and' used for enumerations."""
        ...

    @abstractmethod
    def enumeration(self, items: Iterable[str]) -> str:
        """Enumerate items like you would in a sentence."""
        ...

    @abstractmethod
    def options(self, items: Iterable[str]) -> str:
        """Enumerate options like you would in a sentence."""
        ...

    @abstractmethod
    def possessive_of(self) -> str:
        """Translation of the possessive being 'of' something."""
        ...

    @abstractmethod
    def related_to(self) -> str:
        """Translation for 'related to'."""
        ...

    @abstractmethod
    def where_respectively(self) -> str:
        """Translation for 'where, respectively'."""
        ...
