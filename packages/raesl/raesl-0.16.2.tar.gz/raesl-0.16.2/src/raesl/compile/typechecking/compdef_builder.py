"""Builder for collecting and building component definitions."""
import collections
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Union

from raesl.compile import diagnostics
from raesl.compile.ast import components
from raesl.compile.typechecking.compdef_behavior_builder import (
    CompDefBehaviorBuilder,
    ParsedBehavior,
)
from raesl.compile.typechecking.compdef_comment_builder import CompDefCommentBuilder
from raesl.compile.typechecking.compdef_compinst_builder import (
    CompDefCompInstBuilder,
    ComponentInstance,
)
from raesl.compile.typechecking.compdef_design_builder import CompDefDesignBuilder
from raesl.compile.typechecking.compdef_goal_builder import CompDefGoalBuilder
from raesl.compile.typechecking.compdef_need_builder import CompDefNeedBuilder
from raesl.compile.typechecking.compdef_relinst_builder import (
    CompDefRelInstBuilder,
    RelInst,
)
from raesl.compile.typechecking.compdef_transform_builder import CompDefTransformBuilder
from raesl.compile.typechecking.compdef_vargroup_builder import (
    CollectedVarGroup,
    CompDefVarGroupBuilder,
)
from raesl.compile.typechecking.compdef_varparam_builder import CompDefVarParamBuilder
from raesl.compile.typechecking.orderer import Orderer

if TYPE_CHECKING:
    from raesl.compile.ast import exprs
    from raesl.compile.ast.comment_storage import DocCommentDistributor
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder


class Counter:
    """Class for handing out unique numeric values.

    Normally, a static class variable would do, except testing more than one
    specification at a time doesn't reset the counter, leading to different output
    depending on what is being tested together.

    Arguments:
        first_free_value: First free value to set the counter to.

    Attributes:
        counter: Next free value.
    """

    def __init__(self, first_free_value: int):
        self.counter = first_free_value

    def next(self) -> int:
        """Get a unique number from the counter instance."""
        value = self.counter
        self.counter = self.counter + 1
        return value


