"""Dutch locale overrides."""

from collections import defaultdict
from typing import Any, Dict, Generator, List

from ragraph.graph import Graph
from ragraph.node import Node

import raesl.doc.lines as lns
from raesl import logger
from raesl.doc.locales import hookimpl, pm

LineGen = Generator[str, None, None]


translations = {
    "system specification decomposition level": "systeemspecificatie decompositieniveau",
    "this chapters describes the system of interest at the first decomposition level. That is, it describes {} components which play a role within the environment in which the system of interest must operate and the (functional) interactions between those components": "dit hoofdstuk beschrijft het systeem op het eerste decompositie niveau. Dit niveau beschrijft {} componenten een die rol spelen in de wereld waarin het systeem dient te opereren en die (functionele) interacties daar tussen",  # noqa
    "this chapters describes the system of interest at decomposition level {} and introduces one additional component": "dit hoofdstuk beschrijft het systeem op decompositieniveau {} en introdceert e\\'e\\'m extra component",  # noqa
    "this chapters describes the system of interest at decomposition level {} and introduces {} additional component": "dit hoofdstuk beschrijft het systeem op decompositieniveau {} en introdceert {} extra component",  # noqa
    "transformation function requirements": "transformatiefunctie-eisen",
    "transformation function constraints": "transformatiefunctie-randvoorwaarden",
    "qualitative design requirements": "kwalitatieve ontwerpeisen",
    "quantitative design requirements": "kwantitatieve ontwerpeisen",
    "quantitative design constraints": "kwantitatieve ontwerprandvoorwaarden",
    "sub-components": "sub-componenten",
    "sub-component": "sub-component",
    "goal function requirements": "doelfunctie-eisen",
    "goal function constraints": "doelfunctie-randvoorwaarden",
    "local component tree": "locale objectboom",
    "relations between variables": "relaties tussen variabelen",
    "dependency structure": "afhankelijkheidsstructuur",
    "this section describes **{}**": "deze sectie beschrijft **{}**",
    "this component is a sub-component of {}": "dit component is een sub-component van {}",
    "clarification": "toelichting",
    "of": "van",
    "world": "de wereld",
    "scope": "scope",
    "path": "pad",
    "the following sub-components are defined within {}:": "de volgende sub-componenten zijn gedefinieerd binnen {}:",  # noqa
    "list of variables": "lijst van variabelen",
    "variable": "variabele",
    "type": "type",
    "definitions": "definities",
    "variable reference list": "referentielijst variabelen",
    "related to": "gerelateerd aan",
    "properties": "eigenschappen",
    "interval(s): ": "interval(len): ",
    "enumeration of ": "enumeratie van ",
    "units": "eenheden",
    "domain": "domein",
    " upper bound equals {}": " bovengrens gelijk aan {}",
    " and upper bound equals {}": " en bovengrens gelijk aan {}",
    "lower bound equals {}": "ondergrens gelijk aan {}",
    "the following properties are specified for {}": "de volgende eigenschappen zijn gedefinieerd voor {}",  # noqa
    "relations and models": "relaties en modellen",
    "variables": "variabelen",
    "{} dependency matrix of decomposition level {}.": "{} raakvlakken matrix van decompositieniveau {}.",  # noqa
    "in Figure \\ref{{{}}} the associated design-structure-matrix (DSM) is shown": "in Figuur \\ref{{{}}} is de bijbehorende dependency-structure-matrix (DSM) te zien",  # noqa
    "the DSM shows the dependencies between the elements that are relevant to this decomposition level": "de DSM geeft de afhankelijkheden tussen de elementen die relevant zijn voor dit decompositieniveau.",  # noqa
    "global qualitative design requirements": "systeembrede kwalitatieve ontwerpeisen",
    "global quantitative design requirements": "systeembrede kwantitatieve ontwerpeisen",
    "global quantitative design constraints": "systeembrede kwantitatieve ontwerprandvoorwaarden",
    "the MDM shows the dependencies between the components, the function specifications and the combinations thereof that are relevant to this decomposition level": "de MDM illustreert de afhankelijkheden tussen de componenten, tussen de functies en combinaties daarvan behorende bij dit decompositieniveau",  # noqa
    "behavior requirements": "gedragseisen",
    "behavior constraints": "gedragsrandvoorwaarden",
    "{} is composed of the following sub-components:": "{} bestaat uit de volgende subcomponenten:",
    "this is the first decomposition level which indicates which components play a role in the environment in which the system at hand must operate": "dit is het eerste decompositieniveau waarin de elementen worden beschreven waarmee het systeem interactie heeft of dient te hebben.",  # noqa
    "subordinate function specifications": "onderliggende functie specificaties",
    "external models": "externe modellen",
    "model definition name": "naam van de model definitie",
    "required variables": "input variabelen",
    "returned variables": "output variabelen",
    "related variables": "gerelateerde variabelen",
    "this goal function requirement automatically migrated from {}": "deze doelfunctie-eis is automatisch ge-migreerd van {}",  # noqa
    "this goal function constraint automatically migrated from {}": "deze doelfunctie-randvoorwaarde is automatisch ge-migreerd van {}",  # noqa
    "system-wide qualitative and quantitative specifications": "systeembrede kwalitatieve and kwantitatieve ontwerpeisen",  # noqa
    "this chapter lists all qualitative and quantitative design specifications that cannot be linked to a component": "dit hoofdstuk bevat alle kwalitatieve and kwantitatieve ontwerpeisen die niet aan een component zijn gerelateerd",  # noqa
    "is a bundle": "een bundel is",
    "are bundles": "bundles zijn",
    "where {} {} of which the following variables are used:": "waar {} {} waaruit de volgende variabelen worden gebruikt:",  # noqa
    "where the full name of variable {} is {}": "waar de variabel {} de volledige naam {} heeft",
    "where, respectively:": "waar, respectivelijk",
    "variable {} has full name {}": "variabel {} de volledige naam {} heeft",
}


