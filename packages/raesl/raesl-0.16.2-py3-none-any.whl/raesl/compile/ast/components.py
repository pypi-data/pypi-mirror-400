"""Component definitions with their contents."""

from typing import TYPE_CHECKING, Generator, List, Optional, Union

from raesl.compile.ast import comment_storage
from raesl.utils import split_first_dot

if TYPE_CHECKING:
    from raesl.compile.ast.exprs import (
        Comparison,
        Disjunction,
        Expression,
        RelationComparison,
    )
    from raesl.compile.ast.nodes import Node, VarNode
    from raesl.compile.ast.relations import RelationDefinition
    from raesl.compile.ast.types import BaseType
    from raesl.compile.scanner import Token


# Kinds of goals and transformations.
CONSTRAINT = "constraint"
REQUIREMENT = "requirement"


class ComponentDefinition(comment_storage.DefaultDocStore):
    """ESL component definition.

    Arguments:
        pos_tok: Position of the definition. Either the name token or the 'world' token.
        name_tok: Token with the name of the component definition, None means 'world'.

    Attributes:
        variables: Variables of the component definition.
        parameters: Parameters of the component definition.
        var_groups: Groups of variables with a name.
        component_instances: Component instances of the component definition.
        needs: Needs of the component definition.
        goals: Goals of the component definition.
        transforms: Transformations of the component definition.
        designs: Designs of the component definition.
        relations: Relation instances of the component definition.
        behaviors: Behavior functions of the component definition.
    """

    def __init__(self, pos_tok: "Token", name_tok: Optional["Token"]):
        super(ComponentDefinition, self).__init__(name_tok)
        self.pos_tok = pos_tok
        self.name_tok = name_tok

        self.variables: List[VarParam] = []
        self.parameters: List[VarParam] = []
        self.var_groups: List[VariableGroup] = []
        self.component_instances: List[ComponentInstance] = []
        self.needs: List[Need] = []
        self.goals: List[Goal] = []
        self.transforms: List[Transformation] = []
        self.designs: List[Design] = []
        self.relations: List[RelationInstance] = []
        self.behaviors: List["BehaviorFunction"] = []


class VarParam(comment_storage.DocStore):
    """ESL component definition variable or parameter.

    Arguments:
        is_variable: Whether the object represents a variable.
        name_tok: Token with the name of the variable being defined.
        type_tok: Token with the name of the type of the variable being defined.
        is_property: Whether the parameter is a property.

    Attributes:
        type: Type of the variable, if it exists. Set during type checking.
    """

    def __init__(
        self,
        is_variable: bool,
        name_tok: "Token",
        type_tok: "Token",
        is_property: bool = False,
    ):
        super(VarParam, self).__init__(name_tok)
        self.is_variable = is_variable
        self.name_tok = name_tok
        self.type_tok = type_tok
        self.is_property = is_property
        self.type: Optional["BaseType"] = None

        self.node: Optional["VarNode"] = None

        # Variables are never explicit property, since they naturally belong
        # to the component defining them.
        assert not self.is_property or not self.is_variable

    def resolve_node(self, name: str) -> Optional["VarNode"]:
        """Find the varparam (sub) node that matches the dotted 'name'.

        Arguments:
            name: Possibly dotted name that should point at an existing sub-node.
                The empty string denotes 'self'.

        Returns:
            The node that matches the name, or None if no such node exists. In the
                latter case, use 'self.get_error_position(name)' to get
                an indication where the match fails in the name.
        """
        local_name, remaining_name, _dot_length = split_first_dot(name)

        if self.name_tok.tok_text != local_name:
            return None

        assert self.node is not None, "Trying to use non-existing node of '{}'".format(
            self.name_tok.tok_text
        )
        return self.node.resolve_node(remaining_name)

    def resolve_element(self, name: str) -> Optional[comment_storage.DocAddElement]:
        node = self.resolve_node(name)
        if node is None:
            return None
        else:
            assert isinstance(node, comment_storage.DocAddElement)
            return node

    def get_error_position(self, name: str) -> int:
        """Return the index in the given string where an error occurs in resolving the
        node.

        Arguments:
            name: Name of the element to find.

        Returns:
            Approximated index in the string where matching the element fails.
            Returned value has no meaning if resolving a node succeeds.
        """
        local_name, remaining_name, dot_length = split_first_dot(name)

        if self.name_tok.tok_text != local_name:
            return 0  # Local name == first name is wrong.
        else:
            # Ask child about the position of the error.
            offset = self.node.get_error_position(remaining_name)
            return offset + len(local_name) + dot_length

    def __repr__(self):
        if self.is_variable:
            kind = "Variable"
        else:
            kind = "Parameter"
        text = "{}[{}, {}, {}]"
        return text.format(kind, self.name_tok.tok_text, self.type_tok.tok_text, self.is_property)