class CompDefChildBuilders:
    """Class storing child builders for all sections of a component definition.

    As type checking cannot be done until the entire specification has been parsed
    (global types, verbs, and relation definitions may not exist at the time of the end
    of a component definition, and definitions of instantiated component may be defined
    further down in the specification), child builders for each definition must be kept
    around until the end.

    Arguments:
        compdef_builder: Parent component definition builder.
        pos_tok: Position of the start of the component definition.
        name_tok: Name of the component definition if it exists
        varparam_counter: Object for handing out unique numbers to elementary var/param
            nodes.
    """

    def __init__(
        self,
        compdef_builder: "ComponentDefBuilder",
        pos_tok: "Token",
        name_tok: Optional["Token"],
        varparam_counter: Counter,
    ):
        self.diag_store: diagnostics.DiagnosticStore = compdef_builder.diag_store

        self.pos_tok = pos_tok
        self.name_tok = name_tok
        self.elements_by_label = collections.defaultdict(list)

        # Builders for specific parts of the component.
        self.varparam_builder = CompDefVarParamBuilder(self, varparam_counter)
        self.vargroup_builder = CompDefVarGroupBuilder(self)
        self.compinst_builder = CompDefCompInstBuilder(self)
        self.relinst_builder = CompDefRelInstBuilder(self)
        self.goal_builder = CompDefGoalBuilder(self)
        self.transform_builder = CompDefTransformBuilder(self)
        self.behavior_builder = CompDefBehaviorBuilder(self)
        self.design_builder = CompDefDesignBuilder(self)
        self.need_builder = CompDefNeedBuilder(self)
        self.comment_builder = CompDefCommentBuilder(self)

    def add_variables(self, new_vars: List[components.VarParam]):
        """Forward call to variable & parameter builder."""
        self.varparam_builder.add_variables(new_vars)

    def add_parameters(self, new_params: List[components.VarParam]):
        """Forward call to variable & parameter builder."""
        self.varparam_builder.add_parameters(new_params)

    def new_vargroup(self, name_tok: "Token"):
        """Forward call to variable group builder."""
        self.vargroup_builder.new_vargroup(name_tok)

    def vgroup_add_vars(self, varname_toks: List["Token"]):
        """Forward call to variable group builder."""
        self.vargroup_builder.vgroup_add_vars(varname_toks)

    def add_compinst(self, inst_name_tok: "Token", def_name_tok: "Token", has_arguments: bool):
        """Forward call to component instance builder."""
        self.compinst_builder.add_compinst(inst_name_tok, def_name_tok, has_arguments)

    def add_compinst_arguments(self, arguments: List["Token"]):
        """Forward call to component instance builder."""
        self.compinst_builder.add_compinst_arguments(arguments)

    def new_relinst(self, inst_name_tok: "Token", def_name_tok: "Token"):
        """Forward call to relation instance builder."""
        self.relinst_builder.new_relinst(inst_name_tok, def_name_tok)

    def relinst_argheader(self, argkind_tok: "Token"):
        """Forward call to relation instance builder."""
        self.relinst_builder.relinst_argheader(argkind_tok)

    def add_relinst_arguments(self, name_toks: List["Token"]):
        """Forward call to relation instance builder."""
        self.relinst_builder.add_relinst_arguments(name_toks)

    def new_goal_header(self, goal_kind: "Token"):
        """Forward call to goal builder."""
        self.goal_builder.new_goal_header(goal_kind)

    def add_goal(self, goal: components.Goal):
        """Forward call to goal builder."""
        self.goal_builder.add_goal(goal)

    def add_goal_subclause(self, sub_clause: components.SubClause):
        """Forward call to goal builder."""
        self.goal_builder.add_goal_subclause(sub_clause)

    def new_transform_header(self, transform_kind: "Token"):
        """Forward call to transform builder."""
        self.transform_builder.new_transform_header(transform_kind)

    def add_transform(self, transform: components.Transformation):
        """Forward call to transform builder."""
        self.transform_builder.add_transform(transform)

    def add_transform_subclause(self, sub_clause: components.SubClause):
        """Forward call to transform builder."""
        self.transform_builder.add_transform_subclause(sub_clause)

    def new_behavior_header(self, kind_tok: "Token"):
        """Forward call to behavior builder."""
        self.behavior_builder.new_behavior_header(kind_tok)

    def new_behavior_function(self, label_tok: "Token"):
        """Forward call to behavior builder."""
        self.behavior_builder.new_behavior_function(label_tok)

    def behavior_case(self, case_label_tok: "Token"):
        """Forward call to behavior builder."""
        self.behavior_builder.behavior_case(case_label_tok)

    def behavior_normal_when(self, when_tok: "Token"):
        """Forward call to behavior builder."""
        self.behavior_builder.behavior_normal_when(when_tok)

    def behavior_default_when(self, when_tok: "Token"):
        """Forward call to behavior builder."""
        self.behavior_builder.behavior_default_when(when_tok)

    def behavior_when_condition(
        self,
        name_tok: "Token",
        condition: Union["exprs.Disjunction", "exprs.RelationComparison"],
    ):
        """Forward call to behavior builder."""
        self.behavior_builder.behavior_when_condition(name_tok, condition)

    def behavior_normal_then(self, then_tok: "Token"):
        """Forward call to behavior builder."""
        self.behavior_builder.behavior_normal_then(then_tok)

    def behavior_then_result(self, name_tok: "Token", result: "exprs.Comparison"):
        """Forward call to behavior builder."""
        self.behavior_builder.behavior_then_result(name_tok, result)

    def new_design_header(self, kind: "Token"):
        """Forward call to design builder."""
        self.design_builder.new_design_header(kind)

    def design_line(self, design: components.Design):
        """Forward call to design builder."""
        self.design_builder.design_line(design)

    def add_design_subclause(self, sub: components.SubClause):
        """Forward call to design builder."""
        self.design_builder.add_design_subclause(sub)

    def add_need(self, label_tok: "Token", subject_tok: "Token", description: str):
        """Forward call to need builder."""
        self.need_builder.add_need(label_tok, subject_tok, description)

    def add_comment(self, name_tok: "Token"):
        """Forward call to comment builder."""
        self.comment_builder.add_comment(name_tok)

    def get_child_compdefnames(self) -> Set[str]:
        """Get the names of component definitions that are needed for child instances.

        Returns:
            Names of the components being instantiated in this component.
        """
        return self.compinst_builder.get_compdef_names()

    def finish(self, spec: "Specification", doc_distributor: "DocCommentDistributor"):
        """Parsing is finished, component child instances have been checked already.
        Check the collected component data, and add the component definition to the
        specification.

        Arguments:
            spec: Specification to use as source for types, verbs relation definitions,
                and other component definitions, and to fill with the type-checked
                component.
            doc_distributor: Object that accepts the found doc comments for distributing
                them to the elements of the specification.
        """
        comp_def = components.ComponentDefinition(self.pos_tok, self.name_tok)
        self.varparam_builder.finish_comp(comp_def, spec)
        self.vargroup_builder.finish_comp(comp_def, spec)
        self.compinst_builder.finish_comp(comp_def, spec)
        self.relinst_builder.finish_comp(comp_def, spec)
        self.goal_builder.finish_comp(comp_def, spec)
        self.transform_builder.finish_comp(comp_def, spec)
        self.behavior_builder.finish_comp(comp_def, spec)
        self.design_builder.finish_comp(comp_def, spec)
        self.need_builder.finish_comp(comp_def, spec)
        self.comment_builder.finish_comp(comp_def, doc_distributor)  # Must be final build step.

        # Check for unique labels within the scope of each comp_def.
        for labeled_elements in self.elements_by_label.values():
            if len(labeled_elements) > 1:
                locs = []
                for elem in labeled_elements:
                    if isinstance(elem, (components.VarParam, CollectedVarGroup)):
                        locs.append(elem.name_tok.get_location())
                    elif isinstance(elem, ParsedBehavior):
                        locs.append(elem.name.get_location())
                    elif isinstance(elem, (RelInst, ComponentInstance)):
                        locs.append(elem.inst_name_tok.get_location())
                    else:
                        locs.append(elem.label_tok.get_location())

                if self.name_tok:
                    scope = "component definition {}".format(self.name_tok.tok_text)
                else:
                    scope = "world"

                if hasattr(labeled_elements[-1], "label_tok"):
                    name = labeled_elements[-1].label_tok.tok_text
                elif hasattr(labeled_elements[-1], "name_tok"):
                    name = labeled_elements[-1].name_tok.tok_text
                elif hasattr(labeled_elements[-1], "name"):
                    name = labeled_elements[-1].name.tok_text
                elif hasattr(labeled_elements[-1], "inst_name_tok"):
                    name = labeled_elements[-1].inst_name_tok.tok_text
                else:
                    name = ""

                self.diag_store.add(
                    diagnostics.E227(
                        name,
                        scope,
                        location=locs[0],
                        dupes=locs,
                    )
                )

        # Add all elements of the component to the documentation distributor.
        for elem in components.get_doc_comment_comp_elements(comp_def):
            doc_distributor.add_element(elem)

        if comp_def.name_tok is None:
            spec.world = comp_def
        else:
            spec.comp_defs.append(comp_def)

    def notify_parameter_section(self, pos_tok: "Token"):
        """A parameter section was found, check if it is allowed."""
        if self.name_tok is None:  # We're processing 'world'
            # Parameter section not allowed in 'world'.
            self.diag_store.add(diagnostics.E201("parameter", "world", pos_tok.get_location()))

    def notify_transform_section(self, pos_tok: "Token"):
        """A transform section was found, check if it is allowed."""
        if self.name_tok is None:  # We're processing 'world'
            # Transformation section not allowed in 'world'.
            self.diag_store.add(diagnostics.E201("transformation", "world", pos_tok.get_location()))


