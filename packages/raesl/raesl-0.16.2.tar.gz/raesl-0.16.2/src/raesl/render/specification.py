"""Document renderer and its subsections."""
# pyright: reportAttributeAccessIssue=false, reportRedeclaration=false

from dataclasses import dataclass
from typing import Any

import ratio_typst
from ragraph.graph import Graph
from ragraph.node import Node

from raesl import logger
from raesl.render.elements import (
    Bold,
    BoldHeading,
    Heading,
    Par,
    Reference,
    Table,
    TableCell,
    TableHeader,
    TableHLine,
    Unordered,
)
from raesl.render.figure import Mdm
from raesl.render.paths import PathDisplay, pretty_path, var_path
from raesl.render.renderer import LineGen, Renderer
from raesl.utils import (
    cap,
    get_component_behaviors,
    get_component_designs,
    get_component_goals,
    get_component_needs,
    get_component_properties,
    get_component_relations,
    get_component_transformations,
    get_global_designs,
    get_global_needs,
    get_node_comments,
    get_node_tagged_comments,
    is_number,
    path_contents_or_str,
)


@dataclass
class DesignRuleLine(Renderer):
    """Render a design rule as a sentence."""

    graph: Graph
    rule: dict[str, Any]
    parent: Node | None = None

    @property
    def subject(self) -> str:
        return str(
            var_path(
                self.context,
                node=self.rule["subject"],
                graph=self.graph,
            )
        )

    @property
    def aux(self) -> str:
        return self.rule["auxiliary"]

    @property
    def comparison(self) -> str:
        return self.rule["comparison"]

    @property
    def bound(self) -> str:
        bound = self.rule["bound"]["value"]
        if bound == "t.b.d.":
            return str(Bold(self.context, bound))
        elif is_number(bound):
            return str(bound)
        else:
            return str(
                var_path(
                    self.context,
                    node=bound,
                    graph=self.graph,
                )
            )

    @property
    def unit(self) -> str | None:
        return self.rule["bound"]["unit"] or None

    def gen_content(self) -> LineGen:
        subject, aux, comparison = self.subject, self.aux, self.comparison
        if comparison == "maximized" or comparison == "minimized":
            yield self.context.l10n.design_rule_line(
                subject,
                aux,
                comparison,
                bound=None,
                unit=None,
            )
        else:
            (bound, unit) = self.bound, self.unit
            yield self.L10N.design_rule_line(
                subject,
                aux,
                comparison,
                bound=bound,
                unit=unit,
            )


@dataclass
class SubclauseLine(Renderer):
    """Render a subclause as an options sentence."""

    graph: Graph
    subclause: dict[str, Any]
    path: PathDisplay | None = None
    parent: Node | None = None

    def gen_content(self) -> LineGen:
        label = self.path or Bold(
            self.context,
            self.subclause["name"],
        )
        options = self.L10N.options(
            str(
                DesignRuleLine(
                    self.context,
                    graph=self.graph,
                    rule=rule,
                    parent=self.parent,
                )
            )
            for rule in self.subclause["body"]
        )
        yield f"{label}: {options}."


@dataclass
class Requirement(Renderer):
    """Render any requirement with a main clause and optional subclauses."""

    graph: Graph
    path: PathDisplay
    clause: str
    subclauses: list[dict[str, Any]]
    parent: Node | None = None
    comments: list[str] | None = None
    tagged_comments: dict[str, list[str]] | None = None

    def gen_content(self) -> LineGen:
        subclauses = self.subclauses
        plural = len(subclauses) != 1

        clause = self.clause
        if self.subclauses:
            clause = f"{clause}, {self.L10N.with_subclause(plural=plural)}:"
        else:
            clause = f"{clause}."

        def sub_line(sc: dict[str, Any]):
            path = pretty_path(
                self.context,
                node=self.join((self.path.ref_path, sc["name"])),
                graph=self.graph,
                parent=self.parent,
                skip_all=True,
                label=True,
                bold=True,
            )
            return SubclauseLine(
                self.context,
                graph=self.graph,
                subclause=sc,
                path=path,
                parent=self.parent,
            )

        subs = (
            [
                TableCell(
                    self.context,
                    Unordered(
                        self.context,
                        [sub_line(sc) for sc in subclauses],
                    ),
                )
            ]
            if subclauses
            else []
        )

        comments: list[str | Renderer] = []
        if self.comments:
            comments.append(Bold(self.context, cap(self.L10N.comments())))
            comments.append(TableCell(self.context, self.comments))

        if self.tagged_comments:
            for tag, contents in self.tagged_comments.items():
                comments.append(Bold(self.context, tag))
                comments.append(TableCell(self.context, contents))

        yield from Table(
            self.context,
            columns=["1fr"],
            align=["left"],
            children=[
                TableHeader(
                    self.context,
                    TableCell(self.context, self.path),
                    repeat=True,
                ),
                clause,
            ]
            + subs
            + comments,
        )


