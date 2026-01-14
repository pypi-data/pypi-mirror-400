"""Methods for casting ESL AST into ragraph.node.Node objects."""

import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

from ragraph.node import Node

from raesl import logger
from raesl.compile import diagnostics
from raesl.compile.ast import exprs, types
from raesl.compile.ast.components import (
    BehaviorFunction,
    ComponentDefinition,
    ComponentInstance,
    Design,
    Flow,
    Goal,
    InstanceArgument,
    Need,
    RelationInstance,
    Transformation,
    VarParam,
)
from raesl.compile.ast.nodes import (
    CompoundVarNode,
    ElementaryVarNode,
    GroupNode,
    VarNode,
)
from raesl.compile.ast.specification import Specification
from raesl.compile.ast.types import ElementaryType, TypeDef
from raesl.compile.instantiating.graph_data import InstNode


class NodeStore:
    """Node storage with multiple catagories for quicker access to specific subsets."""

    categories = [
        "nodes",
        "types",
        "components",
        "variables",
        "needs",
        "goals",
        "transforms",
        "designs",
        "behaviors",
        "relations",
    ]

    def __init__(self):
        for cat in self.categories:
            setattr(self, cat, dict())

    def clear(self):
        """Clear all node categories."""
        for cat in self.categories:
            getattr(self, cat).clear()

    def add(self, node: Node, *args):
        """Add node to :obj:`self.nodes` and any other specified categories in args."""
        name = node.name
        self.nodes[name] = node
        for m in args:
            getattr(self, m)[name] = node
        logger.debug(f"Added ragraph.node.Node '{node.name}' to nodes and {args}.")


class NodeFactory:
    """Node factory. Creates :obj:`Node` objects from a :obj:`Specification`."""

    def __init__(
        self,
        diag_store: diagnostics.DiagnosticStore,
        spec: Optional[Specification] = None,
    ):
        self.diag_store = diag_store
        self.spec = spec
        self.node_store = NodeStore()
        self.type_inst_map = {}

    def _add(self, node: Optional[Node], *args):
        """Proxy for :obj:`NodeStore.add`."""
        self.node_store.add(node, *args)

    def make_nodes(self, spec: Optional[Specification] = None) -> Dict[str, Node]:
        """Instantiate AST and create :obj:`Node` objects accordingly."""
        # Clear maps.
        self.node_store.clear()

        # Set provided spec or try and keep the current one.
        self.spec = self.spec if spec is None else spec
        if self.spec is None:
            return dict()

        # Create types first.
        for t in self.spec.types.values():
            self.type_inst_map[t.type] = t
            tn = make_type_node(t)
            if tn is not None:
                self._add(tn, "types")

        # Create world node and instantiate it (recursively).
        self._add(
            Node(
                name="world",
                kind="component",
                annotations=dict(
                    esl_info=dict(definition_name="world", property_variables=[], comments=[])
                ),
            ),
            "components",
        )
        self._instantiate_component(spec.world, {}, "world")

        post_process_comments(self.node_store.nodes.values())

        return self.node_store.nodes

    def _instantiate_component(
        self,
        comp_def: ComponentDefinition,
        inst_map: Dict[ElementaryVarNode, InstNode],
        inst_name: str,
    ):
        """Instantiate a component definition.

        Arguments
            comp_def: Component definition to instantiate.
            inst_map: Mapping of parameter VarNodes of the component definition
                to InstNodes of the parent. Is not used by the parent afterwards.
            inst_name: Dotted name of the component instance.
        """
        # Keep a separate list of the component variables for property counting checks
        local_varinst_list: List[InstNode] = []
        for var in comp_def.variables:
            varname = [inst_name, var.name_tok.tok_text]  # Dotted (sub) var name.
            var_map = make_variable_instmap(var, varname, var.node)
            local_varinst_list.extend(inst_map.values())
            inst_map.update(var_map)

        # Dump mapping of elementary variable nodes to instance nodes.
        logger.debug("Variable node map of instance {}".format(inst_name))
        logger.debug("\n".join(str(k) + ":" + str(v) for k, v in inst_map.items()))
        logger.debug("")

        # Creating ragraph.node.Node object for all new instance nodes.
        for v in inst_map.values():
            self._add(make_variable_node(v, self.type_inst_map), "variables")

        # Construct child component instances, recursing down to the leaf components.
        for comp_inst in comp_def.component_instances:
            assert comp_inst.compdef is not None
            assert len(comp_inst.arguments) == len(comp_inst.compdef.parameters)

            child_inst_map: Dict[ElementaryVarNode, InstNode] = {}
            for arg, param in zip(comp_inst.arguments, comp_inst.compdef.parameters):
                assert arg.argnode is not None
                result = make_parameter_instmap(param, param.node, arg.argnode, inst_map)
                child_inst_map.update(result)

            # Full dotted name.
            child_inst_name = f"{inst_name}.{comp_inst.inst_name_tok.tok_text}"

            # Add component as a node.
            self._add(
                make_component_node(c=comp_inst, inst_name=child_inst_name, params=child_inst_map),
                "components",
            )
            self._instantiate_component(comp_inst.compdef, child_inst_map, child_inst_name)

            # Set parent of child
            self.node_store.components[child_inst_name].parent = self.node_store.components[
                inst_name
            ]

        # Verify ownership of the variable InstNodes.
        for inst_node in local_varinst_list:
            inst_node.check_owner(self.diag_store)

        # Instantiate need, goal, transform, design, behavior and relation specs.
        for n in comp_def.needs:
            self._add(make_need_node(n, inst_name), "needs")

        for g in comp_def.goals:
            self._add(make_goal_node(g, inst_name, inst_map), "goals")

        for t in comp_def.transforms:
            self._add(make_transform_node(t, inst_name, inst_map), "transforms")

        for d in comp_def.designs:
            self._add(make_design_node(d, inst_name, inst_map), "designs")

        for b in comp_def.behaviors:
            self._add(make_behavior_node(b, inst_name, inst_map), "behaviors")

        for r in comp_def.relations:
            self._add(make_relation_node(r, inst_name, inst_map), "relations")