class VariableGroup:
    """One variable group in ESL (a named group of variables).

    It has no documentation comment, as its only purpose is to enable interfacing
    to child components.

    As a variable group doesn't need to contain uniquely named variables, their names
    cannot be used to build a Compound type. Therefore, it just stays a group, and it
    gets dealt with in component instantiation.

    Arguments:
        name_tok: Token with the name of the group being defined.
        variablepart_names: Tokens with possibly dotted name of variable parts in the
            group.

    Attributes:
        node: Node representing the group, if available.
    """

    def __init__(self, name_tok: "Token", variablepart_names: List["Token"]):
        self.name_tok = name_tok
        self.variablepart_names = variablepart_names

        # Set during type checking.
        self.node: Optional["Node"] = None


class InstanceArgument:
    """Actual argument of a component or relation.

    Arguments:
        name_tok: Name of the actual argument.
        argnode: Node of the argument, filled during type checking.
    """

    def __init__(self, name_tok: "Token", argnode: Optional["Node"] = None):
        self.name_tok = name_tok
        self.argnode = argnode


class ComponentInstance(comment_storage.DefaultDocStore):
    """ESL component instance in a component definition.

    Arguments:
        inst_name_tok: Token with the name of the component instance.
        def_name_tok: Token withe the name of the component definition to apply.

    Attributes:
        arguments: Arguments of the instance.
        compdef: Component definition matching the name in 'def_name_tok', if it exists.
            Set during type checking.
    """

    def __init__(self, inst_name_tok: "Token", def_name_tok: "Token"):
        super(ComponentInstance, self).__init__(inst_name_tok)
        self.inst_name_tok = inst_name_tok
        self.def_name_tok = def_name_tok
        self.arguments: List[InstanceArgument] = []

        self.compdef: Optional[ComponentDefinition] = None


class RelationInstance(comment_storage.DefaultDocStore):
    """ESL relation instance in a component definition.

    Arguments:
        inst_name_tok: Token with the name of the relation instance.
        def_name_tok: Token withe the name of the relation definition to apply.
        arguments: Arguments of the instance. One element for each parameter, where one
            element may have several arguments due to the 'one or more' feature.
        reldef: Relation definition of this instance.
    """

    def __init__(
        self,
        inst_name_tok: "Token",
        def_name_tok: "Token",
        arguments: List[List[InstanceArgument]],
        reldef: Optional["RelationDefinition"],
    ):
        super(RelationInstance, self).__init__(inst_name_tok)
        self.inst_name_tok = inst_name_tok
        self.def_name_tok = def_name_tok
        self.arguments = arguments
        self.reldef = reldef


class Flow:
    """Flow in a goal or Transformation.

    Arguments:
        name_tok: Dotted name of the flow.

    Attributes:
        flow_node: If not None, node represented by the flow.
    """

    def __init__(self, name_tok: "Token") -> None:
        self.name_tok = name_tok
        self.flow_node: Optional[VarNode] = None


class Goal(comment_storage.DefaultDocStore):
    """Goal in an ESL component definition.

    Arguments:
        label_tok: Label name of the goal.
        active: Token with the name of the active component.
        doesaux: 'does' or auxiliary word token.
        verb: Verb of the goal.
        flows: Flows of the goal.
        prepos: Token with the preposition word.
        passive: Token with the name of the passive component.

    Attributes:
        goal_kind: Kind of goal, filled after construction.
            Either 'requirement' or 'constraint' string.
        sub_clauses: Sub-clauses of the goal.
        active_comp: If not None, resolved active component instance of the goal.
        passive_comp: If not None, resolved passive component instance of the goal.
    """

    def __init__(
        self,
        label_tok: "Token",
        active: "Token",
        doesaux: "Token",
        verb: "Token",
        flows: List[Flow],
        prepos: "Token",
        passive: "Token",
    ):
        super(Goal, self).__init__(label_tok)
        self.goal_kind: Optional[str] = None
        self.label_tok = label_tok
        self.active = active
        self.doesaux = doesaux
        self.verb = verb
        self.flows = flows
        self.prepos = prepos
        self.passive = passive
        self.sub_clauses: List[SubClause] = []

        self.active_comp: Optional[ComponentInstance] = None
        self.passive_comp: Optional[ComponentInstance] = None