@dataclass
class Goal(Renderer):
    """Render a goal function."""

    graph: Graph
    node: Node
    parent: Node | None = None

    @property
    def active(self) -> str:
        return str(
            pretty_path(
                self.context,
                node=self.node.annotations.esl_info["body"]["active"],
                graph=self.graph,
                skip_all=True,
                link=True,
            )
        )

    @property
    def aux(self) -> str:
        return self.node.annotations.esl_info["body"]["auxiliary"]

    @property
    def verb(self) -> str:
        return self.node.annotations.esl_info["body"]["verb"]

    @property
    def flows(self) -> str:
        return self.L10N.enumeration(
            sorted(
                set(
                    str(
                        var_path(
                            self.context,
                            node=self.graph[flow],
                            graph=self.graph,
                            link=True,
                        )
                    )
                    for flow in self.node.annotations.esl_info["body"]["variables"]
                )
            )
        )

    @property
    def prep(self) -> str:
        return self.node.annotations.esl_info["body"]["preposition"]

    @property
    def passive(self) -> str:
        return str(
            pretty_path(
                self.context,
                node=self.node.annotations.esl_info["body"]["passive"],
                graph=self.graph,
                link=True,
                skip_all=True,
            )
        )

    @property
    def subclauses(self) -> list[dict[str, Any]]:
        return self.node.annotations.esl_info["body"]["subclauses"]

    @property
    def clause(self) -> str:
        return self.L10N.goal_clause(
            self.active,
            self.aux,
            self.verb,
            self.flows,
            self.prep,
            self.passive,
        )

    @property
    def comments(self) -> list[str]:
        return self.node.annotations.esl_info.get("comments", [])

    @property
    def tagged_comments(self) -> dict[str, list[str]]:
        return self.node.annotations.esl_info.get("tagged_comments").items()

    def gen_content(self) -> LineGen:
        yield from Requirement(
            self.context,
            graph=self.graph,
            path=pretty_path(self.context, node=self.node, graph=self.graph, label=True, bold=True),
            parent=self.parent,
            clause=self.clause,
            subclauses=self.subclauses,
            comments=self.comments,
            tagged_comments=self.tagged_comments,
        )


@dataclass
class Transformation(Renderer):
    """Render a transformation function."""

    graph: Graph
    node: Node
    parent: Node | None = None

    @property
    def active(self) -> str:
        return str(
            pretty_path(
                self.context,
                node=self.node.annotations.esl_info["body"]["active"],
                graph=self.graph,
                link=True,
                skip_all=True,
                parent=self.parent,
            )
        )

    @property
    def aux(self) -> str:
        return self.node.annotations.esl_info["body"]["auxiliary"]

    @property
    def verb(self) -> str:
        return self.node.annotations.esl_info["body"]["verb"]

    @property
    def in_flows(self) -> str:
        return self.L10N.enumeration(
            sorted(
                set(
                    str(
                        var_path(
                            self.context,
                            node=self.graph[flow],
                            graph=self.graph,
                            link=True,
                        )
                    )
                    for flow in self.node.annotations.esl_info["body"]["input_variables"]
                )
            )
        )

    @property
    def prep(self) -> str:
        return self.node.annotations.esl_info["body"]["preposition"]

    @property
    def out_flows(self) -> str:
        return self.L10N.enumeration(
            sorted(
                set(
                    str(
                        var_path(
                            self.context,
                            node=self.graph[flow],
                            graph=self.graph,
                            link=True,
                        )
                    )
                    for flow in self.node.annotations.esl_info["body"]["output_variables"]
                )
            )
        )

    @property
    def subclauses(self) -> list[dict[str, Any]]:
        return self.node.annotations.esl_info["body"]["subclauses"]

    @property
    def clause(self) -> str:
        return self.L10N.transformation_clause(
            self.active,
            self.aux,
            self.verb,
            self.in_flows,
            self.prep,
            self.out_flows,
        )

    @property
    def comments(self) -> list[str]:
        return self.node.annotations.esl_info.get("comments", [])

    @property
    def tagged_comments(self) -> dict[str, list[str]]:
        return self.node.annotations.esl_info.get("tagged_comments").items()

    def gen_content(self) -> LineGen:
        yield from Requirement(
            self.context,
            graph=self.graph,
            path=pretty_path(self.context, node=self.node, label=True, bold=True),
            parent=self.parent,
            clause=self.clause,
            subclauses=self.subclauses,
            comments=self.comments,
            tagged_comments=self.tagged_comments,
        )