def make_variable_instmap(
    var: VarParam, varname: List[str], node: VarNode
) -> Dict[ElementaryVarNode, InstNode]:
    """Construct instance nodes for the provided variable.

    Arguments:
        var: Variable represented by the node.
        varname: Collected prefixes of the dotted name so far.
        node: Node to associate with one or more inst nodes.

    Returns:
        Map of the elementary variable nodes to their associated instance nodes.
    """
    assert var.is_variable

    if isinstance(node, ElementaryVarNode):
        instnode = InstNode(".".join(varname), node)
        instnode.add_comment(node.get_comment())
        return {node: instnode}
    else:
        assert isinstance(node, CompoundVarNode)
        varname.append("")  # Will be overwritten in upcoming loop
        inst_map = {}
        for cn in node.child_nodes:
            varname[-1] = cn.name_tok.tok_text
            inst_map.update(make_variable_instmap(var, varname, cn))
        del varname[-1]
        return inst_map


def make_parameter_instmap(
    param: VarParam,
    param_node: VarNode,
    arg_node: VarNode,
    parent_inst_map: Dict[ElementaryVarNode, InstNode],
) -> Dict[ElementaryVarNode, InstNode]:
    """Construct an inst node map for a parameter of a child component instance.

    Arguments:
        param: Parameter definition in the child component definition.
        param_node: VarNode within the parameter in the child component
            definition. Note these are like variables in the child.
        arg_node: Node in the parent that must match with param_node.
            These nodes exist in the parent component, and may contain part of a
            variable group.
        parent_inst_map: Variable instance map of the parent. As component
            instantiation is recursive, this may also include nodes from the
            grand-parent or higher. Should not be modified.

    Returns:
        Instance node map for a parameter.
    """
    if isinstance(param_node, ElementaryVarNode):
        # Elementary parameter node. At this point, the arg_node should also be
        # elementary, and exist as instance node representing part of a variable
        # in the # parent.
        # Link that instance node to the param node in the child.
        assert isinstance(arg_node, ElementaryVarNode)

        instnode = parent_inst_map.get(arg_node)
        assert instnode is not None

        instnode.add_param(param)

        node = param.resolve_element(param.name_tok.tok_text)
        if isinstance(node, ElementaryVarNode):
            instnode.add_comment(node.get_comment())
        elif isinstance(node, CompoundVarNode):
            child = node.resolve_node(instnode.name.split(".")[-1])
            if child:
                instnode.add_comment(child.get_comment())
        return {param_node: instnode}
    else:
        child_map = {}
        assert isinstance(param_node, CompoundVarNode)
        if isinstance(arg_node, CompoundVarNode):
            assert len(param_node.child_nodes) == len(arg_node.child_nodes)
            for param_child, arg_child in zip(param_node.child_nodes, arg_node.child_nodes):
                child_map.update(
                    make_parameter_instmap(param, param_child, arg_child, parent_inst_map)
                )
        else:
            assert isinstance(arg_node, GroupNode)
            assert len(param_node.child_nodes) == len(arg_node.child_nodes)
            for param_child, arg_child in zip(param_node.child_nodes, arg_node.child_nodes):
                child_map.update(
                    make_parameter_instmap(param, param_child, arg_child, parent_inst_map)
                )

        return child_map


