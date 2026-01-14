"""Builder to add child component instances to a component definition."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

from raesl.compile import diagnostics
from raesl.compile.ast.components import ComponentInstance, InstanceArgument
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.type_checker import check_type

if TYPE_CHECKING:
    from raesl.compile.ast.components import ComponentDefinition
    from raesl.compile.ast.nodes import Node
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CompDefCompInstBuilder:
    """Collect and check child component instances of a component definition.

    Arguments:
        comp_child_builders: Storage of child builder for a component definition.

    Attributes:
        diag_store: Child builders problem store.
        instances: Collected component instances.
        last_instance: Link to last added instance, to allow adding instance
            arguments to it.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.instances: List[ComponentInstance] = []
        self.comp_child_builders = comp_child_builders
        self.last_instance: Optional[ComponentInstance] = None

    def add_compinst(self, inst_name_tok: "Token", def_name_tok: "Token", has_arguments: bool):
        """Store a new child component instance line."""
        compinst = ComponentInstance(inst_name_tok, def_name_tok)
        self.instances.append(compinst)
        if has_arguments:
            self.last_instance = compinst
        else:
            self.last_instance = None

    def add_compinst_arguments(self, arguments: List["Token"]):
        """Store a line of component instance argument names."""
        assert self.last_instance is not None
        for argname in arguments:
            self.last_instance.arguments.append(InstanceArgument(argname))

    def get_compdef_names(self) -> Set[str]:
        """Get the names of used definitions."""
        def_names = set()
        for inst in self.instances:
            name = inst.def_name_tok.tok_text
            def_names.add(name)

        return def_names

    def finish_comp(self, comp_def: "ComponentDefinition", spec: "Specification"):
        """Finish checking and adding child component instances to the component.

        Arguments:
            comp_def: Used as 'my' component definition.
            spec: Used as source for types.
        """
        # Available names of variables, parameters, and variable-groups in 'my'
        # component.
        avail_vps = utils.construct_var_param_map(comp_def)
        avail_vgroups = utils.construct_vargroup_map(comp_def)

        # The 'other' component definition needed for checking the instance  is
        # already available, as ComponentDefBuilder ordered compdef checking on
        # instance use.
        avail_compdefs = dict(
            (cdef.name_tok.tok_text, cdef) for cdef in spec.comp_defs if cdef.name_tok is not None
        )

        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for inst in self.instances:
            elements_by_label[inst.inst_name_tok.tok_text].append(inst)

        # Collection reported names to avoid double problem reports.
        reported_names: Set[str] = set()

        # Check 'my' instances.
        for inst in self.instances:
            compdef = avail_compdefs.get(inst.def_name_tok.tok_text)
            if compdef is None:
                # Truly undefined 'other' component definition.
                name = inst.def_name_tok.tok_text
                loc = inst.def_name_tok.get_location()
                self.diag_store.add(
                    diagnostics.E203("component definition", name=name, location=loc)
                )
                continue  # Cannot do anything else useful with it.

            # Link 'other' component definition to the instance for future use.
            inst.compdef = compdef

            # Found a component definition with the same name, do arguments match as
            # well?
            #
            # 1. Collect argument information of the instance.
            found_error = False
            inst_arguments: List[Optional[Tuple["Token", "Node"]]] = []
            for arg in inst.arguments:
                node: Optional["Node"]
                node = utils.resolve_var_param_group_node(
                    arg.name_tok,
                    avail_vps,
                    avail_vgroups,
                    reported_names,
                    self.diag_store,
                )

                if node is None:
                    # resolve_var_param_group_node() already created an error.

                    inst_arguments.append(None)  # Add dummy to check other arguments.
                    found_error = True
                else:
                    inst_arguments.append((arg.name_tok, node))
                    arg.argnode = node

            # Convert parameters of the definition to InputType as well.
            parameters = [(param.name_tok, param.node) for param in compdef.parameters]

            # 2. Check number of parameters against number of arguments.
            inst_length = len(inst_arguments)
            def_length = len(parameters)
            if inst_length != def_length:
                self.diag_store.add(
                    diagnostics.E221(
                        "argument",
                        inst_length,
                        def_length,
                        location=inst.inst_name_tok.get_location(),
                        references=[compdef.pos_tok.get_location()],
                    )
                )
                found_error = True
                continue

            # 3. Check argument types against parameter types of compdef, skipping None
            #    arguments. We assume undirected flow direction, thus arguments must
            #    accept all possible values that the definition may provide.
            for param_input, arg_input in zip(parameters, inst_arguments):
                if arg_input is None:
                    continue  # Already reported as an error.

                diag = check_type(
                    subtype=arg_input, supertype=param_input, allow_subtype_limits=False
                )
                if diag:
                    self.diag_store.add(diag)
                    found_error = True

            # Add inst to compdef if no errors.
            if not found_error:
                comp_def.component_instances.append(inst)
