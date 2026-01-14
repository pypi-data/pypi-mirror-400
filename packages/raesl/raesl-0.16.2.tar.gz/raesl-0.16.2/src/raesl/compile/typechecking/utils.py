"""Support functions."""
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

from raesl.compile import diagnostics
from raesl.compile.ast.nodes import VarNode
from raesl.utils import get_first_namepart

if TYPE_CHECKING:
    from raesl.compile.ast.components import (
        BehaviorFunction,
        ComponentDefinition,
        ComponentInstance,
        Design,
        Goal,
        RelationInstance,
        Transformation,
        VariableGroup,
        VarParam,
    )
    from raesl.compile.ast.nodes import Node
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token


def split_arguments(
    params_length: int, multiple_index: Optional[int], arguments: List["Token"]
) -> List[List["Token"]]:
    """Given a list arguments, split them into 'params_length' pieces, where each piece
    has length 1, except piece 'multiple_index' if not None, which takes all the slack.

    Arguments:
        params_length: Number of pieces in the result.
        multiple_index: Index in 'arguments' where the multi-piece starts, only if
            multiple_index is not None.
        arguments: Actual arguments to split in pieces.
    """
    if multiple_index is None:
        assert len(arguments) == params_length
        return [[arg] for arg in arguments]

    assert len(arguments) >= params_length
    assert multiple_index >= 0
    assert multiple_index < params_length
    num_singular = params_length - 1
    length_multi = len(arguments) - num_singular
    after_multiple = multiple_index + length_multi

    return (
        [[arg] for arg in arguments[:multiple_index]]
        + [arguments[multiple_index:after_multiple]]
        + [[arg] for arg in arguments[after_multiple:]]
    )


def construct_var_param_map(comp_def: "ComponentDefinition") -> Dict[str, "VarParam"]:
    """Construct a dict of variable / parameter names to their definitions.

    Arguments:
        comp_def: Definition to search for available variables and parameters.

    Returns:
        Dictionary of names to their definitions.
    """
    vps: Dict[str, "VarParam"] = {}  # Map of name to definition.
    for var in comp_def.variables:
        vps[var.name_tok.tok_text] = var
    for param in comp_def.parameters:
        vps[param.name_tok.tok_text] = param
    return vps


def construct_vargroup_map(
    comp_def: "ComponentDefinition",
) -> Dict[str, "VariableGroup"]:
    """Construct a dict of variable groups names to their definitions.

    Arguments:
        comp_def: Definition to search for available variables and parameters.

    Returns:
        Dictionary of group names to their definitions.
    """
    return dict((var.name_tok.tok_text, var) for var in comp_def.var_groups)


def construct_comp_instances_map(
    comp_def: "ComponentDefinition",
) -> Dict[str, "ComponentInstance"]:
    """
    Construct a dict of child component instance names of the given
    component definition.

    :param comp_def: Definition to search for available component instances.
    :return: Dictionary of component instance names to their instances.
    """
    compinsts = {}
    for cinst in comp_def.component_instances:
        compinsts[cinst.inst_name_tok.tok_text] = cinst
    return compinsts


def construct_verb_prepos_combis(spec: "Specification") -> Set[Tuple[str, str]]:
    """
    Construct a set with all defined verb/prepos combinations.
    """
    return set((vpp.verb.tok_text, vpp.prepos.tok_text) for vpp in spec.verb_prepos)


def construct_relinst_goal_transform_design_behavior_map(
    comp_def: "ComponentDefinition",
) -> Dict[str, Union["RelationInstance", "Goal", "Transformation", "Design", "BehaviorFunction"],]:
    """Construct a dict to quickly find goals, transformations, designs, and behaviors
    by their label name.

    Arguments:
        comp_def: Definition to search.

    Returns:
        Dictionary of labels to their goals, transformations, designs, and behaviors.
    """
    label_map: Dict[
        str,
        Union["RelationInstance", "Goal", "Transformation", "Design", "BehaviorFunction"],
    ]
    label_map = {}
    for relinst in comp_def.relations:
        label_map[relinst.inst_name_tok.tok_text] = relinst
    for goal in comp_def.goals:
        label_map[goal.label_tok.tok_text] = goal
    for trans in comp_def.transforms:
        label_map[trans.label_tok.tok_text] = trans
    for design in comp_def.designs:
        label_map[design.label_tok.tok_text] = design
    for behavior in comp_def.behaviors:
        label_map[behavior.name_tok.tok_text] = behavior
    return label_map