class ComponentDefBuilder:
    """Builder to construct component definitions of the entire specification. The
    builder keeps a list of component child builders, one for each component definition.
    The latter do all the work for each component definition.
    """

    def __init__(self, ast_builder: "AstBuilder"):
        self.diag_store: diagnostics.DiagnosticStore = ast_builder.diag_store
        self.varparam_counter = Counter(100)

        ast_builder.register_new_section(self)
        self.child_builders: List[CompDefChildBuilders] = []
        self.current_component: Optional[CompDefChildBuilders] = None

    def notify_new_section(self, new_top_section):
        """Notification for self and possibly the child builders if a new component
        definition is under construction.
        """
        if new_top_section:
            self.current_component = None

    def new_componentdef(self, pos_tok: "Token", name_tok: Optional["Token"]):
        """New component definition started.

        Arguments:
            pos_tok: Token defining the start position of the component definition.
            name_tok: Token with the name of the definition if it exists.
                Non-existing name means the component represents 'world'.
        """
        self.current_component = CompDefChildBuilders(
            self, pos_tok, name_tok, self.varparam_counter
        )
        self.child_builders.append(self.current_component)

    def finish(self, spec: "Specification", doc_distributor: "DocCommentDistributor"):
        """Parsing has finished, complete type checking.

        Arguments:
            spec: Specification already containing types, verb-prepositions, and
                relation definitions. Must be filled with component definitions and
                world component.
            doc_distributor: Object that accepts the found doc comments for distributing
                them to the elements of the specification.
        """
        # Verify that component definitions are sufficiently unique.
        compdefs: Dict[str, List[CompDefChildBuilders]] = collections.defaultdict(list)
        worlds = []
        for ch_builder in self.child_builders:
            if ch_builder.name_tok is None:
                worlds.append(ch_builder)
            else:
                name = ch_builder.name_tok.tok_text
                compdefs[name].append(ch_builder)

        if len(worlds) == 0:
            self.diag_store.add(diagnostics.E202("world definition"))
        elif len(worlds) > 1:
            locs = [world.pos_tok.get_location() for world in worlds]
            self.diag_store.add(
                diagnostics.E200("world", "component instance", location=locs[0], dupes=locs)
            )

        for cdefs in compdefs.values():
            if len(cdefs) > 1:
                # Duplicate component definitions.
                locs = [cdef.pos_tok.get_location() for cdef in cdefs]
                assert cdefs[0].name_tok is not None
                name = cdefs[0].name_tok.tok_text
                self.diag_store.add(
                    diagnostics.E200(name, "component definition", location=locs[0], dupes=locs)
                )

        # Components to use.
        comp_builders = [cdef[0] for cdef in compdefs.values()]
        if len(worlds) > 0:
            comp_builders.append(worlds[0])

        # Order component definitions such that they are defined before they are used as
        # child component instances.
        orderer = Orderer()
        for comp_builder in comp_builders:
            child_defnames = comp_builder.get_child_compdefnames()
            if comp_builder.name_tok:
                compdef_name = comp_builder.name_tok.tok_text
            else:
                compdef_name = "world"  # Name cannot exist otherwise.

            orderer.add_dependency(compdef_name, child_defnames, comp_builder)

        resolveds, cycle = orderer.resolve()
        for entry in resolveds:
            if entry.data is None:
                # Entry was created by the orderer, we should run into it again and fail
                # to find it. Note that a component definition is always added to the
                # spec even if it contains errors. Therefore, presence of a component
                # definition in spec means it was present in the ESL text.
                continue

            entry.data.finish(spec, doc_distributor)

        if cycle:
            assert entry.data is not None
            locs = [entry.data.pos_tok.get_location() for entry in cycle]
            assert cycle[0].data is not None
            comp_name = cycle[0].data.name_tok.tok_text  # Cannot be world!
            self.diag_store.add(
                diagnostics.E204(comp_name, "component definition", location=locs[0], cycle=locs)
            )