def make_type_node(tdef: types.TypeDef) -> Node:
    """Node creation for a type definition.

    Arguments:
      tdef: Type definition for which a node most be created.

    Returns:
      Node of kind `variabel_type`
    """
    a = _make_type_annotations(tdef=tdef)
    if not a:
        return
    return Node(name=tdef.name.tok_text, kind="variable_type", annotations=a)


def _make_type_annotations(tdef: types.TypeDef) -> Dict[str, Dict[str, Any]]:
    """Creating dictionary to annotate `variable_type` nodes.

    Arguments:
      tdef: The type definition for which an annotation dictionary most be created.

    Returns:
      See YAML output spec /components/schemas/VariableTypeAnnotation
    """
    if not isinstance(tdef.type, types.ElementaryType):
        return

    units = [tok.tok_text for tok in tdef.type.units]
    domain = None
    if not tdef.type.intervals:
        return dict(esl_info=dict(units=units, domain=domain))

    domain = []

    for interval in tdef.type.intervals:
        d = dict(
            lowerbound=dict(value=None, unit=None),
            upperbound=dict(value=None, unit=None),
        )
        if interval[0]:
            if interval[0].value:
                d["lowerbound"]["value"] = interval[0].value.tok_text
            if interval[0].unit:
                d["lowerbound"]["unit"] = interval[0].unit.tok_text
        if interval[1]:
            if interval[1].value:
                d["upperbound"]["value"] = interval[1].value.tok_text
            if interval[1].unit:
                d["upperbound"]["unit"] = interval[1].unit.tok_text
        domain.append(d)

    return dict(esl_info=dict(units=units, domain=domain))


def make_variable_node(v: InstNode, type_inst_map: Dict[ElementaryType, TypeDef]) -> Node:
    """Node creation for a variable.

    Arguments:
        v: The variable for which a nodes must be created.

    Returns:
        Node of kind "variable".
    """
    a = _make_variable_annotations(v=v, type_inst_map=type_inst_map)
    return Node(name=v.name, kind="variable", annotations=a)


def _make_variable_annotations(
    v: InstNode,
    type_inst_map: Dict[ElementaryType, TypeDef],
    comments: Optional[List[str]] = [],
) -> Dict[str, Dict[str, Any]]:
    """Creating dictionary for variable annotations.

    Arguments:
        v: The variable for which the annotation dict must be created.
        comments: List of comments attached to the nodes.

    Returns:
        See YAML output spec /components/schemas/VariableAnnotation
    """
    is_property = False
    if v.owners():
        is_property = True

    return dict(
        esl_info=dict(
            is_property=is_property,
            type_ref=type_inst_map[v.variable.the_type].name.tok_text,
            comments=v.comments,
        )
    )


def make_component_node(
    c: ComponentInstance, inst_name: str, params: Dict[ElementaryVarNode, InstNode]
) -> Node:
    """Node creation for a component.

    Arguments:
        c: The component for which a node is created.
        inst_name: The instantiation name of the node.
        params: List of parameters of the component.

    Returns:
        Node of kind "component"
    """
    a = _make_component_annotations(c=c, params=params)
    return Node(name=inst_name, kind="component", annotations=a)


def _make_component_annotations(
    c: ComponentInstance, params: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Dict[str, Any]]:
    """Component annotation creation.

    Arguments:
        c: The component for which the annotations must be created.
        params: List of parameters of the component.

    Returns:
        See YAML output spec /components/schemas/ComponentAnnotation
    """
    property_variables = [
        v.name
        for v in params.values()
        if v.owners() and set(v.owners()).intersection(c.compdef.parameters)
    ]
    return dict(
        esl_info=dict(
            definition_name=c.def_name_tok.tok_text,
            property_variables=property_variables,
            comments=c.comments,
        )
    )


