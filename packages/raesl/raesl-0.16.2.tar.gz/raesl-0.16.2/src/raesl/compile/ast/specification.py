"""Overall output specification."""
from typing import TYPE_CHECKING, Dict, Generator, List, Optional, TextIO

import click

from raesl.compile.ast import components, exprs, types
from raesl.compile.ast.comment_storage import DefaultDocStore, DocElement, DocStore
from raesl.compile.ast.exprs import Value, VariableValue
from raesl.compile.ast.nodes import CompoundVarNode, ElementaryVarNode, GroupNode, Node

if TYPE_CHECKING:
    from raesl.compile.ast.exprs import Expression
    from raesl.compile.ast.relations import RelationDefinition
    from raesl.compile.ast.verbs import VerbPreposDef


class Specification:
    """Main class.

    Attributes:
        types: Types of the specification.
        verb_prepos: Verbs and pre-positions.
        rel_defs: Relation definitions.
        comp_defs: Component definitions.
        world: Root component.
    """

    def __init__(self):
        self.types: Dict[str, types.TypeDef] = {}
        self.verb_prepos: List["VerbPreposDef"] = []
        self.rel_defs: List["RelationDefinition"] = []

        self.comp_defs: List[components.ComponentDefinition] = []
        self.world: Optional[components.ComponentDefinition] = None


