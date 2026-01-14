from copy import deepcopy
from typing import Generator, List, Optional

from ragraph.graph import Graph
from ragraph.node import Node

import raesl.doc.lines as lns
from raesl.doc import utils
from raesl.doc.locales import _, pm

LineGen = Generator[str, None, None]
TABLE_SINGLE = (
    "+------------------------------------------------"
    "------------------------------------------------+"
)
TABLE_LEFT_DOUBLE = (
    "+:==============================================="
    "================================================+"
)


def node_decomp_level(
    depth: int, comps: List[Node], h: int = 1, rich: str = None, rich_opts: dict = {}
):
    """Yield a decomposition level intro section."""
    yield lns.header(
        h,
        "{} {} \\label{{{}}}".format(
            _("system specification decomposition level"),
            depth + 1,
            "chp:esl" + str(depth + 1),
        ),
    )
    if depth == 0:
        leader = lns.snt(
            _(
                "this chapters describes the system of interest at the first "
                "decomposition level. That is, it describes {} components which play a "
                "role within the environment in which the system of interest must "
                "operate and the (functional) interactions between those components"
            ).format(len(comps))
        )
    elif depth > 0 and len(comps) == 1:
        leader = lns.snt(
            _(
                "this chapters describes the system of interest at decomposition level "
                "{} and introduces one additional component"
            ).format(depth + 1)
        )
    else:
        leader = lns.snt(
            _(
                "this chapters describes the system of interest at decomposition level "
                "{} and introduces {} additional components"
            ).format(depth + 1, len(comps))
        )
    yield leader

    if rich == "tex" or rich == "md":
        yield lns.snt(
            _(
                "in Figure \\ref{{{}}} the associated design-structure-matrix (DSM) is " "shown"
            ).format("fig:mdmlevel" + str(depth + 1))
        )
        yield lns.snt(
            _(
                "the DSM shows the dependencies between the elements that are relevant "
                "to this decomposition level"
            )
        )


def global_needs_and_designs(h: int = 1):
    """Yield a global need and design specification intro section."""
    yield lns.header(h, "{}".format(_("system-wide qualitative and quantitative specifications")))

    yield lns.snt(
        _(
            "this chapter lists all qualitative and quantitative design specifications "
            "that cannot be linked to a component"
        )
    )


def get_node_table(
    node: Node, graph: Optional[Graph] = None, sub_nodes: Optional[List[str]] = None
) -> List:
    """Returns a Markdown grid table."""
    table = []
    table.append(TABLE_SINGLE)
    table.append("| {} |".format(lns.bold(lns.node_path(node.name))))
    table.append(TABLE_LEFT_DOUBLE)
    lines = list(lns.lines(node, graph=graph))
    main_clause = lines[0].replace("\n", "")
    table.append("| {} |".format(main_clause))
    if len(lines) > 1:
        for line in lines[1:]:
            table.append("| {} |".format(line.replace("\n", "")))
        table.append("|    |")
    table.append(TABLE_SINGLE)

    if sub_nodes:
        table.append(
            "| {} |".format(
                lns.boldhead(_("subordinate function specifications")).replace("\n", "")
            )
        )
        table.append(TABLE_SINGLE)
        for s in sub_nodes:
            table.append("| {} |".format(lns.node_path(s).replace("\n", "")))
        table.append("|    |")

        table.append(TABLE_SINGLE)

    plain_comments = (
        [("comments", node.annotations.esl_info.get("comments", []))]
        if node.annotations.esl_info.get("comments", [])
        else []
    )

    for key, comments in plain_comments + list(
        node.annotations.esl_info["tagged_comments"].items()
    ):
        table.append("| {} |".format(lns.boldhead(_(key)).replace("\n", "")))
        table.append(TABLE_SINGLE)
        for comment in comments:
            table.append("| {} |".format(comment.replace("\n", "")))
        table.append(TABLE_SINGLE)

    table.append("")

    return table