def make_need_node(n: Need, inst_name: str) -> Node:
    """Node creation for a component.

    Arguments:
      n: The need for which a node must be created.
      inst_name: The instation name of the need.

    Returns:
      Node of kind "need"
    """
    name = f"{inst_name}.{n.label_tok.tok_text}"
    a = _make_need_annotations(n=n, inst_prefix=inst_name)
    return Node(name=name, kind="need", annotations=a)


def _make_need_annotations(n: Need, inst_prefix: str) -> Dict[str, Dict[str, Any]]:
    """Need annotation creation.

    Arguments:
      n: The need for which the annotations dict must be created.
      inst_prefix: The instantiation prefix.

    Returns:
      See YAML output spec /components/schemas/ComponentAnnotation.
    """
    return dict(
        esl_info=dict(
            subject=inst_prefix + "." + n.subject_tok.tok_text,
            text=n.description,
            comments=n.comments,
        )
    )


def make_goal_node(g: Goal, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]) -> Node:
    """Goal node creation.

    Arguments:
      g: The goal for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      Node of kind "function".
    """
    name = inst_name + "." + g.label_tok.tok_text
    a = _make_goal_annotations(g=g, inst_name=inst_name, inst_map=inst_map)
    return Node(name=name, kind="function_spec", annotations=a)


def _make_goal_annotations(
    g: Goal, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Dict[str, Any]]:
    """Goal annotation creation.

    Arguments:
      g: The goal for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/FunctionSpecAnnotation.
    """
    body = dict(
        active=inst_name + "." + g.active.tok_text,
        auxiliary=g.doesaux.tok_text,
        verb=g.verb.tok_text,
        variables=_get_variable_inst_names(inst_map, g.flows),
        preposition=g.prepos.tok_text,
        passive=inst_name + "." + g.passive.tok_text,
        subclauses=_make_subclause_annotations(g, inst_map),
    )

    return dict(esl_info=dict(sub_kind="goal", form=g.goal_kind, body=body, comments=g.comments))


