"""Dutch localization implementation."""

# Ignore line length errors for translation strings.
# ruff: noqa: E501

from collections.abc import Iterable

from raesl.l10n.abc import LocaleAbc


class NlNl(LocaleAbc):
    """Dutch rules."""

    def locale_id(self) -> str:
        return "nl-NL"

    # GENERIC SECTION INTRODUCTION

    def section_intro(self, subject: str) -> str:
        return f"Deze sectie beschrijft {subject}."

    # FIGURE CAPTIONS

    def dsm_kind_caption(self, kind: str, level: int) -> str:
        return f"De {kind} afhankelijkheidsmatrix van decompositieniveau {level}."

    def dsm_ref(self, reference: str) -> str:
        return f"De bijbehorende afhankelijkheidsmatrix (DSM) is weergegeven in {reference}."

    def dsm_level_intro(self) -> str:
        return "De DSM laat de afhankelijkheden tussen de elementen die relevant zijn voor dit decompositieniveau."

    def mdm_description(self) -> str:
        return "De MDM illustreert de afhankelijkheden tussen de componenten, tussen de functies en combinaties daarvan behorend bij dit decompositieniveau."

    # SCOPE / PATH

    def world(self) -> str:
        return "wereld"

    def scope(self) -> str:
        return "scope"

    def path(self) -> str:
        return "pad"

    # COMPONENT HIERARCHY AND PROPERTIES

    def component(self, plural: bool) -> str:
        return "componenten" if plural else "component"

    def announce_decomposition_level(self, level: int, n_components: int) -> str:
        return super().announce_decomposition_level(level, n_components)

    def announce_first_decomposition_level(self, n_components: int) -> str:
        ond = self.amount("component", n_components)
        ww = "welke een rol speelt" if n_components == 1 else "die een rol spelen"

        return f"Dit hoofdstuk beschrijft het systeem op het eerste {self.decomposition_level()}. Dit niveau beschrijft {ond} {ww} in de wereld waarin het systeem dient te opereren en die (functionele) interacties daartussen."

    def announce_subsequent_decomposition_level(self, level: int, n_components: int) -> str:
        return f"Dit hoofdstuk beschrijft het systeem op {self.decomposition_level()} {self.numeral(level)} en introduceert {self.amount('component', n_components)}."

    def decomposition_level(self) -> str:
        return "decompositieniveau"

    def subcomponent(self, plural: bool) -> str:
        return "sub-componenten" if plural else "sub-component"

    def local_component_tree(self) -> str:
        return "lokale componentenboom"

    def dependency_structure(self) -> str:
        return "afhankelijkheidsstructuur"

    def is_a_subcomponent_of(self, parent: str) -> str:
        return f"Dit component is een {self.subcomponent(False)} van {parent}."

    def subcomponents_defined_within(self, parent: str, count: int) -> str:
        componenten = self.amount("component", count)
        return f"De volgende {componenten} zijn gedefinieerd binnen {parent}:"

    def following_properties_for(self, subject: str, plural: bool) -> str:
        return f"De volgende {self.property(plural)} {'zijn' if plural else 'is'} gedefinieerd voor {subject}:"

    # FUNCTIONS AND REQUIREMENTS

    def constraint(self, plural: bool) -> str:
        return "randvoorwaarden" if plural else "randvoorwaarde"

    def requirement(self, plural: bool) -> str:
        return "eis" if plural else "eisen"

    def with_subclause(self, plural: bool) -> str:
        return "met aanvullende eisen" if plural else "met aanvullende eis"

    def design_rule_line(
        self,
        subject: str,
        aux: str,
        comparison: str,
        bound: str | None = None,
        unit: str | None = None,
    ) -> str:
        split_aux: tuple[str, str] = self.design_rule_aux(aux)
        comparison = self.design_rule_comparison(comparison)
        return f"{subject} {split_aux[0]} {comparison} {bound} {unit} {split_aux[1]}"

    def design_rule_aux(self, aux: str) -> tuple[str, str]:
        """Translate a design rule auxiliary word pair to a Dutch equivalent."""
        match aux:
            case "must be":
                return ("dient", "te zijn")
            case "shall be":
                return ("zal", "zijn")
            case "should be":
                return ("behoort", "te zijn")
            case "could be":
                return ("zou", "kunnen zijn")
            case "won't be":
                return ("zal nimmer", "zijn")
            case "will be":
                return ("zal", "zijn")
            case _:
                raise NotImplementedError(
                    f"{__class__.__name__} translation for '{aux}' not found."
                )

    def design_rule_comparison(self, comparison: str) -> str:
        """Translate a comparison operator for use in Dutch."""
        match comparison:
            case "smaller than":
                return "kleiner dan"
            case "at most":
                return "hoogstens"
            case "equal to":
                return "gelijk aan"
            case "at least":
                return "ten minste"
            case "greater than":
                return "groter dan"
            case "approximately":
                return "ongeveer"
            case _:
                raise NotImplementedError(
                    f"{__class__.__name__} translation for {comparison} not found."
                )

    def subordinate_function(self, plural: bool) -> str:
        return (
            "onderliggende functiespecificaties" if plural else "onderliggende functiespecificatie"
        )

    # GOAL FUNCTIONS

    def goal_constraint(self, plural: bool) -> str:
        return f"doelfunctie-{self.constraint(plural)}"

    def goal_requirement(self, plural: bool) -> str:
        return f"doelfunctie-{self.requirement(plural)}"

    def goal_clause(
        self, active: str, aux: str, verb: str, flows: str, prep: str, passive: str
    ) -> str:
        match aux:
            case "must":
                pred = self.make_predicate(verb)
                return f"{active} dient {flows} {prep} {passive} {pred}"
            case "should":
                pred = self.make_predicate(verb)
                return f"{active} behoort {flows} {prep} {passive} {pred}"
            case "could":
                return f"{active} zou {flows} {prep} {passive} kunnen {verb}"
            case "won't":
                return f"{active} zal nimmer {flows} {prep} {passive} {verb}"
            case "shall":
                return f"{active} zal {flows} {prep} {passive} {verb}"
            case "does":
                return f"{active} vervult het {verb} van {flows} {prep} {passive}"
            case _:
                pred = self.make_predicate(verb)
                return f"{active} {aux} {pred} {flows} {prep} {passive}"

    def goal_constraint_migrated_from(self, reference: str) -> str:
        return (
            f"Deze doelfunctie-{self.constraint(False)} is automatisch gemigreerd van {reference}."
        )

    def goal_requirement_migrated_from(self, reference: str) -> str:
        return (
            f"Deze doelfunctie-{self.requirement(False)} is automatisch gemigreerd van {reference}."
        )

    # TRANSFORMATION FUNCTIONS

    def transformation_constraint(self, plural: bool) -> str:
        return f"transformatiefunctie-{self.constraint(plural)}"

    def transformation_requirement(self, plural: bool) -> str:
        return f"transformatiefunctie-{self.requirement(plural)}"

    def transformation_clause(
        self, comp: str, aux: str, verb: str, in_flows: str, prep: str, out_flows: str
    ) -> str:
        match aux:
            case "must":
                pred = self.make_predicate(verb)
                return f"{comp} dient {in_flows} {prep} {out_flows} {pred}"
            case "should":
                pred = self.make_predicate(verb)
                return f"{comp} behoort {in_flows} {prep} {out_flows} {pred}"
            case "could":
                return f"{comp} zou {in_flows} {prep} {out_flows} kunnen {verb}"
            case "won't":
                return f"{comp} zal nimmer {in_flows} {prep} {out_flows} {verb}"
            case "shall":
                return f"{comp} zal {in_flows} {prep} {out_flows} {verb}"
            case "is":
                return f"{comp} vervult het {verb} van {in_flows} {prep} {out_flows}"
            case _:
                return f"{comp} {aux} {verb} {in_flows} {prep} {out_flows}"

    # BEHAVIOR FUNCTIONS

    def behavior_constraint(self, plural: bool) -> str:
        return f"gedrags{self.constraint(plural)}"

    def behavior_requirement(self, plural: bool) -> str:
        return f"gedrags{self.requirement(plural)}"

    def behavior_case(self, plural: bool) -> str:
        return "situaties" if plural else "situatie"

    def behavior_default(self) -> str:
        return "standaard"

    def behavior_when(self) -> str:
        return "wanneer"

    def behavior_when_default(self) -> str:
        return "wanneer geen andere situatie van toepassing is"

    def behavior_then(self) -> str:
        return "dan"

    # DESIGN CONSTRAINTS/REQUIREMENTS

    def design_constraint(self, plural: bool) -> str:
        return f"kwantitatieve ontwerp{self.constraint(plural)}"

    def design_requirement(self, plural: bool) -> str:
        return f"kwantitatieve ontwerp{self.requirement(plural)}"

    def global_design_constraint(self, plural: bool) -> str:
        return f"globale {self.design_constraint(plural)}"

    def global_design_requirement(self, plural: bool) -> str:
        return f"globale {self.design_requirement(plural)}"

    def unlinked_needs_designs_heading(self) -> str:
        return f"globale kwalitatieve en kwantitatieve ontwerp{self.requirement(True)}"

    def unlinked_needs_designs_intro(self) -> str:
        return f"Deze sectie bevat alle kwalitatieve and kwantitatieve ontwerp{self.requirement(True)} die niet aan een component zijn gerelateerd."

    # NEEDS

    def need(self, plural: bool) -> str:
        return f"kwalitatieve ontwerp{self.requirement(plural)}"

    def global_need(self, plural: bool) -> str:
        return f"globale {self.need(plural)}"

    # RELATIONS

    def relation(self, plural: bool) -> str:
        return "vergelijkingen en modellen" if plural else "model"

    def required_variable(self, plural: bool) -> str:
        return f"invoer{self.variable(plural)}"

    def returned_variable(self, plural: bool) -> str:
        return f"resulterende {self.variable(plural)}"

    def related_variable(self, plural: bool) -> str:
        return f"gerelateerde {self.variable(plural)}"

    # TYPES

    def type(self, plural: bool) -> str:
        return "types" if plural else "type"

    def definition(self, plural: bool) -> str:
        return "definities" if plural else "definitie"

    def interval(self, plural: bool) -> str:
        return "intervallen" if plural else "interval"

    def enumeration_of(self) -> str:
        return "opsomming van"

    def unit(self, plural: bool) -> str:
        return "eenheden" if plural else "eenheid"

    def domain(self, plural: bool) -> str:
        return "domeinen" if plural else "domein"

    def lower_bound_equals(self, value: str) -> str:
        return f"de ondergrens is gelijk aan {value}"

    def upper_bound_equals(self, value: str) -> str:
        return f"de bovengrens is gelijk aan {value}"

    def is_a_bundle_of(self) -> str:
        return "is een bundel van"

    def are_bundles_of(self) -> str:
        return "zijn bundels van"

    def bundle_clarification(self, bundles: Iterable[str]) -> str:
        bundles = list(bundles)
        meervoud = len(bundles) != 1
        ww = "zijn" if meervoud else "is"
        znw = "bundels" if meervoud else "een bundel"

        return f"Hier {ww} {self.enumeration(bundles)} {znw} waarvan de volgende {self.variable(True)} worden gebruikt:"

    # VARIABLES

    def variable(self, plural: bool) -> str:
        return "variabelen" if plural else "variabele"

    def property(self, plural: bool) -> str:
        return "eigenschappen" if plural else "eigenschap"

    def full_variable_name(self, name: str, path: str) -> str:
        return f"Het volledige {self.path()} naar {self.variable(False)} {name} is {path}."

    def list_of_variables(self) -> str:
        return "lijst van variabelen"

    def variable_reference_list(self) -> str:
        return "variabelen referentielijst"

    # COMMENTS

    def comments(self) -> str:
        return "commentaar"

    def clarification(self) -> str:
        return "toelichting"

    # LINGUISTIC HELPERS

    def amount(self, item: str, count: int, pluralized: str | None = None) -> str:
        num = self.numeral(count)
        if count != 1:
            if pluralized is None:
                if item[-1] in {"a", "e", "i", "o", "u"}:
                    item = f"{item}s"
                else:
                    item = f"{item}en"
        return f"{num} {item}"

    def numeral(self, num: int) -> str:
        try:
            return [
                "geen",
                "één",
                "twee",
                "drie",
                "vier",
                "vijf",
                "zes",
                "zeven",
                "acht",
                "negen",
                "tien",
            ][num]
        except IndexError:
            return str(num)

    def enum_and(self) -> str:
        return "en"

    def enumeration(self, items: Iterable[str]) -> str:
        items = list(items)
        match len(items):
            case 0:
                return ""
            case 1:
                return items.pop()
            case _:
                return "{} en {}".format(", ".join(x for x in items[:-1]), items[-1])

    def options(self, items: Iterable[str]) -> str:
        return " of ".join(items)

    def possessive_of(self) -> str:
        return "van"

    def related_to(self) -> str:
        return "gerelateerd aan"

    def where_respectively(self) -> str:
        return "respectievelijk"

    def make_predicate(self, verb: str) -> str:
        """Check if a "splitsend werkwoord" has been used and return predicate.

        Argument:
        verb: the used verb

        Returns
        Predicate of the sentence.
        """

        preps = [
            "aan",
            "in",
            "op",
            "om",
            "na",
            "tegen",
            "tussen",
            "uit",
            "bij",
            "mee",
            "af",
            "mee",
            "terug",
        ]

        for prep in preps:
            if verb.startswith(prep):
                tail = verb[len(prep) :].strip()
                return f"{prep} te {tail}"

        return f"te {verb}"