# Goal specs
def comp_node_goal_reqs(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a goal-requirement section for a component"""
    glsn = utils.get_component_goals(node, g, constraint=False, inherited=False)
    glsa = utils.get_component_goals(node, g, constraint=False, inherited=True)

    if not glsn and not glsa:
        return

    yield lns.header(h, _("goal function requirements"))

    for gl in glsn:
        table = get_node_table(node=gl, graph=g)
        yield from table

    for gl in glsa:
        temp = deepcopy(gl)
        temp.annotations.esl_info["comments"].append(
            lns.snt(
                _("this goal function requirement automatically migrated from {}").format(
                    lns.node_path(temp.annotations.esl_info["body"]["active"])
                )
            )
        )
        temp.annotations.esl_info["body"]["active"] = node.name
        table = get_node_table(node=temp, graph=g)
        yield from table


def comp_node_goal_cons(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a goal-constraint section for a component"""
    glsn = utils.get_component_goals(node, g, constraint=True, inherited=False)
    glsa = utils.get_component_goals(node, g, constraint=True, inherited=True)
    if not glsn and not glsa:
        return

    yield lns.header(h, _("goal function constraints"))

    for gl in glsn:
        table = get_node_table(node=gl, graph=g)
        yield from table

    for gl in glsa:
        temp = deepcopy(gl)
        temp.annotations.esl_info["comments"].append(
            lns.snt(
                _("this goal function constraint automatically migrated from {}").format(
                    lns.node_path(temp.annotations.esl_info["body"]["active"])
                )
            )
        )
        temp.annotations.esl_info["body"]["active"] = node.name
        table = get_node_table(node=temp, graph=g)
        yield from table


# Transformation specs
def comp_node_transformation_reqs(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a transformation requirements section for a component."""
    trs = utils.get_component_transformations(node, g, constraint=False)
    if not trs:
        return

    trs = sorted(trs, key=lambda x: lns.node_path(x.name))

    yield lns.header(h, _("transformation function requirements"))

    for tr in trs:
        subs = set(
            [
                e.target.name
                for e in g.edges
                if e.source == tr and e.kind == "traceability_dependency"
            ]
        )
        table = get_node_table(tr, graph=g, sub_nodes=subs)
        yield from table


def comp_node_transformation_cons(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a transformation constraints section for a component."""
    trs = utils.get_component_transformations(node, g, constraint=True)
    if not trs:
        return

    trs = sorted(trs, key=lambda x: lns.node_path(x.name))

    yield lns.header(h, _("transformation function constraints"))

    for tr in trs:
        subs = [
            e.target.name for e in g.edges if e.source == tr and e.kind == "traceability_dependency"
        ]
        table = get_node_table(tr, graph=g, sub_nodes=subs)
        yield from table


# Behavior specs
def comp_node_behavior_reqs(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a behavior requirement section for a component node."""
    bhs = utils.get_component_behaviors(node, g, constraint=False)
    if not bhs:
        return

    yield lns.header(h, _("behavior requirements"))

    for b in bhs:
        table = get_node_table(node=b, graph=g)
        yield from table


# Behavior specs
def comp_node_behavior_cons(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a behavior constraint section for a component node."""
    bhs = utils.get_component_behaviors(node, g, constraint=True)
    if not bhs:
        return

    yield lns.header(h, _("behavior constraints"))

    for b in bhs:
        table = get_node_table(node=b, graph=g)
        yield from table


# Design specs
def comp_node_design_reqs(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a design requirements section for a component node."""
    drs = utils.get_component_designs(node, g, constraint=False)
    if not drs:
        return

    yield lns.header(h, _("quantitative design requirements"))

    for d in drs:
        table = get_node_table(node=d, graph=g)
        yield from table


# Design specs
def global_design_reqs(g: Graph, h: int = 1) -> LineGen:
    """Yield a global design requirements section."""
    drs = utils.get_global_designs(g, constraint=False)
    if not drs:
        return

    yield lns.header(h, _("quantitative design requirements"))

    for d in drs:
        table = get_node_table(node=d, graph=g)
        yield from table


def comp_node_design_cons(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a design constraint section for a component node."""
    dcs = utils.get_component_designs(node, g, constraint=True)
    if not dcs:
        return

    yield lns.header(h, _("quantitative design constraints"))

    for d in dcs:
        table = get_node_table(node=d, graph=g)
        yield from table


# Design specs
def global_design_cons(g: Graph, h: int = 1) -> LineGen:
    """Yield a global design constraint section."""
    dcs = utils.get_global_designs(g, constraint=True)
    if not dcs:
        return

    yield lns.header(h, _("quantitative design constraints"))

    for d in dcs:
        table = get_node_table(node=d, graph=g)
        yield from table


# Needs
def comp_node_needs(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a need section for a component node."""
    nds = utils.get_component_needs(node, g)
    if not nds:
        return

    yield lns.header(h, _("qualitative design requirements"))

    for n in nds:
        table = get_node_table(node=n, graph=g)
        yield from table


def global_needs(g: Graph, h: int = 1) -> LineGen:
    """Yield a global need section."""
    nds = utils.get_global_needs(g)
    if not nds:
        return

    yield lns.header(h, _("qualitative design requirements"))

    for n in nds:
        table = get_node_table(node=n, graph=g)
        yield from table


# Relations
def relation_node_table(r: Node, g: Graph) -> List:
    ri = r.annotations.esl_info
    table = []
    table.append(TABLE_SINGLE)
    table.append("| {} |".format(lns.bold(lns.node_path(r.name))))
    table.append(TABLE_LEFT_DOUBLE)
    table.append("| {} |".format(lns.bold(_("model definition name"))))
    table.append(TABLE_SINGLE)
    table.append("|    |")
    table.append("| {} |".format(ri["definition_name"].replace("\n", "")))
    table.append("|    |")
    table.append(TABLE_SINGLE)

    if ri.get("required_variables"):
        table.append("| {} |".format(lns.bold(_("required variables"))))
        table.append(TABLE_SINGLE)
        for v in ri.get("required_variables"):
            table.append("|    |")
            table.append("| {} |".format(lns.var_path(g[v]).replace("\n", "")))
            table.append("|    |")
        table.append(TABLE_SINGLE)

    if ri.get("returned_variables"):
        table.append("| {} |".format(lns.bold(_("returned variables"))))
        table.append(TABLE_SINGLE)
        for v in ri.get("returned_variables"):
            table.append("|    |")
            table.append("| {} |".format(lns.var_path(g[v]).replace("\n", "")))
            table.append("|    |")
        table.append(TABLE_SINGLE)

    if ri.get("related_variables"):
        table.append("| {} |".format(lns.bold(_("related variables"))))
        table.append(TABLE_SINGLE)
        for v in ri.get("related_variables"):
            table.append("|    |")
            table.append("| {} |".format(lns.var_path(g[v]).replace("\n", "")))
            table.append("|    |")
        table.append(TABLE_SINGLE)

    plain_comments = [("comments", ri.get("comments", []))] if ri.get("comments", []) else []

    for key, comments in plain_comments + list(ri["tagged_comments"].items()):
        table.append("| {} |".format(lns.boldhead(_(key)).replace("\n", "")))
        table.append(TABLE_SINGLE)
        for comment in comments:
            table.append("| {} |".format(comment.replace("\n", "")))
        table.append(TABLE_SINGLE)

    table.append("")
    return table


def comp_node_relations(node: Node, g: Graph, h: int = 1) -> LineGen:
    """Yield a relation section for a component."""
    rls = [n for n in g.nodes if n.kind == "relation_spec"]

    c_rls = []
    for r in rls:
        if g[node.name, r.name]:
            c_rls.append(r)

    if not c_rls:
        return

    c_rls = sorted(c_rls, key=lambda x: lns.node_path(x.name))

    yield lns.header(h, _("external models"))

    for r in c_rls:
        table = relation_node_table(r=r, g=g)
        yield from table


def comp_node_props(node: Node, g: Graph, h: int) -> LineGen:
    """Yield a properties section for a component node"""
    props = utils.get_component_properties(node, g)
    if not props:
        return

    name = node.name.split(".")[-1]
    yield lns.boldhead(_("properties") + ":")
    yield lns.cap(_("the following properties are specified for {}").format(name)) + ":"
    yield from lns.unordered(sorted([p.name.split(".")[-1] for p in props]))


def comp_node_subcomps(node: Node, h: int = 1):
    """Yield a subcomponents sections for a component."""
    if not node.children:
        return

    yield lns.header(h, _("sub-components"))

    child_names = [c.name.split(".")[-1] for c in node.children]

    name = node.name.split(".")[-1]

    yield lns.cap(_("{} is composed of the following sub-components:").format(name))

    yield from lns.unordered(sorted(child_names))


def var_node_table(g: Graph, h: int = 1, reference_list: bool = False) -> LineGen:
    """Yield a variable table section."""
    vrs = [n for n in g.nodes if n.kind == "variable"]
    if not vrs:
        return

    vrs = sorted(vrs, key=lambda x: lns.node_path(x.name))

    yield lns.header(h, _("list of variables"))

    yield lns.header(h + 1, _("definitions"))

    # yield "\\begin{landscape}"
    yield ""
    yield "| {} | {} | {} | {} | {} |".format(
        lns.boldhead(_("variable"), newlines=False),
        lns.boldhead(_("type"), newlines=False),
        lns.boldhead(_("domain"), newlines=False),
        lns.boldhead(_("units"), newlines=False),
        lns.boldhead(_("clarification"), newlines=False),
    )
    yield "|:---|:---|:---|:---|:---|"

    for v in vrs:
        vname, tname, domain, units, comments = get_var_table_row_elements(g, v)
        yield "| {} | {} | {} | {} | {} |".format(
            lns.var_path(v), lns.cap(tname), domain, units, comments
        )
    yield ""
    # yield "\\end{landscape}"

    if reference_list:
        yield "\\newpage{}"
        yield lns.header(h + 1, _("variable reference list"))

        yield "| {} | {} |".format(
            lns.boldhead(_("variable"), newlines=False),
            lns.boldhead(_("related to"), newlines=False),
        )
        yield "|:---|:---|"
        for v in vrs:
            rels = [
                lns.node_path(e.source.name)
                for e in g.edges
                if e.kind == "mapping_dependency" and e.target == v
            ]
            rels += [
                lns.node_path(e.target.name)
                for e in g.edges
                if e.kind == "mapping_dependency" and e.source == v
            ]
            if rels:
                refs = pm.hook.linguistic_enumeration(items=rels)
            else:
                refs = ""
            yield "| {} | {} |".format(lns.node_path(v.name), refs)
        yield ""


def get_var_table_row_elements(g: Graph, v: Node) -> str:
    """Yield elements of a row in a var table."""
    if v.annotations.esl_info["comments"]:
        comments = " ".join(v.annotations.esl_info["comments"])
    else:
        comments = ""

    for key, value in v.annotations.esl_info["tagged_comments"].items():
        comments += " ".join([" ", lns.bold(lns.cap(key + ":"))] + value)

    tname = v.annotations.esl_info["type_ref"]
    t = g[tname]
    if t.annotations.esl_info.get("domain"):
        intervals = []
        for ival in t.annotations.esl_info["domain"]:
            if ival["lowerbound"]["value"] != ival["upperbound"]["value"]:
                is_enum = False

                iv = ""
                if ival["lowerbound"]["value"]:
                    unit = ival["lowerbound"]["unit"]
                    if not unit:
                        unit = ""
                    iv += "{} {} $\\leq$ x".format(ival["lowerbound"]["value"], unit)

                if ival["upperbound"]["value"] and ival["lowerbound"]["value"]:
                    unit = ival["upperbound"]["unit"]
                    if not unit:
                        unit = ""
                    iv += "$\\leq$ {} {}".format(ival["upperbound"]["value"], unit)
                elif ival["upperbound"]["value"] and not ival["lowerbound"]["value"]:
                    unit = ival["upperbound"]["unit"]
                    if not unit:
                        unit = ""
                    iv += "x $\\leq$ {} {}".format(ival["upperbound"]["value"], unit)
                intervals.append(iv)
            else:
                is_enum = True
                value = ival["lowerbound"]["value"]
                if ival["lowerbound"]["unit"]:
                    value += " " + ival["lowerbound"]["unit"]
                intervals.append(value)
        if not is_enum:
            domain = ", ".join(intervals)
        else:
            domain = _("enumeration of ") + pm.hook.linguistic_enumeration(items=intervals)
    else:
        domain = ""
    if t.annotations.esl_info.get("units"):
        units = ",".join(t.annotations.esl_info.get("units"))
    else:
        units = ""

    return v.name, tname, domain, units, comments