@dataclass
class Design(Renderer):
    """Design specification."""

    graph: Graph
    node: Node
    parent: Node | None = None

    @property
    def rules(self) -> list[dict[str, Any]]:
        return self.node.annotations.esl_info["body"]

    @property
    def subclauses(self) -> list[dict[str, Any]]:
        return self.node.annotations.esl_info.get("subclauses", [])

    @property
    def clause(self) -> str:
        return self.L10N.options(
            str(
                DesignRuleLine(
                    self.context,
                    graph=self.graph,
                    rule=r,
                    parent=self.parent,
                )
            )
            for r in self.rules
        )

    @property
    def comments(self) -> list[str]:
        return self.node.annotations.esl_info.get("comments", [])

    @property
    def tagged_comments(self) -> dict[str, list[str]]:
        return self.node.annotations.esl_info.get("tagged_comments").items()

    def gen_content(self) -> LineGen:
        yield from Requirement(
            self.context,
            graph=self.graph,
            path=pretty_path(self.context, node=self.node, graph=self.graph, label=True),
            parent=self.parent,
            clause=self.clause,
            subclauses=self.subclauses,
            comments=self.comments,
            tagged_comments=self.tagged_comments,
        )


@dataclass
class Behavior(Renderer):
    """Behavior specification."""

    graph: Graph
    node: Node
    parent: Node | None = None

    def gen_typst(self) -> LineGen:
        cases = self.node.annotations.esl_info["cases"]

        if not cases:
            return

        case, when, then = (
            self.L10N.behavior_case(False),
            self.L10N.behavior_when(),
            self.L10N.behavior_then(),
        )

        children = [
            TableHeader(
                self.context,
                TableCell(
                    self.context,
                    pretty_path(
                        self.context,
                        graph=self.graph,
                        node=self.node,
                        skip_all=True,
                        label=True,
                    ),
                    align="left",
                ),
                repeat=True,
            ),
        ]

        default = self.node.annotations.esl_info.get("default")
        if default:
            children.append(
                TableCell(
                    self.context, Bold(self.context, f"{self.L10N.behavior_when_default()}, {then}")
                )
            )
            children.append(
                TableCell(
                    self.context,
                    Unordered(
                        self.context,
                        [
                            SubclauseLine(
                                self.context,
                                graph=self.graph,
                                subclause=sc,
                                parent=self.parent,
                            )
                            for sc in default
                        ],
                    ),
                )
            )

        def case_display(c: dict[str, Any]) -> LineGen:
            yield TableCell(self.context, Bold(self.context, f"{case}: {c['name']}"))

            yield Bold(self.context, when)
            yield from TableCell(
                self.context,
                Unordered(
                    self.context,
                    [
                        SubclauseLine(
                            self.context,
                            path=pretty_path(
                                self.context,
                                node=self.join((self.node.name, sc["name"])),
                                graph=self.graph,
                                parent=self.parent,
                                skip_all=True,
                                label=True,
                            ),
                            graph=self.graph,
                            subclause=sc,
                        )
                        for sc in c["when_clauses"]
                    ],
                ),
            )

            yield Bold(self.context, then)
            yield from TableCell(
                self.context,
                Unordered(
                    self.context,
                    items=[
                        SubclauseLine(
                            self.context,
                            graph=self.graph,
                            subclause=sc,
                            parent=self.parent,
                        )
                        for sc in c["then_clauses"]
                    ],
                ),
            )

        if cases:
            if default:
                children.append(TableHLine(self.context))
            c = cases[0]
            children.extend(case_display(c))

        for c in cases[1:]:
            children.append(TableHLine(self.context))
            children.extend(case_display(c))

        yield from Table(
            self.context, columns=["1fr"], align=["left"], children=children, inset="(x: 0pt)"
        )