class _DumpSpec:
    """Class for dumping the specification to an output stream."""

    def __init__(self, output_stream: Optional[TextIO] = None):
        self.stream = click.get_text_stream("stdout") if output_stream is None else output_stream
        self.done_types: Dict[types.BaseType, int] = {}

    def dump(self, spec: Specification):
        """Write the specification symbolically onto the output stream. Intended use is
        verifying content or debugging.
        """
        self.stream.write("\nTYPES:\n")
        if spec.types:
            text_tdefs = [(tdef.name, self._dump_type(tdef.type)) for tdef in spec.types.values()]
            self.stream.write("\n")
            for name, tname in text_tdefs:
                self.stream.write("typedef {}: {}\n".format(name.tok_text, tname))

        self.stream.write("\nVERBS:\n")
        for verbdef in spec.verb_prepos:
            self.stream.write("    {}\n".format(verbdef))
            self._dump_docs(verbdef, "    ")

        self.stream.write("\nRELATION-DEFINITIONS:\n")
        for rel_def in spec.rel_defs:
            self.stream.write("    def {}:\n".format(rel_def.name.tok_text))
            self._dump_docs(rel_def, "    ")
            for param in rel_def.params:
                tnumber = self.done_types[param.type]
                param_type = "type#{}".format(tnumber)
                text = "{} {}: {}".format(param.direction, param.name.tok_text, param_type)
                if param.multi:
                    text = "multi " + text

                self.stream.write("        {}\n".format(text))

        self.stream.write("\nCOMPONENTS:\n")
        if spec.world is not None:
            self.dump_component(spec.world)

        sorted_comp_defs = sorted(spec.comp_defs, key=lambda cd: cd.name_tok.tok_text)
        for comp_def in sorted_comp_defs:
            self.dump_component(comp_def)

    def dump_component(self, compdef):
        """Dump content of the provided component."""
        # Dump component name as header.
        if compdef.name_tok is None:
            self.stream.write("    world:\n")
        else:
            name = compdef.name_tok.tok_text
            self.stream.write("    def component {}:\n".format(name))
        self._dump_docs(compdef, "    ")

        # Dump variables of a component definition.
        leading = "        "
        for vdef in compdef.variables:
            self.stream.write("{}var {}\n{}  ".format(leading, vdef.name_tok.tok_text, leading))
            self._dump_nodes(vdef.node, prefixes=[leading + "  "])

        # Dump parameters of a component definition.
        for pdef in compdef.parameters:
            prop_text = {False: "", True: ": property"}[pdef.is_property]
            text = "param {}{}".format(pdef.name_tok.tok_text, prop_text)
            self.stream.write(leading + text + "\n  " + leading)
            self._dump_nodes(pdef.node, prefixes=[leading + "  "])

        # Dump variable groups of a component definition.
        for vgroup in compdef.var_groups:
            content = ", ".join(varpart.tok_text for varpart in vgroup.variablepart_names)
            text = "vgroup {}: {}".format(vgroup.name_tok.tok_text, content)
            self.stream.write(leading + text + "\n  " + leading)
            self._dump_nodes(vgroup.node, prefixes=[leading + "  "])

        # Dump component instances of a component definition.
        for compinst in compdef.component_instances:
            def_name = compinst.compdef.name_tok.tok_text
            text = "child-component {}: def={}".format(compinst.inst_name_tok.tok_text, def_name)
            self.stream.write("        " + text + "\n")
            self._dump_docs(compinst, "        ")
            self._dump_compinst_params(compinst)

        # Dump relation instances of a component definition.
        for relinst in compdef.relations:
            def_name = relinst.reldef.name.tok_text
            text = "relation-instance {}: def={}".format(relinst.inst_name_tok.tok_text, def_name)
            self.stream.write("        " + text + "\n")
            self._dump_docs(relinst, "        ")
            self._dump_relinst_params(relinst)

        # Dump goals
        leading = "        "
        for goal in compdef.goals:
            name = "{} goal {}:".format(goal.goal_kind, goal.label_tok.tok_text)
            comptext1 = "comp '{}' {} ({} {}) comp '{}'"
            comptext1 = comptext1.format(
                goal.active_comp.inst_name_tok.tok_text,
                goal.doesaux.tok_text,
                goal.verb.tok_text,
                goal.prepos.tok_text,
                goal.passive_comp.inst_name_tok.tok_text,
            )
            self.stream.write(leading + name + "\n")
            self._dump_docs(goal, leading)
            indent = leading + "    "
            self.stream.write(indent + comptext1 + "\n")
            for f in goal.flows:
                self.stream.write(indent + "flow '{}':\n".format(f.name_tok.tok_text))
                self.stream.write(indent + "  ")
                self._dump_nodes(f.flow_node, prefixes=[indent + "  "])

            self._dump_subclauses(goal.sub_clauses)

        # Dump transformations
        for trans in compdef.transforms:
            name = "{} transform {}:".format(trans.transform_kind, trans.label_tok.tok_text)
            comptext = "  {} ({} {})"
            comptext = comptext.format(
                trans.doesaux_tok.tok_text,
                trans.verb_tok.tok_text,
                trans.prepos_tok.tok_text,
            )

            indent = "        "
            self.stream.write(indent + name + "\n")
            self._dump_docs(trans, indent)
            self.stream.write(indent + comptext + "\n")
            for f in trans.in_flows:
                self.stream.write(indent + "  in-flow '{}':\n".format(f.name_tok.tok_text))
                self.stream.write(indent + "  ")
                self._dump_nodes(f.flow_node, prefixes=[indent + "  "])
            for f in trans.out_flows:
                self.stream.write(indent + "  out-flow '{}':\n".format(f.name_tok.tok_text))
                self.stream.write(indent + "  ")
                self._dump_nodes(f.flow_node, prefixes=[indent + "  "])
            self._dump_subclauses(trans.sub_clauses)

        # Dump needs
        for need in compdef.needs:
            if need.subject is None:
                subjdef_text = " UNDEFINED"
            else:
                subjdef_text = ""
            text = "need {}: subject {}{}".format(
                need.label_tok.tok_text, need.subject_tok.tok_text, subjdef_text
            )
            self.stream.write("        " + text + "\n")
            self._dump_docs(need, "        ")

        # Dump designs
        indent = "        "
        for design in compdef.designs:
            name = "{} design {}".format(design.design_kind, design.label_tok.tok_text)
            self.stream.write(indent + name + "\n")
            self._dump_docs(design, indent)
            self._dump_expr(design.expr, indent + "    ")
            self._dump_subclauses(design.sub_clauses)

        # Dump behavior
        for behavior in compdef.behaviors:
            name = "{} behavior {}:".format(behavior.behavior_kind, behavior.name_tok.tok_text)
            self.stream.write("        " + name + "\n")
            self._dump_docs(behavior, "        ")
            for case in behavior.cases:
                self.stream.write("            case " + case.name_tok.tok_text + ":\n")
                self._dump_conds(case.conditions)
                self._dump_results(case.results)
            if behavior.default_results is None:
                self.stream.write("            no default case.\n")
            else:
                self.stream.write("            default:\n")
                self._dump_results(behavior.default_results)

    def _dump_expr(self, expr: "Expression", indent: str):
        first = True
        for ex in unfold_disjunction(expr):
            if first:
                self.stream.write(indent)
                first = False
            else:
                self.stream.write("{}or ".format(indent))

            if isinstance(ex, exprs.RelationComparison):
                # Construct text and node for RHS
                rv = ex.rhs_varval
                if isinstance(rv, Value):
                    rhs_text = "{}[{}]".format(rv.value.tok_text, next(iter(rv.get_units())))
                    rhs_node = None
                else:
                    assert isinstance(rv, VariableValue)
                    rhs_text = rv.var_tok.tok_text
                    rhs_node = rv.var_node

                text = "{} {} {} {}".format(
                    ex.lhs_var.var_tok.tok_text,
                    ex.isaux_tok.tok_text,
                    ex.math_compare,
                    rhs_text,
                )
                self.stream.write(text + "\n")
                self.stream.write(indent)
                self._dump_nodes(ex.lhs_var.var_node, prefixes=[indent])
                if rhs_node is not None:
                    self.stream.write(indent)
                    self._dump_nodes(rhs_node, prefixes=[indent])

            else:
                assert isinstance(ex, exprs.ObjectiveComparison)

                aims = []
                if ex.maximize:
                    aims.append("max")
                if ex.minimize:
                    aims.append("min")
                if not aims:
                    aims.append("UNKNOWN")
                text = "{} {} {}".format(
                    "+".join(aims), ex.aux_tok.tok_text, ex.lhs_var.var_tok.tok_text
                )
                self.stream.write(text + "\n")
                self.stream.write(indent)
                self._dump_nodes(ex.lhs_var.var_node, prefixes=[indent])

    def _dump_nodes(self, node: Node, prefixes: List[str] = None):
        """Recursively dump the tree of var/param nodes rooted at 'node', with
        'prefixes' containing the leading text-fields if not None.
        """
        if prefixes is None:
            prefixes = []

        if isinstance(node, ElementaryVarNode):
            tnumber = self.done_types[node.the_type]
            self.stream.write("- type#{}\n".format(tnumber))
            self._dump_docs(node, "".join(prefixes))
        elif isinstance(node, CompoundVarNode):
            last_index = len(node.child_nodes) - 1
            prefixes.append(None)
            for index, subnode in enumerate(node.child_nodes):
                name = subnode.name_tok.tok_text
                if index > 0:
                    self.stream.write("".join(prefixes[:-1]))

                self.stream.write("\\- " + name + " ")
                if index < last_index:
                    prefixes[-1] = "|" + " " * (3 + len(name))
                else:
                    prefixes[-1] = " " + " " * (3 + len(name))

                self._dump_nodes(subnode, prefixes)
                index = index + 1

            del prefixes[-1]
        elif isinstance(node, GroupNode):
            last_index = len(node.child_nodes) - 1
            prefixes.append(None)
            for index, subnode in enumerate(node.child_nodes):
                name = subnode.name_tok.tok_text
                if index > 0:
                    self.stream.write("".join(prefixes[:-1]))

                self.stream.write("@--")
                if index < last_index:
                    prefixes[-1] = "|  "
                else:
                    prefixes[-1] = "   "

                self._dump_nodes(subnode, prefixes)
                index = index + 1

            del prefixes[-1]

    def _dump_docs(self, element: DocElement, indent_text: str):
        """Dump documentation of the given element if it has any. If no documentation
        has been added, report there is no documentation.

        Arguments:
            element: Element to check for documentation.
            indent_text: Leading text printed at each line by the function.
        """
        comments = element.get_comment()
        if not comments:
            self.stream.write(indent_text + "  #< No doc-comments found.\n")
            return

        comment_text = " ".join(comments)
        self.stream.write(indent_text + "  #< {}\n".format(comment_text))

    def _dump_type(self, btp: types.BaseType) -> str:
        """Dump unique types onto the self.output_stream while assigning them names
        of the form 'type#<num>'. Each type is output once.

        Arugments:
            btp: Type to dump.

        Returns:
            Name of the type during the dump process.
        """
        if btp in self.done_types:
            return "type#{}".format(self.done_types[btp])

        number = len(self.done_types) + 1
        self.done_types[btp] = number
        my_typename = "type#" + str(number)

        if isinstance(btp, types.Compound):
            indent = "    "

            type_names = [self._dump_type(field.type) for field in btp.fields]
            self.stream.write("{} = bundle\n".format(my_typename))
            for field, tname in zip(btp.fields, type_names):
                self.stream.write(indent + "{}: {}\n".format(field.name.tok_text, tname))
            self.stream.write("{} end\n".format(my_typename))
            self.stream.write("\n")

        else:
            assert isinstance(btp, types.ElementaryType)
            if btp.parent is not None:
                parent_name = self._dump_type(btp.parent)
                self.stream.write("{} = type <-- {}\n".format(my_typename, parent_name))
            else:
                self.stream.write("{} = type\n".format(my_typename))

            if btp.units:
                self.stream.write("    units: " + ", ".join(u.tok_text for u in btp.units) + "\n")

            if btp.intervals:
                prefix = "    intervals: "
                for ival in btp.intervals:
                    if ival[0] is None:
                        lbound = "*"
                    else:
                        lbound = str(ival[0])
                    if ival[1] is None:
                        ubound = "*"
                    else:
                        ubound = str(ival[1])

                    self.stream.write(prefix + "(=> {}, <= {})\n".format(lbound, ubound))
                    prefix = " " * len(prefix)

        return my_typename

    def _dump_compinst_params(self, compinst):
        """Dump the arguments of the component instance."""
        if not compinst.arguments:
            self.stream.write("            No instance argument!\n")
            return

        for arg, param in zip(compinst.arguments, compinst.compdef.parameters):
            arg_text = "arg {}".format(arg.name_tok.tok_text)
            param_text = "param {}".format(param.name_tok.tok_text)
            leading = "            "
            self.stream.write("{}{} <-> {}\n".format(leading, arg_text, param_text))
            self.stream.write(leading + "  ")
            self._dump_nodes(arg.argnode, prefixes=[leading + "  "])

    def _dump_relinst_params(self, relinst):
        """Dump the arguments of the relation instance."""
        if not relinst.arguments:
            self.stream.write("            No instance argument!\n")
            return

        for args, param in zip(relinst.arguments, relinst.reldef.params):
            arg_text = [arg.name_tok.tok_text for arg in args]
            param_text = "param('{}', {}, multi={})".format(
                param.name.tok_text, param.direction, param.multi
            )
            leading = "            "
            self.stream.write("{}{} <-> {}\n".format(leading, arg_text, param_text))
            for arg in args:
                self.stream.write(leading + "  ")
                self._dump_nodes(arg.argnode, prefixes=[leading + "  "])

    def _dump_subclauses(self, clauses):
        leading = "            "
        for clause in clauses:
            text = "subclause {}:\n".format(clause.label_tok.tok_text)
            self.stream.write(leading + text)
            self._dump_expr(clause.expr, leading + "  ")

    def _dump_conds(self, conditions):
        leading = "                "
        for cond in conditions:
            self.stream.write("{}{}: if\n".format(leading, cond.name_tok.tok_text))
            self._dump_expr(cond.comparison, indent=leading + "  ")

    def _dump_results(self, results):
        leading = "                "
        for res in results:
            self.stream.write("{}{}: then\n".format(leading, res.name_tok.tok_text))
            self._dump_expr(res.result, indent=leading + "  ")


def unfold_disjunction(expr: "Expression") -> List["Expression"]:
    """Convert the child expressions of top-level disjunction expressions to a list."""
    if isinstance(expr, exprs.Disjunction):
        result = []
        for child in expr.childs:
            result.extend(unfold_disjunction(child))
        return result
    else:
        return [expr]


def dump(spec: Specification, output_stream: Optional[TextIO] = None):
    """Dump the provided specification to an output.

    Arguments:
        spec: Specification to dump.
        output_stream: Stream to write to, None means stdout.
    """
    dump_spec = _DumpSpec(output_stream)
    dump_spec.dump(spec)


def get_doc_comment_spec_elements(
    spec: Specification,
) -> Generator["DocStore", None, None]:
    """Retrieve the specification elements interested in getting documentation comments
    from the input.

    Note: Component definitions are added through components
        get_doc_comment_comp_elements

    Note: The implementation is highly knowledgeable about data structure here with
        respect to the implementation.
    """
    elem: DefaultDocStore
    for elem in spec.verb_prepos:
        assert isinstance(elem, DocStore)
        if elem.doc_tok:
            yield elem

    for elem in spec.rel_defs:
        assert isinstance(elem, DocStore)
        if elem.doc_tok:
            yield elem
