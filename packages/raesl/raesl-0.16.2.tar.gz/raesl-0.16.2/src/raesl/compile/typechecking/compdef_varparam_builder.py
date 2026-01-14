"""Variables and components in a component definition."""
from typing import TYPE_CHECKING, Any, Dict, List

from raesl.compile import diagnostics
from raesl.compile.ast import components, nodes, types

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders, Counter


class CompDefVarParamBuilder:
    """Collect and check variables of a component definition.

    Arguments:
        comp_child_builders: Storage of child builders for a component definition.
        varparam_counter: Object for handing out unique numbers to elementary var/param
            nodes.

    Attributes:
        variables: Variables of the component.
        parameters: Parameters of the component.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders", varparam_counter: "Counter"):
        self.diag_store: diagnostics.DiagnosticStore = comp_child_builders.diag_store
        self.varparam_counter = varparam_counter
        self.comp_child_builders = comp_child_builders

        self.variables: List[components.VarParam] = []
        self.parameters: List[components.VarParam] = []

    def add_variables(self, new_vars: List[components.VarParam]):
        """Add variables of the component definition to the collection."""
        self.variables.extend(new_vars)

    def add_parameters(self, new_params: List[components.VarParam]):
        """Add parameters of the component definition to the collection."""
        self.parameters.extend(new_params)

    def finish_comp(self, comp_def: components.ComponentDefinition, spec: "Specification"):
        """Check the collected variables and parameters, report errors, and add the
        instances to the given component.

        Arguments:
            comp_def: Component definition to extend with the found variables and
                parameters.
            spec: Specification being constructed. Source for types, verbs and relation
                definitions processed previously.
        """
        varsparams_by_name: Dict[str, List[Any]]
        varsparams_by_name = self.comp_child_builders.elements_by_label
        for var in self.variables:
            name = var.name_tok.tok_text
            varsparams_by_name[name].append(var)
        for param in self.parameters:
            name = param.name_tok.tok_text
            varsparams_by_name[name].append(param)

        for name, varsparams in varsparams_by_name.items():
            # Verify properties of the variable or parameter.
            varparam = varsparams[0]
            typename = varparam.type_tok.tok_text
            vartypedef = spec.types.get(typename)
            if vartypedef is None:
                loc = varparam.name_tok.get_location()
                self.diag_store.add(diagnostics.E203("type", name=typename, location=loc))
            else:
                # Build node tree for the variable or parameter.
                varparam.node = _make_varnodes(
                    varparam.name_tok, vartypedef.type, self.varparam_counter
                )

                # And store it at the right spot in the component definition.
                if varparam.is_variable:
                    comp_def.variables.append(varparam)
                else:
                    comp_def.parameters.append(varparam)


def _make_varnodes(name_tok: "Token", the_type: types.BaseType, varparam_counter: "Counter"):
    """Make a VarNode tree that matches the shape of the type."""
    if isinstance(the_type, types.ElementaryType):
        return nodes.ElementaryVarNode(name_tok, the_type, varparam_counter)
    else:
        assert isinstance(the_type, types.Compound)
        childs = [_make_varnodes(fld.name, fld.type, varparam_counter) for fld in the_type.fields]
        return nodes.CompoundVarNode(name_tok, the_type, childs)
