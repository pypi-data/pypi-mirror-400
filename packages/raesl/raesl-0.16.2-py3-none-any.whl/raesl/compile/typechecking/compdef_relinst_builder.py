"""Relation instance type-checking in a component definition."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple, Union, cast

from raesl.compile import diagnostics
from raesl.compile.ast import relations
from raesl.compile.ast.components import InstanceArgument, RelationInstance
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.type_checker import check_type

if TYPE_CHECKING:
    from raesl.compile.ast.components import (
        ComponentDefinition,
        VariableGroup,
        VarParam,
    )
    from raesl.compile.ast.specification import Specification
    from raesl.compile.ast.types import BaseType
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class RelInstArgsBlock:
    """A 'block' of arguments of a relation instance. The kind of arguments, and a list
    of argument lines.

    Arguments:
        argkind_tok: Token indicating the kind of arguments specified in the block.
        arg_name_toks: Arguments of the block.
    """

    def __init__(self, argkind_tok: "Token", arg_name_toks: Optional[List["Token"]] = None):
        self.argkind_tok = argkind_tok

        self.arg_name_toks: List["Token"]
        if arg_name_toks is None:
            self.arg_name_toks = []
        else:
            self.arg_name_toks = arg_name_toks


class RelInst:
    """Relation instance while collecting.

    Arguments:
        inst_name_tok: Instance name.
        def_name_tok: Definition name.
        arg_blocks: Blocks with arguments.
    """

    def __init__(
        self,
        inst_name_tok: "Token",
        def_name_tok: "Token",
        arg_blocks: Optional[List[RelInstArgsBlock]] = None,
    ):
        self.inst_name_tok = inst_name_tok
        self.def_name_tok = def_name_tok

        self.arg_blocks: List[RelInstArgsBlock]
        if arg_blocks is None:
            self.arg_blocks = []
        else:
            self.arg_blocks = arg_blocks


class RelInstArgGroup:
    """Temporary data storage of parameters and arguments of a single kind."""

    def __init__(
        self,
        argkind: str,
        parameters: List[relations.RelationDefParameter],
        arguments: List["Token"],
    ):
        self.argkind = argkind
        self.parameters = parameters
        self.arguments = arguments


class CompDefRelInstBuilder:
    """Collect and check relation instances in a component definition.

    Arguments:
        comp_child_builders: Storage of child builders for a component definition.

    Attributes:
        relinsts: Collected relation instances in the component.
        last_relinst: Link to last added instance to allow adding instance arguments.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.relinsts: List[RelInst] = []
        self.comp_child_builders = comp_child_builders
        self.last_relinst: Optional[RelInst] = None

    def new_relinst(self, inst_name_tok: "Token", def_name_tok: "Token"):
        """Parser found a new relation instance, store it for future extending by
        the parser, and eventual type checking and adding to the surrounding
        component definition.
        """
        relinst = RelInst(inst_name_tok, def_name_tok)
        self.relinsts.append(relinst)
        self.last_relinst = relinst

    def relinst_argheader(self, argkind_tok: "Token"):
        """Parser found a new direction block for a relation instance, collect it."""
        assert self.last_relinst is not None

        arg_block = RelInstArgsBlock(argkind_tok)
        self.last_relinst.arg_blocks.append(arg_block)

    def add_relinst_arguments(self, name_toks: List["Token"]):
        """Parser found an argument of a direction-block in a relation instance, store
        it for future checking.
        """
        assert self.last_relinst is not None

        self.last_relinst.arg_blocks[-1].arg_name_toks.extend(name_toks)

    def finish_comp(self, comp_def: "ComponentDefinition", spec: "Specification"):
        """Check the collected relation instances, report errors, and add the
        instances to the given component.

        Arguments:
            comp_def: Component definition to extend with the found relation instances.
                Also a source of available variables, parameters, and variable groups.
            spec: Specification being constructed. Source for types and relation
                definitions processed previously.
        """
        self._add_relation_instance_names()

        # Available names of variables, parameters, and variable-groups in the
        # component.
        avail_vps = utils.construct_var_param_map(comp_def)
        avail_vgroups = utils.construct_vargroup_map(comp_def)

        reported_names: Set[str] = set()  # Names already reported to avoid reporting them again.

        # Make access to relation definitions in the specification easy.
        reldefs = dict((reldef.name.tok_text, reldef) for reldef in spec.rel_defs)

        # Check instances.
        for relinst in self.relinsts:
            # Look for a definition.
            reldef = reldefs.get(relinst.def_name_tok.tok_text)
            if reldef is None:
                # Truly undefined relation definition.
                loc = relinst.def_name_tok.get_location()
                name = relinst.def_name_tok.tok_text
                self.diag_store.add(
                    diagnostics.E203("relation definition", name=name, location=loc)
                )
                continue

            def_parameters = CompDefRelInstBuilder._split_definition_parameters_by_kind(reldef)
            instkind_groups: Optional[List[RelInstArgGroup]]
            instkind_groups = self._split_instance_arguments_by_kind(
                relinst, reldef, def_parameters
            )
            if instkind_groups is None:
                continue

            reldef_param_indices = dict((rd_param, i) for i, rd_param in enumerate(reldef.params))
            instance_arguments: List[Optional[List[InstanceArgument]]]
            instance_arguments = [None] * len(
                reldef.params
            )  # Gets filled using 'reldef_param_indices'

            found_error = False
            for group in instkind_groups:
                argkind = group.argkind
                params = group.parameters
                argument_lists = self._group_param_args(
                    argkind, params, group.arguments, relinst, reldef
                )
                if argument_lists is None:
                    found_error = True
                    continue

                # Perform type checking.
                assert len(params) == len(argument_lists)
                for param, args in zip(params, argument_lists):
                    relinst_argument = []  # list due to the 'one or more' feature.

                    # - For singular-value parameters, args is a list of length 1 and
                    #   each value in it must fit in the parameter type.
                    # - For plural-value parameters, args may be longer and
                    #   each value in it must fit in the parameter type.
                    param_input: Tuple[
                        Optional["Token"],
                        Union["BaseType", "VarParam", "VariableGroup"],
                    ]
                    assert param.type is not None
                    param_input = (param.name, param.type)
                    for arg in args:
                        # Convert token of the argument to a node.
                        node = utils.resolve_var_param_group_node(
                            arg,
                            avail_vps,
                            avail_vgroups,
                            reported_names,
                            self.diag_store,
                        )
                        if node is None:
                            found_error = True
                            continue

                        # Check type
                        arg_input = (arg, node)
                        type_problem: Optional[diagnostics.EslDiagnostic]
                        type_problem = check_type(
                            subtype=arg_input,
                            supertype=param_input,
                            allow_subtype_limits=(argkind == "requiring"),
                        )
                        if type_problem is not None:
                            self.diag_store.add(type_problem)
                            found_error = True
                            continue

                        relinst_argument.append(InstanceArgument(arg, node))

                    instance_arguments[reldef_param_indices[param]] = relinst_argument

            if not found_error:
                assert all(ia is not None for ia in instance_arguments)
                instance = RelationInstance(
                    relinst.inst_name_tok,
                    relinst.def_name_tok,
                    cast(List[List[InstanceArgument]], instance_arguments),
                    reldef,
                )
                comp_def.relations.append(instance)

    def _add_relation_instance_names(self):
        """Check whether the relation instances all have unique instance names, else
        report an error.
        """
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for relinst in self.relinsts:
            elements_by_label[relinst.inst_name_tok.tok_text].append(relinst)

    @staticmethod
    def _split_definition_parameters_by_kind(
        reldef: relations.RelationDefinition,
    ) -> Dict[str, List[relations.RelationDefParameter]]:
        """Split the parameters of the definition in 3 groups, 'requiring', 'returning',
        and 'relating'.

        Arguments:
            reldef: Relation definition to use.

        Returns:
            Mapping of the parameters in the mentioned 3 groups.
        """
        def_parameters: Dict[str, List[relations.RelationDefParameter]]
        def_parameters = {"requiring": [], "returning": [], "relating": []}
        for param in reldef.params:
            if param.direction == relations.INPUT:
                def_parameters["requiring"].append(param)
            elif param.direction == relations.OUTPUT:
                def_parameters["returning"].append(param)
            else:
                assert param.direction == relations.INPOUT
                def_parameters["relating"].append(param)

        return def_parameters

    def _split_instance_arguments_by_kind(
        self,
        relinst: RelInst,
        reldef: relations.RelationDefinition,
        def_parameters: Dict[str, List[relations.RelationDefParameter]],
    ) -> Optional[List[RelInstArgGroup]]:
        """Split the argument blocks, and check whether instance and definition agree
        with each other. Report errors if discrepancies are found, and merge argument
        blocks.

        Arguments
            relinst: Relation instance to check.
            def_parameters: Parameters of the definition grouped by argument kind.

        Returns:
            Triplets (kind, parameter-defs, argument tokens) wrapped in RelInstArgGroup
                instances, or None if a fatal error was found.
        """
        # Split argument blocks by argument kind.
        inst_blocks: Dict[str, List[RelInstArgsBlock]]
        inst_blocks = {"requiring": [], "returning": [], "relating": []}
        for arg_block in relinst.arg_blocks:
            inst_blocks[arg_block.argkind_tok.tok_text].append(arg_block)

        # Verify blocks for each kind, instance should have one block if definition has
        # one, else it should have no block.
        for argkind, arg_blocks in inst_blocks.items():
            if not def_parameters[argkind]:
                # Definition has no arguments for the kind.
                if arg_blocks:
                    rel_loc = reldef.name.get_location()
                    block_locs = [arg_block.argkind_tok.get_location() for arg_block in arg_blocks]
                    self.diag_store.add(
                        diagnostics.E206(
                            reldef.name.tok_text,
                            argkind,
                            location=rel_loc,
                            blocks=block_locs,
                        )
                    )
                continue  # Ignore any existing arguments.

            # Definition has arguments for the kind.
            if not arg_blocks:
                # But the instance has not.
                inst_loc = relinst.inst_name_tok.get_location()
                def_loc = reldef.name.get_location()
                name = relinst.inst_name_tok.tok_text
                self.diag_store.add(
                    diagnostics.E207(name, argkind, location=inst_loc, definition=def_loc)
                )
                return None  # Fatal error.

            if len(arg_blocks) > 1:
                locs = [arg_block.argkind_tok.get_location() for arg_block in arg_blocks]
                diag = diagnostics.E200(argkind, "parameter block", location=locs[0], dupes=locs)
                diag.severity = diagnostics.WARN
                self.diag_store.add(diag)
                # Not fatal, we merge the blocks below.

        groups = []
        for argkind, arg_blocks in inst_blocks.items():
            parameters = def_parameters[argkind]
            if not parameters:
                continue  # Ignore arguments if there are no parameters for them.

            arguments: List["Token"] = []
            for arg_block in arg_blocks:
                arguments.extend(arg_block.arg_name_toks)

            groups.append(RelInstArgGroup(argkind, parameters, arguments))

        return groups

    def _group_param_args(
        self,
        argkind: str,
        parameters: List[relations.RelationDefParameter],
        arguments: List["Token"],
        relinst: RelInst,
        reldef: relations.RelationDefinition,
    ) -> Optional[List[List["Token"]]]:
        """Group the arguments into pieces such that each parameter has exactly one
        piece. Mostly this means that the first multi-value parameter takes up all
        slack.

        Arguments:
            argkind: Kind of parameters, one of ('requiring', 'returning', 'relating')
            parameters: Parameters of the definition for the argkind.
            arguments: Arguments of the instance for the argkind.
            relinst: Relation instance.
            reldef: Relation definition.

        Returns:
            None if a fatal error occurred, else grouped arguments.
        """
        # Are there multi-value parameters?
        multiple_index = None
        for i, param in enumerate(parameters):
            if param.multi:
                multiple_index = i
                break

        # Verify length of both lists, and split the argument list such that
        # each parameter gets a list of values.
        params_length = len(parameters)
        args_length = len(arguments)

        if multiple_index is None:
            # All single value parameters.
            if params_length != args_length:
                # Unequal number of arguments and parameters, report an error.
                self.diag_store.add(
                    diagnostics.E221(
                        "argument",
                        args_length,
                        params_length,
                        location=relinst.inst_name_tok.get_location(),
                        references=[reldef.name.get_location()],
                    )
                )
                return None

        else:
            if args_length < params_length:
                name = relinst.inst_name_tok.tok_text
                inst_loc = relinst.inst_name_tok.get_location()
                def_loc = reldef.name.get_location()
                self.diag_store.add(
                    diagnostics.E208(
                        name,
                        argkind,
                        params_length - args_length,
                        location=inst_loc,
                        definition=def_loc,
                    )
                )
                return None

        splitted = utils.split_arguments(params_length, multiple_index, arguments)
        return splitted