@dataclass
class Need(Renderer):
    """Need specification."""

    graph: Graph
    node: Node
    parent: Node | None = None

    def gen_typst(self) -> LineGen:
        label = pretty_path(
            self.context,
            graph=self.graph,
            node=self.node,
            label=True,
        )
        subject = pretty_path(
            self.context,
            graph=self.graph,
            node=self.node.annotations.esl_info["subject"],
        )
        text = self.node.annotations.esl_info["text"]

        children = [
            TableHeader(self.context, TableCell(self.context, label), repeat=True),
            f"{subject} {text}",
        ]

        yield from Table(
            self.context, columns=["1fr"], align=["left"], children=children, inset="(x: 0pt)"
        )


@dataclass
class Component(Renderer):
    """Component section."""

    graph: Graph
    node: Node
    level: int = 1

    def gen_content(self) -> LineGen:
        yield from self.heading()
        yield from self.intro()
        yield from self.comments()
        yield from self.properties()
        yield from self.subcomponents()
        yield from self.goals()
        yield from self.transforms()
        yield from self.behaviors()
        yield from self.designs()
        yield from self.needs()
        yield from self.relations()

    def heading(self) -> LineGen:
        path = pretty_path(
            self.context,
            self.node,
            graph=self.graph,
            skip_all=True,
            label=True,
            bold=False,
        )
        yield from Heading(
            self.context,
            body=f"{cap(self.L10N.component(False))}: {path}",
            level=self.level,
        )

    def intro(self) -> LineGen:
        path = pretty_path(self.context, node=self.node, skip_all=True, link=True)
        yield Par(
            self.context,
            self.L10N.section_intro(subject=str(path)),
        )
        if self.node.parent and self.node.parent.name != "world":
            yield Par(
                self.context,
                self.L10N.is_a_subcomponent_of(
                    parent=str(
                        pretty_path(
                            self.context,
                            node=self.node.parent,
                            link=True,
                        )
                    )
                ),
            )

    def comments(self) -> LineGen:
        comments = get_node_comments(component=self.node)
        tagged_comments = get_node_tagged_comments(component=self.node).items()

        if comments:
            yield from BoldHeading(
                self.context,
                body=self.L10N.comments(),
                cap=True,
            )
            yield from Par(
                self.context,
                body=comments,
            )

        for key, comments in tagged_comments:
            yield from BoldHeading(
                self.context,
                body=key,
            )
            yield from Par(
                self.context,
                body=comments,
            )

    def properties(self) -> LineGen:
        properties = get_component_properties(component=self.node, graph=self.graph)
        if not properties:
            return
        plural = len(properties) != 1
        yield from Heading(
            self.context,
            body=cap(self.L10N.property(True)),
            level=self.level + 1,
        )
        yield from Par(
            self.context,
            body=self.L10N.following_properties_for(
                subject=str(
                    pretty_path(
                        self.context,
                        node=self.node,
                        link=True,
                    )
                ),
                plural=plural,
            ),
        )
        yield from Unordered(
            self.context,
            items=sorted(
                [
                    str(
                        pretty_path(
                            self.context,
                            graph=self.graph,
                            node=p,
                            parent=self.node,
                            skip_all=True,
                        )
                    )
                    for p in properties
                ]
            ),
        )

    def subcomponents(self) -> LineGen:
        subcomps = self.node.children
        if not subcomps:
            return
        plural = len(subcomps) != 1
        yield from Heading(
            self.context, body=cap(self.L10N.subcomponent(plural=plural)), level=self.level + 1
        )
        yield from Par(
            self.context,
            body=self.L10N.subcomponents_defined_within(
                str(
                    pretty_path(
                        self.context,
                        node=self.node,
                        link=True,
                    )
                ),
                len(subcomps),
            ),
        )
        yield from Unordered(
            self.context,
            items=sorted(
                str(
                    pretty_path(
                        self.context,
                        node=n,
                        skip_all=True,
                        link=True,
                    )
                )
                for n in subcomps
            ),
        )

    def goals(self) -> LineGen:
        cons = get_component_goals(
            component=self.node, graph=self.graph, constraint=True, inherited=True
        )
        if cons:
            yield from Heading(
                self.context,
                body=cap(self.L10N.goal_constraint(len(cons) != 1)),
                level=self.level + 1,
            )
            for con in cons:
                yield from Goal(
                    self.context,
                    graph=self.graph,
                    node=con,
                    parent=self.node,
                )

        reqs = get_component_goals(
            component=self.node, graph=self.graph, constraint=False, inherited=True
        )
        if reqs:
            yield from Heading(
                self.context,
                body=cap(self.L10N.goal_requirement(len(reqs) != 1)),
                level=self.level + 1,
            )
            for req in reqs:
                yield from Goal(
                    self.context,
                    graph=self.graph,
                    node=req,
                    parent=self.node,
                )

    def transforms(self) -> LineGen:
        cons = get_component_transformations(component=self.node, graph=self.graph, constraint=True)
        if cons:
            yield from Heading(
                self.context,
                body=cap(self.L10N.transformation_constraint(len(cons) != 1)),
                level=self.level + 1,
            )
            for con in cons:
                yield from Transformation(
                    self.context,
                    graph=self.graph,
                    node=con,
                    parent=self.node,
                )

        reqs = get_component_transformations(
            component=self.node, graph=self.graph, constraint=False
        )
        if reqs:
            yield from Heading(
                self.context,
                body=cap(self.L10N.transformation_requirement(len(reqs) != 1)),
                level=self.level + 1,
            )
            for req in reqs:
                yield from Transformation(
                    self.context,
                    graph=self.graph,
                    node=req,
                    parent=self.node,
                )

    def behaviors(self) -> LineGen:
        cons = get_component_behaviors(component=self.node, graph=self.graph, constraint=True)
        if cons:
            yield from Heading(
                self.context,
                body=cap(self.L10N.behavior_constraint(len(cons) != 1)),
                level=self.level + 1,
            )
            for con in cons:
                yield from Behavior(
                    self.context,
                    graph=self.graph,
                    node=con,
                    parent=self.node,
                )

        reqs = get_component_behaviors(component=self.node, graph=self.graph, constraint=False)
        if reqs:
            yield from Heading(
                self.context,
                body=cap(self.L10N.behavior_requirement(len(reqs) != 1)),
                level=self.level + 1,
            )
            for req in reqs:
                yield from Behavior(
                    self.context,
                    graph=self.graph,
                    node=req,
                    parent=self.node,
                )

    def designs(self) -> LineGen:
        cons = get_component_designs(component=self.node, graph=self.graph, constraint=True)
        if cons:
            yield from Heading(
                self.context,
                body=cap(self.L10N.design_constraint(len(cons) != 1)),
                level=self.level + 1,
            )
            for con in cons:
                yield from Design(
                    self.context,
                    graph=self.graph,
                    node=con,
                    parent=self.node,
                )

        reqs = get_component_designs(component=self.node, graph=self.graph, constraint=False)
        if reqs:
            yield from Heading(
                self.context,
                body=cap(self.L10N.design_requirement(len(reqs) != 1)),
                level=self.level + 1,
            )
            for req in reqs:
                yield from Design(
                    self.context,
                    graph=self.graph,
                    node=req,
                    parent=self.node,
                )

    def needs(self) -> LineGen:
        needs = get_component_needs(component=self.node, graph=self.graph)
        if needs:
            yield from Heading(
                self.context,
                body=(cap(self.L10N.need(len(needs) != 0))),
                level=self.level + 1,
            )
            for need in needs:
                yield from Need(
                    self.context,
                    graph=self.graph,
                    node=need,
                    parent=self.node,
                )

    def relations(self) -> LineGen:
        relations = sorted(
            get_component_relations(component=self.node, graph=self.graph), key=lambda x: x.name
        )
        if not relations:
            return

        yield from Heading(
            self.context,
            body=self.L10N.relation(plural=len(relations) != 0),
            level=self.level + 1,
            capitalize=True,
        )

        for relation in relations:
            yield from Relation(
                self.context,
                node=relation,
                parent=self.node,
                graph=self.graph,
            )


