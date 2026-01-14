"""English localization."""

from collections import defaultdict
from typing import Any, Dict, Generator, List

from ragraph.graph import Graph
from ragraph.node import Node

import raesl.doc.lines as lns
from raesl.doc.locales import hookimpl, pm

LineGen = Generator[str, None, None]

translations = {"world": "the world"}


@hookimpl
def gettext(key: str):
    """Get translated string."""
    if key in translations:
        return translations[key]
    return key


_ = gettext


@hookimpl
def linguistic_enumeration(items: List[str]) -> str:
    n = len(items)
    if n <= 2:
        return " and ".join(items)

    return ", ".join(items[:-1]) + ", and " + items[-1]


@hookimpl
def linguistic_options(items: List[str]) -> str:
    return " or ".join(items)


# Node based hook implementations
def subclause_line(s: Dict[str, Any]):
    """Yield subclause line."""

    yield " or ".join([design_rule_line(r=r) for r in s["body"]])


def is_number(v: Any) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


def design_rule_line(r: Dict[str, str]):
    s = r["subject"].split(".")[-1]
    aux = r["auxiliary"]
    comparison = r["comparison"]
    if comparison == "maximized" or comparison == "minimized":
        return "{} {} {}".format(s, aux, comparison)
    if is_number(v=r["bound"]["value"]):
        value = r["bound"]["value"]
    elif r["bound"]["value"] == "t.b.d.":
        value = "t.b.d."
    else:
        value = r["bound"]["value"].split(".")[-1]
    unit = ""
    if r["bound"]["unit"]:
        unit = r["bound"]["unit"]

    return "{} {} {} {} {}".format(s, aux, comparison, value, unit)


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
                            graph[flow].annotations.esl_info.get("bundle_root_name")
                            if graph[flow].annotations.esl_info.get("bundle_root_name")
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
                            graph[flow].annotations.esl_info.get("bundle_root_name")
                            if graph[flow].annotations.esl_info.get("bundle_root_name")
                            else flow.split(".")[-1]
                            for flow in node.annotations.esl_info["body"]["output_variables"]
                        ]
                    )
                )
            )
        )
        line = "{} {} {} {} {} {}".format(comp, aux, verb, in_flows, prep, out_flows)

        # Bundle root variable dict
        brvdict = defaultdict(list)
        for flow in (
            node.annotations.esl_info["body"]["input_variables"]
            + node.annotations.esl_info["body"]["output_variables"]
        ):
            r = graph[flow].annotations.esl_info.get("bundle_root_name")
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
                            graph[flow].annotations.esl_info.get("bundle_root_name")
                            if graph[flow].annotations.esl_info.get("bundle_root_name")
                            else flow.split(".")[-1]
                            for flow in node.annotations.esl_info["body"]["variables"]
                        ]
                    )
                )
            )
        )
        prep = node.annotations.esl_info["body"]["preposition"]
        passive = node.annotations.esl_info["body"]["passive"].split(".")[-1]
        line = "{} {} {} {} {} {}".format(active, aux, verb, flows, prep, passive)

        # Bundle root variable dict
        brvdict = defaultdict(list)
        for flow in node.annotations.esl_info["body"]["variables"]:
            r = graph[flow].annotations.esl_info.get("bundle_root_name")
            if r:
                brvdict[r].append(flow)

    if node.annotations.esl_info["body"]["subclauses"]:
        yield lns.cap(line) + ", with subclauses:\n"
        yield from lns.unordered(
            [
                "\n".join(subclause_line(s=sc))
                for sc in node.annotations.esl_info["body"]["subclauses"]
            ],
            html=html,
        )
    else:
        yield lns.snt(line)

    if brvdict:
        yield from lns.bundle_clarification(brvdict=brvdict, html=html)


@hookimpl
def design_spec_node(node: Node, graph: Graph, html: bool) -> LineGen:
    line = " or ".join([design_rule_line(r) for r in node.annotations.esl_info["body"]])
    if node.annotations.esl_info.get("sub_clauses", "node"):
        yield lns.cap(line) + ", with subclauses:\n"
        yield from lns.unordered(
            ["\n".join(subclause_line(s=sc)) for sc in node.annotations.esl_info["sub_clauses"]],
            html=html,
        )
    else:
        yield lns.snt(line)

    bvars = [
        v
        for v in lns.get_design_rule_line_vars(rules=node.annotations.esl_info["body"], g=graph)
        if v.annotations.esl_info.get("bundle_root_name")
    ]

    if bvars:
        yield from lns.var_clarification(bvars=bvars, html=html)


@hookimpl
def behavior_spec_node(node: Node, graph: Graph, html: bool) -> LineGen:
    clauses = []
    for case in node.annotations.esl_info["cases"]:
        yield lns.cap("case {}:\n".format(lns.emph(case["name"], html=html)))
        yield ""
        yield "when:"
        yield from lns.unordered(
            ["\n".join(subclause_line(s=sc)) for sc in case["when_clauses"]], html=html
        )
        yield "\n"
        yield "then:"
        yield from lns.unordered(
            ["\n".join(subclause_line(s=sc)) for sc in case["then_clauses"]], html=html
        )
        clauses += case["when_clauses"] + case["then_clauses"]

    default = node.annotations.esl_info.get("default")
    if default:
        yield lns.cap("case {}:\n".format(lns.emph("default", html=html)))
        yield ""
        yield "when no other case applies, then:\n"
        yield from lns.unordered(["\n".join(subclause_line(s=sc)) for sc in default], html=html)
        clauses += default

    bvars = [
        v
        for s in clauses
        for v in lns.get_design_rule_line_vars(rules=s["body"], g=graph)
        if v.annotations.esl_info.get("bundle_root_name")
    ]

    if bvars:
        yield from lns.var_clarification(bvars=bvars, html=html)


@hookimpl
def need_node(node: Node, graph: Graph, html: bool) -> LineGen:
    subject = node.annotations.esl_info["subject"]
    line = "{} {}".format(
        subject.split(".")[-1],
        node.annotations.esl_info["text"],
    )
    yield lns.snt(line)

    if graph[subject].kind == "variable":
        if graph[subject].annotations.esl_info.get("bundle_root_name"):
            yield from lns.var_clarification(bvars=[graph[subject]], html=html)