def resolve_var_param_node(
    name_tok: "Token",
    avail_vps: Dict[str, "VarParam"],
    reported_names: Set[str],
    diag_store: diagnostics.DiagnosticStore,
) -> Optional["VarNode"]:
    """Resolve the (possibly sub)node of a variable or parameter indicated by 'name'.
    If it fails, report an error if necessary.

    Arguments:
        name_tok: Name of the node to obtain, may contain a dotted name.
        avail_vps: Variables and parameters available in the context.
        reported_names: Non-existing names and prefixes that are reported already.
        diag_store: Storage for found diagnostics.

    Returns:
        The node represented by the name, or None if it could not be found.
            In the latter case, an problem exists indicating failure to find the node.
    """
    node = resolve_var_param_group_node(name_tok, avail_vps, None, reported_names, diag_store)
    if node is None:
        return None
    assert isinstance(node, VarNode)
    return node


def resolve_var_param_group_node(
    name_tok: "Token",
    avail_vps: Optional[Dict[str, "VarParam"]],
    avail_vgroups: Optional[Dict[str, "VariableGroup"]],
    reported_names: Set[str],
    diag_store: diagnostics.DiagnosticStore,
) -> Optional["Node"]:
    """Resolve the provided (possibly dotted) name to a node from a variable, parameter
    or variable group.

    Arguments:
        name_tok: Name of the node to obtain, may contain a dotted name.
        avail_vps: Available variables and parameters, may be None.
        avail_vgroups: Available variable groups, may be None.
        reported_names: Non-existing variables, parameters, and groups that are
            reported already.
        diag_store: Destination for found diagnostics.

    Returns:
        The node represented by the name. It can be a Node if the name points at a
            variable groups. It is always a VarNode if the nam points at a variable or
            parameter.
    """
    first_part = get_first_namepart(name_tok.tok_text)
    if avail_vgroups is not None:
        vgrp = avail_vgroups.get(first_part)
        if vgrp is not None:
            i = name_tok.tok_text.find(".")
            if i >= 0:
                # It is a dotted name, which is not allowed in a group.
                # Report an error if not done already.
                if first_part not in reported_names:
                    reported_names.add(first_part)
                    diag_store.add(
                        diagnostics.E224(
                            "variable group",
                            f"selections like '{name_tok.tok_text[i:]}'",
                            location=name_tok.get_location(len(first_part)),
                        )
                    )
                    return None

            return vgrp.node

    # No variable groups, or no match, try variable or parameters.
    if avail_vps is not None:
        varparam = avail_vps.get(first_part)
        if varparam is not None:
            node = varparam.resolve_node(name_tok.tok_text)
            if node is not None:
                return node

            # varparam.resolve_node failed. Do report multiple times for the same
            # var/param for different dotted suffixes.
            if name_tok.tok_text not in reported_names:
                reported_names.add(name_tok.tok_text)

                kind = {True: "variable", False: "parameter"}[varparam.is_variable]
                offset = varparam.get_error_position(name_tok.tok_text)
                # Cannot resolve part of a dotted name.
                diag_store.add(
                    diagnostics.E225(
                        name_tok.tok_text[offset:],
                        first_part,
                        kind,
                        location=name_tok.get_location(offset),
                    )
                )

            return None

    # Name does not exist.
    if first_part not in reported_names:
        reported_names.add(first_part)

        if avail_vps is not None:
            if avail_vgroups is not None:
                kind = "variable, parameter, or variable group instance"
            else:
                kind = "variable or parameter instance"
        else:
            assert avail_vgroups is not None, "Must have at least one set of names."
            kind = "variable group instance"
        diag_store.add(diagnostics.E203(kind, name=first_part, location=name_tok.get_location()))

    return None