@dataclass
class Relation(Renderer):
    """Describe an instantiated component relation."""

    graph: Graph
    node: Node
    parent: Node | None = None

    def gen_content(self) -> LineGen:
        full = pretty_path(
            self.context,
            node=self.node,
            graph=self.graph,
            bold=True,
        )
        name = pretty_path(
            self.context,
            node=self.node,
            graph=self.graph,
            skip_all=True,
            parent=self.parent,
            bold=True,
        )
        def_name = Bold(
            self.context,
            self.node.annotations.esl_info["definition_name"],
        )

        children = [
            TableHeader(
                self.context,
                TableCell(self.context, full),
            ),
            TableCell(
                self.context,
                f"{name} is a {def_name} relation.",
            ),
        ]

        comments = get_node_comments(component=self.node)
        tagged_comments = get_node_tagged_comments(component=self.node).items()

        if comments:
            children.append(
                BoldHeading(
                    self.context,
                    body=self.L10N.comments(),
                    cap=True,
                )
            )
            children.append(
                TableCell(
                    self.context,
                    body=comments,
                )
            )

        for key, comments in tagged_comments:
            children.append(
                BoldHeading(
                    self.context,
                    body=key,
                )
            )
            children.append(
                TableCell(
                    self.context,
                    body=comments,
                )
            )

        info = self.node.annotations.esl_info

        required = info.get("required_variables")
        if required:
            children.append(TableHLine(self.context))
            children.append(
                Bold(
                    self.context,
                    self.L10N.required_variable(len(required) != 0),
                )
            )
            children.extend(
                TableCell(
                    self.context,
                    Unordered(
                        self.context,
                        [
                            var_path(
                                self.context,
                                node=v,
                                graph=self.graph,
                            )
                            for v in required
                        ],
                    ),
                )
            )

        returned = info.get("returned_variables")
        if returned:
            children.append(TableHLine(self.context))
            children.append(
                Bold(
                    self.context,
                    self.L10N.returned_variable(len(returned) != 0),
                )
            )
            children.extend(
                TableCell(
                    self.context,
                    Unordered(
                        self.context,
                        [
                            var_path(
                                self.context,
                                node=v,
                                graph=self.graph,
                            )
                            for v in returned
                        ],
                    ),
                )
            )
        related = info.get("related_variables")
        if related:
            children.append(
                TableHLine(
                    self.context,
                )
            )
            children.append(
                Bold(
                    self.context,
                    self.L10N.related_variable(len(related) != 0),
                )
            )
            children.extend(
                TableCell(
                    self.context,
                    Unordered(
                        self.context,
                        [
                            var_path(
                                self.context,
                                node=v,
                                graph=self.graph,
                                parent=self.parent,
                            )
                            for v in related
                        ],
                    ),
                )
            )

        yield from Table(
            self.context,
            children=children,
            columns=["1fr"],
            align=["left"],
        )