@hookimpl
def gettext(key: str):
    """Get translated string."""
    if key in translations:
        return translations[key]
    logger.debug("Cannot find a translation for '{}' in {}.".format(key, __file__))
    return key


_ = gettext


@hookimpl
def linguistic_enumeration(items: List[str]):
    n = len(items)
    if n <= 2:
        return " en ".join(items)
    return ", ".join(items[:-1]) + " en " + items[-1]


@hookimpl
def linguistic_options(items: List[str]):
    n = len(items)
    if n <= 2:
        return " of ".join(items)
    return ", ".join(items[:-1]) + " of " + items[-1]


def subclause_line(s: Dict[str, Any]):
    """Yield subclause line."""

    yield " of ".join([subclause_rule_line(r=r) for r in s["body"]])


def is_number(v: Any) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


drule_auxmap = {
    "must be": ("dient", "te zijn"),
    "shall be": ("zal", "zijn"),
    "should be": ("behoort", "te zijn"),
    "could be": ("zou", "kunnen zijn"),
    "won't": ("zal", "zijn"),
    "is": ("is", ""),
}

cmap = {
    "smaller than": "kleiner dan",
    "at most": "hoogstens",
    "equal to": "gelijk aan",
    "at least": "tenminste",
    "greater than": "groter dan",
    "approximately": "ongeveer",
}


def make_predicate(verb: str) -> str:
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
            return prep + " te " + verb[len(prep) :]

    return " te " + verb


def design_rule_line(r: Dict[str, str]):
    s = r["subject"].split(".")[-1]
    aux = drule_auxmap.get(r["auxiliary"])
    comparison = cmap.get(r["comparison"])

    if is_number(v=r["bound"]["value"]):
        value = r["bound"]["value"]
    elif r["bound"]["value"] == "t.b.d.":
        value = "n.t.b."
    else:
        value = r["bound"]["value"].split(".")[-1]
    unit = ""
    if r["bound"]["unit"]:
        unit = r["bound"]["unit"]

    if r["auxiliary"] == "won't":
        return "{} {} nimmer {} {} {} {}".format(s, aux[0], comparison, value, unit, aux[1])
    else:
        return "{} {} {} {} {} {}".format(s, aux[0], comparison, value, unit, aux[1])


def then_clause_line(s: Dict[str, Any]):
    """Yield subclause line."""

    yield " of ".join([then_clause_rule_line(r=r) for r in s["body"]])


