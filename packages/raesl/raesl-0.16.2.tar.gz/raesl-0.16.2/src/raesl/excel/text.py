"""Raw text export of ESL requirement nodes."""

from textwrap import indent
from typing import Any, Dict, Iterable, List, Optional

from ragraph.graph import Graph
from ragraph.node import Node

from raesl.doc import lines


def requirement_text(requirement: Node, graph: Graph, skip: Optional[str] = "world") -> str:
    """Re-format the requirement as text."""
    info = requirement.annotations.esl_info
    if requirement.kind == "function_spec":
        if info["sub_kind"] == "goal":
            func = goal_text
        elif info["sub_kind"] == "transformation":
            func = transformation_text
        else:
            raise ValueError(f"Unknown sub kind for function spec: {info['sub_kind']}.")
    elif requirement.kind == "design_spec":
        func = design_text
    elif requirement.kind == "behavior_spec":
        func = behavior_text
    elif requirement.kind == "need":
        func = need_text
    else:
        raise ValueError(f"Unknown requirement type of node {requirement.json_dict}.")

    text = func(requirement, graph, skip=skip)

    if (
        requirement.kind == "function_spec"
        and info["body"].get("subclauses")
        or requirement.kind == "design_spec"
        and info["sub_clauses"]
    ):
        return "{}, with subclauses:\n{}".format(
            text, subclauses_text(requirement, graph, skip=skip, spaces=2)
        )
    else:
        return text


def goal_text(requirement: Node, graph: Graph, skip: Optional[str] = "world") -> str:
    """Re-format goal requirement as text."""
    body = requirement.annotations.esl_info["body"]
    text = "{active} {auxiliary} {verb} {variables} {preposition} {passive}".format(
        active=lines.node_path(body["active"], italic=False, arrows=False, skip=skip),
        auxiliary=body["auxiliary"],
        verb=body["verb"],
        variables=", ".join(
            lines.var_path(graph[var], italic=False, arrows=False, skip=skip)
            for var in body["variables"]
        ),
        preposition=body["preposition"],
        passive=lines.node_path(body["passive"], italic=False, arrows=False, skip=skip),
    )
    return text


def transformation_text(requirement: Node, graph: Graph, skip: Optional[str] = "world") -> str:
    """Re-format transformation requirement as text."""
    body = requirement.annotations.esl_info["body"]
    text = ("{auxiliary} {verb} {input_variables} {preposition} {output_variables}").format(
        auxiliary=body["auxiliary"],
        verb=body["verb"],
        input_variables=", ".join(
            lines.var_path(graph[var], italic=False, arrows=False, skip=skip)
            for var in body["input_variables"]
        ),
        preposition=body["preposition"],
        output_variables=", ".join(
            lines.var_path(graph[var], italic=False, arrows=False, skip=skip)
            for var in body["output_variables"]
        ),
    )
    return text


def designrule_text(
    body: Dict[str, Any],
    graph: Graph,
    skip: Optional[str] = "world",
) -> str:
    """Re-format design rule as text."""
    return "{subject} {auxiliary} {comparison} {value} {unit}".format(
        subject=lines.var_path(graph[body["subject"]], italic=False, arrows=False, skip=skip),
        auxiliary=body["auxiliary"],
        comparison=body["comparison"],
        value=body["bound"]["value"],
        unit=body["bound"]["unit"],
    )


def designclause_text(
    bodies: List[Dict[str, Any]],
    graph: Graph,
    label: Optional[str] = None,
    skip: Optional[str] = "world",
) -> str:
    """Re-format design clause as text."""
    rule = " or ".join(designrule_text(rule, graph, skip=skip) for rule in bodies)
    return "{}: {}".format(label, rule) if label else rule


def design_text(requirement: Node, graph: Graph, skip: Optional[str] = "world") -> str:
    """Re-format design requirement as text."""
    return designclause_text(requirement.annotations.esl_info["body"], graph, skip=skip)


def subclauses_text(
    requirement: Node, graph: Graph, skip: Optional[str] = "world", spaces: int = 2
) -> str:
    """Re-format subclauses as text."""
    if requirement.kind == "function_spec":
        clauses = requirement.annotations.esl_info["body"]["subclauses"]
    elif requirement.kind == "design_spec":
        clauses = requirement.annotations.esl_info["sub_clauses"]
    else:
        raise ValueError("Unsupported node kind '{}'.".format(requirement.kind))
    return "\n".join(
        indent(
            designclause_text(clause["body"], graph, label=clause["name"], skip=skip),
            prefix="{}{}".format(spaces * " ", "- " if spaces else ""),
        )
        for clause in clauses
    )


def case_text(case: Dict[str, Any], graph: Graph, skip: str = "world") -> str:
    """Re-format behavior requirement case as text."""
    return "{name}:\n  when:\n{whens}\n  then:\n{thens}".format(
        name=case["name"],
        whens=indent(
            "\n".join(
                designclause_text(clause["body"], graph, label=clause["name"], skip=skip)
                for clause in case["when_clauses"]
            ),
            prefix=4 * " ",
        ),
        thens=indent(
            "\n".join(
                designclause_text(clause["body"], graph, label=clause["name"], skip=skip)
                for clause in case["then_clauses"]
            ),
            prefix=4 * " ",
        ),
    )


def behavior_text(requirement: Node, graph: Graph, skip: Optional[str] = "world") -> str:
    """Re-format behavior requirement as text."""
    info = requirement.annotations.esl_info

    text = "\n\n".join(case_text(case, graph, skip=skip) for case in info["cases"])
    if info["default"]:
        text += "\n\nwhen no other case applies:\n{}".format(
            indent(
                "\n".join(
                    designclause_text(clause["body"], graph, label=clause["name"], skip=skip)
                    for clause in info["default"]
                ),
                prefix=4 * " ",
            ),
        )
    return text


def need_text(requirement: Node, graph: Graph, skip: Optional[str] = "world") -> str:
    """Re-format need as text."""
    info = requirement.annotations.esl_info
    text = ("{subject} {text}").format(
        subject=lines.var_path(graph[info["subject"]], italic=False, arrows=False, skip=skip),
        text=info["text"],
    )
    return text


def get_common_parts(strings: Iterable[str]) -> List[str]:
    """Find out the largest shared substrings separated on dots '.'."""
    result = []
    # Get dotted string splits, reversed so later pops start at the first part.
    splits = [s.split(".")[::-1] for s in strings]
    if len(splits) == 1:
        return splits[0][::-1]
    while True:
        try:
            parts = [s.pop() for s in splits]
            head = parts[0]
            for p in parts[1:]:
                if p != head:
                    return result
            result.append(head)
        except IndexError:
            return result


def strip_prefix(input: str, prefix: str) -> str:
    """Strip a prefix from a string if it starts with it."""
    if input.startswith(prefix):
        return input[len(prefix) :]
    return input


def abbreviate_comparison(comp_str: str) -> str:
    """Use symbols instead of full text for comparison text."""
    if comp_str == "equal to":
        return '="=="'
    elif comp_str == "at most":
        return '="<="'
    elif comp_str == "at least":
        return '=">="'
    elif comp_str == "smaller than":
        return '="<"'
    elif comp_str == "greater than":
        return '=">"'
    elif comp_str == "maximized":
        return '="++"'
    elif comp_str == "minimized":
        return '="--"'
    else:
        return comp_str