@dataclass
class Function(Renderer):
    """Function specification."""

    graph: Graph
    node: Node
    level: int = 1

    def gen_content(self) -> LineGen:
        match self.node.annotations.esl_info["sub_kind"]:
            case "goal":
                yield from Goal(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )
            case "transformation":
                yield from Transformation(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )
            case other:
                raise NotImplementedError(
                    f"No function line rendering implementation exists for the '{other}' kind.",
                )


@dataclass
class AnyNode(Renderer):
    """Describe any node.

    It may be of the following kinds: component, function, design, behavior, or need.
    """

    graph: Graph
    node: Node
    level: int = 1

    def gen_content(self):
        match self.node.kind:
            case "component":
                yield from Component(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )

            case "function_spec":
                yield from Function(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )

            case "design_spec":
                yield from Design(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )

            case "behavior_spec":
                yield from Behavior(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )

            case "need":
                yield from Need(
                    self.context,
                    self.graph,
                    self.node,
                    level=self.level,
                )

            case _:
                raise NotImplementedError(f"Node kind {self.node.kind} is not implemented.")


@dataclass
class NodeDecompositionLevel(Renderer):
    """Describe a node decomposition level."""

    graph: Graph
    depth: int
    components: list[Node]
    level: int = 1

    def gen_content(self) -> LineGen:
        prefix = cap(self.L10N.decomposition_level())
        yield from Heading(
            self.context,
            f"{prefix} {self.depth + 1}",
            level=self.level,
        )

        depth, n_comps = self.depth + 1, len(self.components)
        leader = self.L10N.announce_decomposition_level(level=depth, n_components=n_comps)

        if Renderer.RICH:
            fig_ref = self.L10N.dsm_ref(
                reference=str(
                    Reference(
                        self.context,
                        kind="fig",
                        label=f"mdm-level-{depth}",
                    )
                )
            )
            yield from Par(
                self.context,
                [leader, fig_ref],
            )
            logger.debug("Adding MDM image at level {}...".format(depth))
            yield from Mdm(
                self.context,
                graph=self.graph,
                depth=depth,
            )
        else:
            yield from Par(
                self.context,
                leader,
            )

        if self.depth == 0:
            yield from GlobalNeedsDesigns(
                self.context,
                graph=self.graph,
                level=self.level + 1,
            )