def then_clause_rule_line(r: Dict[str, str]):
    s = r["subject"].split(".")[-1]
    aux = drule_auxmap.get(r["auxiliary"])
    comparison = cmap.get(r["comparison"])

    if is_number(v=r["bound"]["value"]):
        value = r["bound"]["value"]
    elif r["bound"]["value"] == "t.b.d.":
        value = "n.t.b."
    else:
        value = r["bound"]["value"].split(".")[-1]
    unit = ""
    if r["bound"]["unit"]:
        unit = r["bound"]["unit"]

    if r["auxiliary"] == "won't":
        return "{} {} nimmer {} {} {} {}".format(s, aux[0], comparison, value, unit, aux[1])
    else:
        return "{} {} {} {} {} {}".format(aux[0], s, comparison, value, unit, aux[1])


srule_auxmap = {
    "must be": "dient te zijn",
    "shall be": "zal zijn",
    "should be": "behoort te zijn",
    "could be": "zou kunnen zijn",
    "won't": "zal zijn",
    "is": "is",
}


def subclause_rule_line(r: Dict[str, str]):
    s = r["subject"].split(".")[-1]
    aux = srule_auxmap.get(r["auxiliary"])
    comparison = cmap.get(r["comparison"])

    if is_number(v=r["bound"]["value"]):
        value = r["bound"]["value"]
    elif r["bound"]["value"] == "t.b.d.":
        value = "n.t.b."
    else:
        value = r["bound"]["value"].split(".")[-1]
    unit = ""
    if r["bound"]["unit"]:
        unit = r["bound"]["unit"]

    if r["auxiliary"] == "won't":
        return "{} nimmer {} {} {} {}".format(s, comparison, value, unit, aux)
    else:
        return "{} {} {} {} {}".format(s, comparison, value, unit, aux)


@hookimpl
def function_spec_node(node: Node, graph: Graph, html: bool) -> LineGen:
    if node.annotations.esl_info["sub_kind"] == "transformation":
        comp = node.annotations.esl_info["body"]["active"].split(".")[-1]
        aux = node.annotations.esl_info["body"]["auxiliary"]
        verb = node.annotations.esl_info["body"]["verb"]
        in_flows = pm.hook.linguistic_enumeration(
            items=sorted(
                list(
                    set(
                        [
                            graph[flow].annotations.esl_info["bundle_root_name"]
                            if graph[flow].annotations.esl_info["bundle_root_name"]
                            else flow.split(".")[-1]
                            for flow in node.annotations.esl_info["body"]["input_variables"]
                        ]
                    )
                )
            )
        )
        prep = node.annotations.esl_info["body"]["preposition"]
        out_flows = pm.hook.linguistic_enumeration(
            items=sorted(
                list(
                    set(
                        [
                            graph[flow].annotations.esl_info["bundle_root_name"]
                            if graph[flow].annotations.esl_info["bundle_root_name"]
                            else flow.split(".")[-1]
                            for flow in node.annotations.esl_info["body"]["output_variables"]
                        ]
                    )
                )
            )
        )
        if aux == "must":
            line = "{} dient {} {} {} {}".format(
                comp, in_flows, prep, out_flows, make_predicate(verb)
            )
        elif aux == "should":
            line = "{} behoort {} {} {} {}".format(
                comp, in_flows, prep, out_flows, make_predicate(verb)
            )
        elif aux == "could":
            line = "{} zou {} {} {} kunnen {}".format(comp, in_flows, prep, out_flows, verb)
        elif aux == "won't":
            line = "{} zal nimmer {} {} {} {}".format(comp, in_flows, prep, out_flows, verb)
        elif aux == "shall":
            line = "{} zal {} {} {} {}".format(comp, in_flows, prep, out_flows, verb)
        elif aux == "is":
            line = "{} vervult het {} van {} {} {}".format(comp, verb, in_flows, prep, out_flows)
        else:
            line = "{} {} {} {} {} {}".format(comp, aux, verb, in_flows, prep, out_flows)

        # Bundle root varaible dict
        brvdict = defaultdict(list)
        for flow in (
            node.annotations.esl_info["body"]["input_variables"]
            + node.annotations.esl_info["body"]["output_variables"]
        ):
            r = graph[flow].annotations.esl_info["bundle_root_name"]
            if r:
                brvdict[r].append(flow)

    elif node.annotations.esl_info["sub_kind"] == "goal":
        active = node.annotations.esl_info["body"]["active"].split(".")[-1]
        aux = node.annotations.esl_info["body"]["auxiliary"]
        verb = node.annotations.esl_info["body"]["verb"]
        flows = pm.hook.linguistic_enumeration(
            items=sorted(
                list(
                    set(
                        [
                            graph[flow].annotations.esl_info["bundle_root_name"]
                            if graph[flow].annotations.esl_info["bundle_root_name"]
                            else flow.split(".")[-1]
                            for flow in node.annotations.esl_info["body"]["variables"]
                        ]
                    )
                )
            )
        )
        prep = node.annotations.esl_info["body"]["preposition"]
        passive = node.annotations.esl_info["body"]["passive"].split(".")[-1]

        if aux == "must":
            line = "{} dient {} {} {} {}".format(active, flows, prep, passive, make_predicate(verb))
        elif aux == "should":
            line = "{} behoort {} {} {} {}".format(
                active, flows, prep, passive, make_predicate(verb)
            )
        elif aux == "could":
            line = "{} zou {} {} {} kunnen {}".format(active, flows, prep, passive, verb)
        elif aux == "won't":
            line = "{} zal nimmer {} {} {} {}".format(active, flows, prep, passive, verb)
        elif aux == "does":
            line = "{} vervult het {} van {} {} {}".format(active, verb, flows, prep, passive)
        elif aux == "shall":
            line = "{} zal {} {} {} {}".format(active, flows, prep, passive, verb)
        else:
            line = "{} {} {} {} {} {}".format(
                active, aux, make_predicate(verb), flows, prep, passive
            )

        # Bundle root varaible dict
        brvdict = defaultdict(list)
        for flow in node.annotations.esl_info["body"]["variables"]:
            r = graph[flow].annotations.esl_info["bundle_root_name"]
            if r:
                brvdict[r].append(flow)

    if node.annotations.esl_info["body"]["subclauses"]:
        yield lns.cap(line) + ", waarbij:\n"
        yield from lns.unordered(
            [
                "\n".join(subclause_line(s=sc))
                for sc in node.annotations.esl_info["body"]["subclauses"]
            ]
        )
    else:
        yield lns.snt(line)

    if brvdict:
        yield from lns.bundle_clarification(brvdict=brvdict)


