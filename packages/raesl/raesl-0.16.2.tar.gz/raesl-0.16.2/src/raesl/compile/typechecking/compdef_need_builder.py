"""Code for handling 'needs' in component definitions."""
from typing import TYPE_CHECKING, Any, Dict, List

from raesl.compile import diagnostics
from raesl.compile.ast.components import Need
from raesl.compile.ast.nodes import ElementaryVarNode
from raesl.compile.typechecking import utils
from raesl.compile.typechecking.utils import resolve_var_param_node

if TYPE_CHECKING:
    from raesl.compile.ast.components import ComponentDefinition
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CompDefNeedBuilder:
    """Class for handling 'need' sections.

    Arguments:
        comp_child_builders: Storage of child builders for a component definition.

    Attributes:
        needs: Collected needs.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.comp_child_builders = comp_child_builders

        self.needs: List[Need] = []

    def add_need(self, label_tok: "Token", subject_tok: "Token", description: str):
        """Parser found another need, store it for future processing."""
        need = Need(label_tok, subject_tok, description)
        self.needs.append(need)

    def finish_comp(self, comp_def: "ComponentDefinition", _spec: "Specification"):
        """Check the collected needs, and store them in the component definition."""
        # Verify non-duplicated need labels.
        elements_by_label: Dict[str, List[Any]] = self.comp_child_builders.elements_by_label
        for need in self.needs:
            elements_by_label[need.label_tok.tok_text].append(need)

        # Construct link to the definition of the subject mentioned in the neEd.
        # If found, add the need to the component definition, else give an error.
        vps = utils.construct_var_param_map(comp_def)
        cinsts = utils.construct_comp_instances_map(comp_def)
        rgtdbs = utils.construct_relinst_goal_transform_design_behavior_map(comp_def)

        for need in self.needs:
            cinst = cinsts.get(need.subject_tok.tok_text)
            if cinst is not None:
                need.subject = cinst
                comp_def.needs.append(need)
                continue

            rgtdb = rgtdbs.get(need.subject_tok.tok_text)
            if rgtdb is not None:
                # XXX Returned type of rgtdb looks like a subset of allowed subject
                # types. Check!
                need.subject = rgtdb
                comp_def.needs.append(need)
                continue

            varparam = resolve_var_param_node(need.subject_tok, vps, set(), self.diag_store)
            if varparam is not None:
                if isinstance(varparam, ElementaryVarNode):
                    need.subject = varparam
                    comp_def.needs.append(need)
                    continue
                else:
                    loc = need.subject_tok.get_location()
                    name = need.label_tok.tok_text
                    self.diag_store.add(diagnostics.E226(name, location=loc))
                    continue

            loc = need.subject_tok.get_location()
            name = need.subject_tok.tok_text
            context = need.label_tok.tok_text
            self.diag_store.add(
                diagnostics.E205(
                    f"subject '{name}'",
                    f"the context of need '{context}'",
                    location=loc,
                )
            )