class Transformation(comment_storage.DefaultDocStore):
    """Transformation in a component.

    Arguments:
        label_tok: Label name of the transformation.
        doesaux_tok: 'does' or aux word token.
        verb_tok: Verb of the transformation.
        in_flows: Inputs required for the transformation.
        prepos_tok: Preposition of the transformation.
        out_flows: Outputs resulting from the transformation.

    Attributes:
        transform_kind: Kind of transformation, filled after construction.
            Either 'requirement' or 'constraint' string.
        sub_clauses: Sub-clauses of the transformation.
    """

    def __init__(
        self,
        label_tok: "Token",
        doesaux_tok: "Token",
        verb_tok: "Token",
        in_flows: List[Flow],
        prepos_tok: "Token",
        out_flows: List[Flow],
    ):
        super(Transformation, self).__init__(label_tok)
        self.transform_kind: Optional[str] = None
        self.label_tok = label_tok
        self.doesaux_tok = doesaux_tok
        self.verb_tok = verb_tok
        self.in_flows = in_flows
        self.prepos_tok = prepos_tok
        self.out_flows = out_flows
        self.sub_clauses: List[SubClause] = []


class Design(comment_storage.DefaultDocStore):
    """Design rule in a component.

    Arguments:
        label_tok: Name of the design rule.
        expr: Condition expressed in the design.

    Attributes:
        design_kind: Kind of the design, filled in after construction.
            Contains either 'requirement' or 'constraint'.
        sub_clauses: Sub-clauses of the design.
    """

    def __init__(self, label_tok: "Token", expr: "Expression"):
        super(Design, self).__init__(label_tok)
        self.design_kind: Optional[str] = None
        self.label_tok = label_tok
        self.expr = expr
        self.sub_clauses: List[SubClause] = []


class SubClause:
    """Subclause in a goal, transformation, or behavior.

    Arguments:
        label_tok: Name of the subclause.
        expr: Expression describing the subclause.
    """

    def __init__(self, label_tok: "Token", expr: "Expression"):
        self.label_tok = label_tok
        self.expr = expr


class BehaviorFunction(comment_storage.DefaultDocStore):
    """One function specifying some behavior.

    Arguments:
        behavior_kind: Kind of behavior. Either 'requirement' or 'constraint'.
        name_tok: Name of the behavior.

    Attributes:
        cases: Behavior cases.
        default_results: Results that hold when none of the cases applies. None means
            there is no default result.
    """

    def __init__(self, behavior_kind: str, name_tok: "Token"):
        super(BehaviorFunction, self).__init__(name_tok)
        self.behavior_kind = behavior_kind
        self.name_tok = name_tok
        self.cases: List[BehaviorCase] = []
        self.default_results: Optional[List[BehaviorResult]] = None


class BehaviorCondition:
    """A condition of a case."""

    def __init__(self, name_tok: "Token", comparison: Union["Disjunction", "RelationComparison"]):
        self.name_tok = name_tok
        self.comparison = comparison


class BehaviorResult:
    """A result of a case."""

    def __init__(self, name_tok: "Token", result: "Comparison"):
        self.name_tok = name_tok
        self.result = result


class BehaviorCase:
    """A set of desired behavioral results given a set of conditions.

    Arguments:
        name_tok: Name of the behavior case.
        conditions: Conditions that should hold for the case to apply.
        results: Results that should hold when the case applies.
    """

    def __init__(
        self,
        name_tok: "Token",
        conditions: List[BehaviorCondition],
        results: List[BehaviorResult],
    ):
        self.name_tok = name_tok
        self.conditions = conditions
        self.results = results


NeedSubjectTypes = Union[
    RelationInstance,
    VarParam,
    ComponentInstance,
    Goal,
    Transformation,
    Design,
    BehaviorFunction,
]


class Need(comment_storage.DefaultDocStore):
    """Informal need in ESL.

    Arguments:
        label_tok: Token with the name of the label.
        subject_tok: Token with the name of the subject of the need.
        description: Description of the need.

    Attributes:
        subject: If not None, subject of the need.
    """

    def __init__(self, label_tok: "Token", subject_tok: "Token", description: str):
        super(Need, self).__init__(label_tok)
        self.label_tok = label_tok
        self.subject_tok = subject_tok
        self.description = description

        self.subject: Optional[NeedSubjectTypes] = None


def get_doc_comment_comp_elements(
    comp: ComponentDefinition,
) -> Generator[comment_storage.DocStore, None, None]:
    """Retrieve the component elements interested in getting documentation comments from
    the input. This includes the component itself, so you can add documentation to it
    in its 'comments' section.

    Arguments:
        comp: Component definition to search.

    Returns:
        Generator yielding interested elements.
    """
    all_elems: List[
        Union[
            List[ComponentDefinition],
            List[VarParam],
            List[ComponentInstance],
            List[Need],
            List[Goal],
            List[Transformation],
            List[Design],
            List[RelationInstance],
            List[BehaviorFunction],
        ]
    ] = [
        [comp],
        comp.variables,
        comp.parameters,
        comp.component_instances,
        comp.needs,
        comp.goals,
        comp.transforms,
        comp.designs,
        comp.relations,
        comp.behaviors,
    ]
    for elems in all_elems:
        for elem in elems:
            if elem.doc_tok:
                yield elem