@hookimpl
def design_spec_node(node: Node, graph: Graph, html: bool) -> LineGen:
    line = " of ".join([design_rule_line(r) for r in node.annotations.esl_info["body"]])
    if node.annotations.esl_info.get("sub_clauses"):
        yield lns.cap(line) + ", waarbij:\n"
        yield from lns.unordered(
            ["\n".join(subclause_line(s=sc)) for sc in node.annotations.esl_info["sub_clauses"]]
        )
    else:
        yield lns.snt(line)

    bvars = [
        v
        for v in lns.get_design_rule_line_vars(rules=node.annotations.esl_info["body"], g=graph)
        if v.annotations.esl_info["bundle_root_name"]
    ]

    if bvars:
        yield from lns.var_clarification(bvars=bvars)


@hookimpl
def behavior_spec_node(node: Node, graph: Graph, html: bool) -> LineGen:
    clauses = []
    for case in node.annotations.esl_info["cases"]:
        yield lns.cap("situatie {}:\n".format(lns.emph(case["name"])))
        yield ""
        yield "als:"
        yield from lns.unordered(["\n".join(subclause_line(s=sc)) for sc in case["when_clauses"]])
        yield "\n"
        yield "dan:"
        yield from lns.unordered(["\n".join(then_clause_line(s=sc)) for sc in case["then_clauses"]])
        clauses += case["when_clauses"] + case["then_clauses"]

    default = node.annotations.esl_info.get("default")
    if default:
        yield lns.cap("situatie {}:\n".format(lns.emph("default")))
        yield ""
        yield "als geen andere situatie van toepassing is, dan:\n"
        yield from lns.unordered(["\n".join(then_clause_line(s=sc)) for sc in default])
        clauses += default

    bvars = [
        v
        for s in clauses
        for v in lns.get_design_rule_line_vars(rules=s["body"], g=graph)
        if v.annotations.esl_info["bundle_root_name"]
    ]

    if bvars:
        yield from lns.var_clarification(bvars=bvars)


@hookimpl
def need_node(node: Node, graph: Graph, html: bool) -> LineGen:
    subject = node.annotations.esl_info["subject"]
    line = "{} {}".format(
        node.annotations.esl_info["subject"].split(".")[-1],
        node.annotations.esl_info["text"],
    )
    yield lns.snt(line)

    if graph[subject].kind == "variable":
        if graph[subject].annotations.esl_info["bundle_root_name"]:
            yield from lns.var_clarification(bvars=[graph[subject]])
