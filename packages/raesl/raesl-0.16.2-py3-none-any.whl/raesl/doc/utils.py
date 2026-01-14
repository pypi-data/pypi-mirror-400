"""Doc generation utility functions."""

from typing import List

from ragraph.graph import Graph
from ragraph.node import Node


def get_component_goals(
    component: Node, graph: Graph, constraint: bool = True, inherited: bool = True
) -> List[Node]:
    """Get relevant goal requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    ancestors = set([a.name for a in component.ancestors]) if inherited else set()
    goals = [
        n
        for n in graph.nodes
        if n.kind == "function_spec"
        and n.annotations.esl_info.get("sub_kind") == "goal"
        and n.annotations.esl_info.get("form") == form
        and (
            n.annotations.esl_info["body"].get("active") in ancestors
            if inherited
            else n.annotations.esl_info["body"].get("active") == component.name
        )
        and [e for e in graph.edges_between(component, n) if e.kind == "mapping_dependency"]
    ]
    return goals


def get_component_transformations(
    component: Node, graph: Graph, constraint: bool = True
) -> List[Node]:
    """Get relevant transformation requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    transformations = [
        n
        for n in graph.nodes
        if n.kind == "function_spec"
        and n.annotations.esl_info.get("sub_kind") == "transformation"
        and n.annotations.esl_info.get("form") == form
        and n.annotations.esl_info["body"].get("active") == component.name
    ]
    return transformations


def get_component_behaviors(component: Node, graph: Graph, constraint: bool = True) -> List[Node]:
    """Get relevant behavior requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    return [
        b
        for b in graph.nodes
        if b.kind == "behavior_spec"
        and b.annotations.esl_info.get("form") == form
        and graph[component.name, b.name]
    ]


def get_component_designs(component: Node, graph: Graph, constraint: bool = True) -> List[Node]:
    """Get relevant design requirements or constraints for a component."""
    form = "constraint" if constraint else "requirement"
    return [
        d
        for d in graph.nodes
        if d.kind == "design_spec"
        and d.annotations.esl_info.get("form") == form
        and graph[component.name, d.name]
    ]


def get_global_designs(graph: Graph, constraint: bool = True) -> List[Node]:
    """Get globally relevant design requirments or constraints."""
    form = "constraint" if constraint else "requirement"
    dc_dict = {}
    for e in graph.edges:
        if e.source.kind != "component":
            continue
        dc_dict[e.target.name] = e.source.name

    drs = [
        d
        for d in graph.nodes
        if d.kind == "design_spec"
        and d.annotations.esl_info.get("form") == form
        and d.name not in dc_dict
    ]

    return drs


def get_component_needs(component: Node, graph: Graph) -> List[Node]:
    """Get relevant needs for a component."""
    subjects = set([n.name for n in graph.targets_of(component) if n.kind != "component"])
    subjects.add(component.name)
    return [
        n for n in graph.nodes if n.kind == "need" and n.annotations.esl_info["subject"] in subjects
    ]


def get_global_needs(graph: Graph) -> List[Node]:
    """Get globally relevant needs."""
    sc_dict = {}
    for e in graph.edges:
        if e.source.kind != "component":
            continue
        sc_dict[e.target.name] = e.source.name

    all_needs = graph.get_nodes_by_kind("need")

    def get_subject(need):
        return need.annotations.esl_info["subject"]

    return [
        need
        for need in all_needs
        if get_subject(need) not in sc_dict and graph[get_subject(need)].kind != "component"
    ]


def get_component_relations(component: Node, graph: Graph) -> List[Node]:
    """Get relevant relations for a component."""
    return [n for n in graph.nodes if n.kind == "relation_spec" and graph[component.name, n.name]]


def get_component_properties(component: Node, graph: Graph) -> List[Node]:
    """Get relevant properties for a component."""
    return [graph[prop] for prop in component.annotations.esl_info.get("property_variables", [])]