@dataclass
class GlobalNeedsDesigns(Renderer):
    """Global needs and design specifications."""

    graph: Graph
    level: int = 1

    def gen_content(self) -> LineGen:
        needs = get_global_needs(graph=self.graph)
        cons = get_global_designs(graph=self.graph, constraint=True)
        reqs = get_global_designs(graph=self.graph, constraint=False)

        if not needs and not cons and not reqs:
            return

        yield from Heading(
            self.context,
            body=self.L10N.unlinked_needs_designs_heading(),
            level=self.level,
            capitalize=True,
        )
        yield from Par(
            self.context,
            body=self.L10N.unlinked_needs_designs_intro(),
        )

        parent = self.graph["world"]

        if needs:
            yield from Heading(
                self.context,
                body=self.L10N.need(plural=len(needs) != 1),
                level=self.level + 1,
                capitalize=True,
            )
        for need in needs:
            yield from Need(
                self.context,
                graph=self.graph,
                node=need,
                parent=parent,
            )

        if cons:
            yield from Heading(
                self.context,
                body=self.L10N.design_constraint(plural=len(cons) != 1),
                level=self.level + 1,
                capitalize=True,
            )
        for con in cons:
            yield from Design(
                self.context,
                graph=self.graph,
                node=con,
                parent=parent,
            )

        if reqs:
            yield from Heading(
                self.context,
                body=self.L10N.design_requirement(plural=len(cons) != 1),
                level=self.level + 1,
                capitalize=True,
            )
        for req in reqs:
            yield from Design(
                self.context,
                graph=self.graph,
                node=req,
                parent=parent,
            )


@dataclass
class Author(ratio_typst.Author):
    """Author of the document."""


@dataclass
class Info(ratio_typst.Info):
    """Document info."""


@dataclass
class VarTable(Renderer):
    """Variable table appendix."""

    def gen_content(self) -> LineGen:
        self.todo()
        if False:
            yield
        return None


@dataclass
class Appendices(Renderer):
    """Appendices to renderer."""

    graph: Graph
    var_table: bool

    def gen_content(self) -> LineGen:
        yield from VarTable(self.context)


@dataclass
class Specification(Renderer):
    """Render a components section."""

    graph: Graph

    def gen_content(self) -> LineGen:
        components = sorted(
            self.graph["world"].children,
            key=lambda n: n.name,
        )
        depth = 0
        level = 1

        while components:
            logger.debug("Processing nodes at level {}...".format(depth))
            yield from NodeDecompositionLevel(
                self.context,
                graph=self.graph,
                depth=depth,
                components=components,
                level=level,
            )

            for comp in components:
                yield from Component(
                    self.context,
                    graph=self.graph,
                    node=comp,
                    level=level + 1,
                )

            children = [child for comp in components for child in comp.children]
            components = children
            depth += 1


@dataclass
class Document(Renderer):
    """Output document."""

    graph: Graph
    info: Info
    prologue: str | None = None
    epilogue: str | None = None
    outline_depth: int | None = 2
    var_table: bool = True

    def __post_init__(self) -> None:
        self.prologue = path_contents_or_str(self.prologue)
        self.epilogue = path_contents_or_str(self.epilogue)

    def gen_typst(self) -> LineGen:
        backmatter = []
        if self.epilogue:
            backmatter.append(self.epilogue)
        backmatter.extend(Appendices(self.context, graph=self.graph, var_table=self.var_table))

        outline = None if self.outline_depth is None else f"outline(depth: {self.outline_depth})"

        yield ratio_typst.Report(
            theme=ratio_typst.Theme(
                info=self.info,
                frontmatter=str(self.prologue).rstrip("\n") if self.prologue else None,
                backmatter=str(Par(self.context, backmatter)).rstrip("\n") if backmatter else None,
                outline=outline,
            ),
        ).render()

        # Stops long 'raw' variables names from forcing justified lines in tables.
        yield "#show table: set par(justify: false)"

        yield from Specification(self.context, graph=self.graph)

    def gen_html(self) -> LineGen:
        yield self.prologue
        yield from Specification(self.context, graph=self.graph)
        yield self.epilogue
        yield from Appendices(self.context, graph=self.graph, var_table=self.var_table)
