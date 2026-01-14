"""Variable groups in a component."""

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from raesl.compile import diagnostics
from raesl.compile.ast.components import VariableGroup
from raesl.compile.ast.nodes import GroupNode, Node
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.orderer import Orderer
from raesl.utils import get_first_namepart

if TYPE_CHECKING:
    from raesl.compile.ast.components import ComponentDefinition
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CollectedVarGroup:
    """Temporary data storage of found variable groups."""

    def __init__(self, name_tok: "Token", child_name_toks: List["Token"]):
        self.name_tok = name_tok
        self.child_name_toks = child_name_toks


class CompDefVarGroupBuilder:
    """Collect and check variable groups of a component definition.

    Arguments:
        comp_child_builders: Storage of child builders for a component definition.

    Attributes:
        collected_var_groups: Collected var group instances in the component.
        last_vgroup: Link to last added instance to allow adding instance arguments.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.collected_var_groups: List[CollectedVarGroup] = []
        self.comp_child_builders = comp_child_builders
        self.last_vgroup: Optional[CollectedVarGroup] = None

    def new_vargroup(self, name_tok: "Token"):
        """Parser found the start of a new variable group definition. Create a new group
        for it.

        Arguments:
            name_tok: Name of the new variable group.
        """
        self.last_vgroup = CollectedVarGroup(name_tok, [])
        self.collected_var_groups.append(self.last_vgroup)

    def vgroup_add_vars(self, varpart_name_toks: List["Token"]):
        """Parser found a line with variables that are part of the group. Store them for
        further processing afterwards.

        Arguments:
            varpart_name_toks: Name of variable parts that should become included in
                the last defined variable group.
        """
        assert self.last_vgroup is not None
        self.last_vgroup.child_name_toks.extend(varpart_name_toks)

    def finish_comp(self, comp_def: "ComponentDefinition", _spec: "Specification"):
        """Check the collected variable groups, report errors, and add the
        instances to the given component.

        Arguments:
            comp_def: Component definition to extend with the found variable groups.
                Also a source of available variables and parameters.
            _spec: Specification being constructed. Source for types and relation
                definitions processed previously.
        """
        self.last_vgroup = None

        avail_varsparams = utils.construct_var_param_map(comp_def)

        # Check for duplicates and conflicts with variables and parameters.
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label

        groups_by_label: Dict[str, List[CollectedVarGroup]] = defaultdict(list)

        for cgroup in self.collected_var_groups:
            elements_by_label[cgroup.name_tok.tok_text].append(cgroup)
            groups_by_label[cgroup.name_tok.tok_text].append(cgroup)
        for name, vgrps in groups_by_label.items():
            varparam = avail_varsparams.get(name)
            if varparam is not None:
                vp_loc = varparam.name_tok.get_location()
                vg_locs = [vgrp.name_tok.get_location() for vgrp in vgrps]
                kind = {True: "variable", False: "parameter"}[varparam.is_variable]
                self.diag_store.add(
                    diagnostics.E209(name, kind, "variable group", location=vp_loc, others=vg_locs)
                )

        # Build a dependency graph for the variable groups (as groups may include other
        # groups).
        orderer = Orderer()
        for cgroup in self.collected_var_groups:
            # Build a set required variables, parameters, and variable groups, using
            # non-dotted prefixes.
            needs = set(get_first_namepart(vtok.tok_text) for vtok in cgroup.child_name_toks)
            orderer.add_dependency(cgroup.name_tok.tok_text, needs, cgroup)

        reported: Set[str] = set()  # Reported failures
        vargroups: Dict[str, VariableGroup] = {}  # Resolved variable groups.

        resolved, cycle = orderer.resolve()
        for entry in resolved:
            cgroup = entry.data
            if cgroup is None:
                # Need entry added by the orderer, ignore.
                continue

            # Next collected group to deal with.
            #
            # Each of its variablepart_names either contains non-dotted previous
            # variable groups, or possibly dotted variables or parameters.
            content_vgroup: List[Node] = []  # Result content for the future variable group.
            for partname_tok in cgroup.child_name_toks:
                node = utils.resolve_var_param_group_node(
                    partname_tok,
                    avail_varsparams,
                    vargroups,
                    reported,
                    self.diag_store,
                )
                if node is not None:
                    content_vgroup.append(node)
                # Else, error already reported, ignore it.

            # Even with errors a variable group is constructed to avoid follow-up
            # errors on non-existing groups.
            vgroup = VariableGroup(cgroup.name_tok, cgroup.child_name_toks)
            vgroup.node = GroupNode(cgroup.name_tok, content_vgroup)
            vargroups[cgroup.name_tok.tok_text] = vgroup
            comp_def.var_groups.append(vgroup)

        if cycle:
            locs = [entry.data.name_tok.get_location() for entry in cycle]
            name = cycle[0].data.name_tok.tok_text
            self.diag_store.add(
                diagnostics.E204(name, "variable group", location=locs[0], cycle=locs)
            )