def make_transform_node(
    t: Transformation, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Node:
    """Transformation node creation.

    Arguments:
      t: The transformation for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      Node of kind "function_spec".
    """
    name = inst_name + "." + t.label_tok.tok_text
    a = _make_transform_annotations(t=t, inst_name=inst_name, inst_map=inst_map)
    return Node(name=name, kind="function_spec", annotations=a)


def _unfold_compound_var(v: CompoundVarNode) -> List[ElementaryVarNode]:
    """Unfolding CompoundVarNode into a list of ElementartyVarNode"""
    vrs = []
    for v in v.child_nodes:
        if isinstance(v, ElementaryVarNode):
            vrs.append(v)
        elif isinstance(v, CompoundVarNode):
            vrs += _unfold_compound_var(v)

    return vrs


def _get_variable_inst_names(
    inst_map: Dict[ElementaryVarNode, InstNode], flows: List[Flow]
) -> List[str]:
    """Converting list of Flow objects into a list of instantiated variable names."""
    vrs = []
    for f in flows:
        if isinstance(f.flow_node, ElementaryVarNode):
            vrs.append(inst_map.get(f.flow_node).name)
        elif isinstance(f.flow_node, CompoundVarNode):
            vrs += [inst_map[v].name for v in _unfold_compound_var(f.flow_node)]

    return vrs


def _make_transform_annotations(
    t: Transformation, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Dict[str, Any]]:
    """Transform annotation creation.

    Arguments:
      t: The transformation for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/FunctionSpecAnnotation.
    """
    body = dict(
        active=inst_name,
        auxiliary=t.doesaux_tok.tok_text,
        verb=t.verb_tok.tok_text,
        input_variables=_get_variable_inst_names(inst_map, t.in_flows),
        preposition=t.prepos_tok.tok_text,
        output_variables=_get_variable_inst_names(inst_map, t.out_flows),
        subclauses=_make_subclause_annotations(t, inst_map),
    )

    return dict(
        esl_info=dict(
            sub_kind="transformation",
            form=t.transform_kind,
            body=body,
            comments=t.comments,
        )
    )


def make_design_node(
    d: Design, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Node:
    """Design spec node creation.

    Arguments:
      d: The design specification for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      Node of kind "design_spec".
    """
    n = inst_name + "." + d.label_tok.tok_text
    a = _make_design_annotations(d=d, inst_map=inst_map)
    return Node(name=n, kind="design_spec", annotations=a)


def _make_design_annotations(
    d: Design, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Dict[str, any]]:
    """Design spec annotation creation.

    Arguments:
      d: The design spec for which a node must be created.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/DesignSpecAnotation.
    """
    body = _make_design_rule_annotation(expr=d.expr, inst_map=inst_map)
    subs = _make_subclause_annotations(d, inst_map)
    return dict(esl_info=dict(form=d.design_kind, body=body, sub_clauses=subs, comments=d.comments))


def _make_subclause_annotations(
    e: Union[Goal, Transformation, Design], inst_map: Dict[ElementaryVarNode, InstNode]
) -> List[Dict[str, Any]]:
    """Subclause spec annotation creation.

    Arguments:
      e: The relation for which annotations must be created.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      List of YAML output spec /components/schemas/SubclauseSpecAnnotation.
    """
    a = []
    for s in e.sub_clauses:
        name = s.label_tok.tok_text
        form = "requirement"

        # if s.expr.is_constraint:
        #    form = "constraint"

        body = _make_design_rule_annotation(s.expr, inst_map)

        a.append(dict(name=name, form=form, body=body))

    return a


comparison_dict = {
    "least": "at least",
    "most": "at most",
    "equal": "equal to",
    "not": "not equal to",
    "smaller": "smaller than",
    "greater": "greater than",
    "approximately": "approximately",
}

aux_dict = {
    "must": "must be",
    "should": "should be",
    "could": "could be",
    "would": "would be",
    "won't": "won't be",
    "shall": "shall be",
    "is": "is",
}


def _make_design_rule_annotation(
    expr: Union[exprs.RelationComparison, exprs.Disjunction, exprs.ObjectiveComparison],
    inst_map: Dict[ElementaryVarNode, InstNode],
) -> List[Dict[str, Any]]:
    """Design rule spec annotation creation.

    Arguments:
      expr: The the expression for which the annotations must be created.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/DesignRuleSpecArray.
    """
    if isinstance(expr, exprs.RelationComparison):
        return [
            dict(
                subject=inst_map[expr.lhs_var.var_node].name,
                auxiliary=aux_dict[expr.isaux_tok.tok_text],
                comparison=comparison_dict[expr.cmp_tok.tok_text],
                bound=_make_bound_annotation(expr.rhs_varval, inst_map),
            )
        ]
    elif isinstance(expr, exprs.ObjectiveComparison):
        if expr.maximize:
            comparison = "maximized"
        else:
            comparison = "minimized"

        return [
            dict(
                subject=inst_map[expr.lhs_var.var_node].name,
                auxiliary=expr.aux_tok.tok_text,
                comparison=comparison,
                bound=None,
            )
        ]
    elif isinstance(expr, exprs.Disjunction):
        a = []
        for c in expr.childs:
            a.extend(_make_design_rule_annotation(expr=c, inst_map=inst_map))
        return a
    else:
        return []


def make_behavior_node(
    b: BehaviorFunction, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Node:
    """Behavior spec node creation.

    Arguments:
      b: The behavior specification for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      Node of kind "behavior_spec".
    """
    n = inst_name + "." + b.name_tok.tok_text
    a = _make_behavior_annotations(b=b, inst_map=inst_map)
    return Node(name=n, kind="behavior_spec", annotations=a)


def _make_behavior_annotations(
    b: BehaviorFunction, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Dict[str, Any]]:
    """Behavior spec annotation creation.

    Arguments:
      h: The behavior spec for which the annotations must be created.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/BehaviorSpecAnnotation.
    """
    default = []
    if b.default_results:
        default = [
            dict(
                name=r.name_tok.tok_text,
                body=_make_design_rule_annotation(r.result, inst_map),
            )
            for r in b.default_results
        ]

    return dict(
        esl_info=dict(
            form=b.behavior_kind,
            cases=[_make_case_annotations(c, inst_map) for c in b.cases],
            default=default,
            comments=b.comments,
        )
    )


def _make_case_annotations(
    c: BehaviorFunction, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Any]:
    """Case spec annotation creation.

    Arguments:
      r: The behavior specication for which the case annotations must be created.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/CaseSpec.
    """
    return dict(
        name=c.name_tok.tok_text,
        when_clauses=[
            dict(
                name=r.name_tok.tok_text,
                body=_make_design_rule_annotation(r.comparison, inst_map),
            )
            for r in c.conditions
        ],
        then_clauses=[
            dict(
                name=r.name_tok.tok_text,
                body=_make_design_rule_annotation(r.result, inst_map),
            )
            for r in c.results
        ],
    )


def make_relation_node(
    r: RelationInstance, inst_name: str, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Node:
    """Relation spec node creation.

    Arguments:
      r: The relation specification for which a node must be created.
      inst_name: The instantiation name of the component.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      Node of kind "relation_spec".
    """
    n = inst_name + "." + r.inst_name_tok.tok_text
    a = _make_relation_annotations(r, inst_map)
    return Node(name=n, kind="relation_spec", annotations=a)


def _get_arg_inst_names(
    inst_map: Dict[ElementaryVarNode, InstNode], args: List[InstanceArgument]
) -> List[str]:
    """Converting list of InstanceArgument objects into a list of instantiated variable names."""
    vrs = []
    for a in args:
        if isinstance(a.argnode, ElementaryVarNode):
            vrs.append(inst_map.get(a.argnode).name)
        elif isinstance(a.argnode, CompoundVarNode):
            vrs += [inst_map[v].name for v in _unfold_compound_var(a.argnode)]

    return vrs


def _make_relation_annotations(
    r: RelationInstance, inst_map: Dict[ElementaryVarNode, InstNode]
) -> Dict[str, Dict[str, Any]]:
    """Relation spec annotation creation.

    Arguments:
      r: The relation for which a node must be created.
      inst_map: Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/RelationSpecAnnotation.
    """
    reqv = []
    retv = []
    relv = []
    for a, p in zip(r.arguments, r.reldef.params):
        if p.direction == "input":
            reqv.extend(_get_arg_inst_names(inst_map, a))
        elif p.direction == "output":
            retv.extend(_get_arg_inst_names(inst_map, a))
        elif p.direction == "inp_out":
            relv.extend(_get_arg_inst_names(inst_map, a))

    return dict(
        esl_info=dict(
            definition_name=r.def_name_tok.tok_text,
            required_variables=reqv,
            returned_variables=retv,
            related_variables=relv,
            comments=r.comments,
        )
    )


def _make_bound_annotation(
    varval: Union[exprs.Value, exprs.VariableValue],
    inst_map: Dict[ElementaryVarNode, InstNode],
) -> Dict[str, str]:
    """Bound annotation creation

    Arguments:
      varval: The value or variable that denotes the bound.
      inst_map:  Dictionary containing the instantiated variables.

    Returns:
      See YAML output spec /components/schemas/Bound.
    """
    if isinstance(varval, exprs.Value):
        if varval.unit:
            return dict(value=varval.value.tok_text, unit=varval.unit.tok_text)
        else:
            return dict(value=varval.value.tok_text, unit=None)

    assert isinstance(varval, exprs.VariableValue)

    return dict(value=inst_map[varval.var_node].name, unit=None)


TAG_COMMENT_PAT = re.compile(r"^\s*@(?P<tag>[\S]+)[ \t]+(?P<comment>.*)")


def post_process_comments(nodes: List[Node]) -> None:
    """Post-processing comments attached to nodes.

    Arguments:
        nodes: List of nodes for which the comments must be post-processed.

    Note:
        This is a simple implementation to process documentation tags as described
        in LEP0008.
    """
    for n in nodes:
        cms = n.annotations.esl_info.get("comments", [])
        plain_comments = []
        tagged_comments = defaultdict(list)

        for cm in cms:
            match = TAG_COMMENT_PAT.match(cm)
            if match is None:
                plain_comments.append(cm)
            else:
                groups = match.groupdict()
                tagged_comments[groups["tag"]].append(groups["comment"])

        n.annotations.esl_info["comments"] = plain_comments
        n.annotations.esl_info["tagged_comments"] = tagged_comments
