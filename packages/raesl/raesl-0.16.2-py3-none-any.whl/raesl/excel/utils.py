"""Excel export utility methods."""

from typing import Any, Dict, Generator, Iterable, List, Optional, Set, Tuple

from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet
from ragraph.edge import Edge
from ragraph.graph import Graph
from ragraph.node import Node

from raesl.doc import lines
from raesl.excel import text
from raesl.excel.defaults import MONO, WRAP  # noqa


def get_all_tags(nodes: List[Node]) -> List[str]:
    """Get all tagged comment keys from a list of nodes."""
    tags: List[str] = []
    seen: Set[str] = set()
    for node in nodes:
        node_tags = [
            tag for tag in node.annotations.esl_info["tagged_comments"].keys() if tag not in seen
        ]
        tags.extend(node_tags)
        seen.update(node_tags)
    return tags


def make_table(
    ws: Worksheet,
    name: str = "Table",
    min_row: int = 1,
    max_row: int = 1,
    min_col: int = 1,
    max_col: int = 1,
    style: TableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True),
) -> Table:
    """Make a table of a cell range in a worksheet."""
    ref = CellRange(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col)
    table = Table(name=name, displayName=name, ref=ref.coord)
    table.tableStyleInfo = style
    ws.add_table(table)
    return table


def apply_styling(
    ws: Worksheet,
    headers: List[str],
    defaults: Dict[str, Any] = dict(),
    start_row: int = 0,
    end_row: Optional[int] = None,
):
    """Apply styling to columns given some default option dictionary."""
    for i, header in enumerate(headers):
        styles = defaults.get(header, dict()).get("styles", dict())
        for i, row in enumerate(ws.rows):
            if i < start_row:
                continue
            if end_row is not None and i == end_row:
                break
            for cell in row:
                cell.font = styles.get("font", "monospace")

    dims = {}
    for i, row in enumerate(ws.rows):
        if i < start_row:
            continue
        if end_row is not None and i == end_row:
            break
        if i == start_row:
            continue

        for cell in row:
            if cell.value:
                dims[cell.column_letter] = max(
                    (dims.get(cell.column_letter, 0), len(str(cell.value)))
                )
    for col, value in dims.items():
        ws.column_dimensions[col].width = 1.5 * value


def parent_component(requirement: Node, skip: Optional[str] = "world") -> str:
    """Get parent component name of a requirement."""
    path = ".".join(requirement.name.split(".")[:-1])
    return lines.node_path(path, arrows=False, skip=skip) if skip else path


def parent_def(graph: Graph, requirement: Node) -> str:
    """Get the parent (component) definition of a requirement."""
    parent_comp = ".".join(requirement.name.split(".")[:-1])
    parent_def = graph[parent_comp].annotations.esl_info["definition_name"]
    return parent_def


def format_multiline(comments: List[str]) -> str:
    """Format multiline (list) text."""
    return "\n".join(c.rstrip("\\") for c in comments)


def requirement_kind(requirement: Node) -> str:
    """Get requirement kind."""
    info = requirement.annotations.esl_info
    if requirement.kind == "function_spec":
        return info["sub_kind"]
    elif requirement.kind == "design_spec":
        return "design"
    elif requirement.kind == "behavior_spec":
        return "behavior"
    else:
        return requirement.kind


def dedupe(iterable: Iterable) -> List[Any]:
    """Deduplicate any iterable into a list where the first occurrence is preserved."""
    seen: Set[Any] = set()
    unique: List[Any] = list()
    for item in iterable:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def yield_functional_dependencies(
    g: Graph, component: Node, flows: Optional[Set[str]]
) -> Generator[Edge, None, None]:
    """Yield all functional dependencies with which a component is involved."""
    if flows is None:
        for e in g.edges_from(component):
            if e.kind == "functional_dependency":
                yield e
    else:
        for e in g.edges_from(component):
            if e.kind == "functional_dependency" and flows.intersection(e.labels):
                yield e


def yield_all_function_specifications(
    g: Graph, functional_dependencies: Iterable[Edge]
) -> Generator[Tuple[Node, Node], None, None]:
    """Yield all function specification nodes and edge combinations
    for a given iterable of dependency edges.
    """
    for e in functional_dependencies:
        yield from yield_function_specifications(g, e)


def yield_function_specifications(
    g: Graph, functional_dependency: Edge
) -> Generator[Tuple[Node, Node], None, None]:
    """Get all function specification nodes corresponding to a functional dependency edge."""
    for spec in get_function_specification_names(functional_dependency):
        yield (functional_dependency, g[spec])


def get_function_specification_names(functional_dependency: Edge) -> List[str]:
    """Get the function specification node names corresponding to a functional dependency edge."""
    return (
        functional_dependency.annotations.get("esl_info", dict())
        .get("reason", dict())
        .get("function_specifications", [])
    )


def yield_active_functions(
    function_specifications: Iterable[Node], active_path: str
) -> Generator[Node, None, None]:
    """Yield all edge function combinations for which the active component matches the given
    path.
    """
    for n in function_specifications:
        if get_goal_active(n[1]) == active_path:
            yield n


def get_goal_active(function_specification: Node) -> Optional[str]:
    """Get the active component in a function specification."""
    esl_info = function_specification.annotations.get("esl_info", dict())
    if esl_info.get("sub_kind", None) != "goal":
        return None
    return esl_info.get("body", dict()).get("active", None)


def yield_passive_functions(
    function_specifications: Iterable[Node], passive_path: str
) -> Generator[Tuple[Node, Node], None, None]:
    """Yield all edge function combinations for which the passive component matches the given
    path.
    """
    for n in function_specifications:
        if get_goal_passive(n[1]) == passive_path:
            yield n


def get_goal_passive(function_specification: Node) -> Optional[str]:
    """Get the receiving component of a goal function."""
    esl_info = function_specification.annotations.get("esl_info", dict())
    if esl_info.get("sub_kind", None) != "goal":
        return None
    return esl_info.get("body", dict()).get("passive", None)


def get_function_flow_variables(
    function_specification: Node, edge: Edge, function_specifications: Set[Node] = set()
) -> Set[str]:
    """Get the variables involved with a functional dependency."""
    esl_info = function_specification.annotations.get("esl_info", dict())

    transformations = set(
        [
            f
            for (e, f) in function_specifications
            if f.annotations["esl_info"]["sub_kind"] == "transformation"
            and f.name in e.annotations["esl_info"]["reason"]["function_specifications"]
            and f.annotations["esl_info"]["body"]["active"] == edge.target.name
        ]
    )

    goal_vars = set(esl_info.get("body", dict()).get("variables", []))

    if transformations:
        trans_vars = set()
        for t in transformations:
            trans_vars = trans_vars.union(
                set(
                    t.annotations.get("esl_info", dict())
                    .get("body", dict())
                    .get("input_variables", [])
                    + t.annotations.get("esl_info", dict())
                    .get("body", dict())
                    .get("output_variables", [])
                )
            )

        flow_vars = goal_vars.intersection(trans_vars)
        return flow_vars if flow_vars else goal_vars
    else:
        return goal_vars


def get_function_subclauses(function_specification: Node) -> List[str]:
    """Get the subclauses belonging to a function specification."""
    esl_info = function_specification.annotations.get("esl_info", dict())
    return esl_info.get("body", dict()).get("subclauses", [])


def get_variable_type(variable: Node) -> str:
    """Get the variable type of a node."""
    return variable.annotations.get("esl_info", dict()).get("type_ref", "")


def build_active_goal_data(
    graph: Graph, edge: Edge, goal: Node, function_specifications: Set[Node] = set()
) -> Generator[Dict[str, Any], None, None]:
    """Create data dictionaries for the outgoing goals in the component overview.

    Keys:
        label: Goal label.
        target: Target component (shared path skipped).
        flows: Sent flow variables (shared path skipped).
        types: Flow variable types.
        subclause: Subclause label, optionally prefixed with numbers for OR-concatenations.
        subject: Subclause subject with prefix skipped.
        comparison: Abbreviated comparison (<, <=, ==, >=, >, ++, --).
        bound: Comparison variable or value.
        unit: Comparison value unit.
    """
    label = goal.name
    active = get_goal_active(goal)
    target = edge.target.name

    flows = get_function_flow_variables(goal, edge, function_specifications)
    types = set([get_variable_type(graph[f]) for f in flows if graph.node_dict.get(f, False)])
    types = ", ".join(types)
    subclauses = get_function_subclauses(goal)

    # Skip everything in common, except the last part, the flow's own name.
    active_skip = active[: active.rfind(".") + 1] if active else ""
    stripped_flows = [text.strip_prefix(f, active_skip) for f in flows]
    display_flows = ", ".join(stripped_flows)

    common_parts = text.get_common_parts(flows)
    skip_prefix = ".".join(common_parts[:-1])

    label = text.strip_prefix(label, active_skip)
    target = text.strip_prefix(target, active_skip)

    if not subclauses:
        data = dict(label=label, target=target, flows=display_flows, types=types)
        yield data

    for sc in subclauses:
        for sc_data in build_subclause_data(sc, skip_prefix):
            data = dict(label=label, target=target, flows=display_flows, types=types, **sc_data)
            yield data


def build_passive_goal_data(
    graph: Graph, edge: Edge, goal: Node, function_specifications: Set[Node]
) -> Generator[Dict[str, Any], None, None]:
    """Create data dictionaries for the incoming goals in the component overview.

    Keys:
        label: Goal label.
        target: Target component (shared path skipped).
        flows: Sent flow variables (shared path skipped).
        types: Flow variable types.
        subclause: Subclause label, optionally prefixed with numbers for OR-concatenations.
        subject: Subclause subject with prefix skipped.
        comparison: Abbreviated comparison (<, <=, ==, >=, >, ++, --).
        bound: Comparison variable or value.
        unit: Comparison value unit.
    """
    label = goal.name
    active = edge.target.name
    passive = get_goal_passive(goal)
    flows = get_function_flow_variables(goal, passive, function_specifications)
    types = set([get_variable_type(graph[f]) for f in flows if graph.node_dict.get(f, False)])
    types = ", ".join(types)
    subclauses = get_function_subclauses(goal)

    # Skip everything in common, except the last part, the flow's own name.
    passive_skip = passive[: passive.rfind(".") + 1] if passive else ""
    stripped_flows = [text.strip_prefix(f, passive_skip) for f in flows]
    display_flows = ", ".join(stripped_flows)

    common_parts = text.get_common_parts(flows)
    skip_prefix = ".".join(common_parts[:-1])

    label = text.strip_prefix(label, passive_skip)
    active = text.strip_prefix(active, passive_skip)

    if not subclauses:
        data = dict(label=label, source=active, flows=display_flows, types=types)
        yield data

    for sc in subclauses:
        for sc_data in build_subclause_data(sc, skip_prefix):
            data = dict(label=label, source=active, flows=display_flows, types=types, **sc_data)
            yield data


def build_subclause_data(
    subclause_info: Dict[str, Any], skip_prefix: str
) -> Generator[Dict[str, Any], None, None]:
    """Create a subclause data dictionary for each OR clause for use in the component overview.

    Keys:
        subclause: Subclause label, optionally prefixed with numbers for OR-concatenations.
        subject: Subclause subject with prefix skipped.
        comparison: Abbreviated comparison (<, <=, ==, >=, >, ++, --).
        bound: Comparison variable or value.
        unit: Comparison value unit.
    """
    name = subclause_info.get("name", None)
    if name is None:
        return  # No label, no joy.
    bodies = subclause_info.get("body", [])  # concatenated OR clauses
    for i, body in enumerate(bodies):
        if len(bodies) == 1:
            subclause = name
        else:
            subclause = f"OR-{i}-{name}"
        data = build_subclause_body_data(body, skip_prefix)
        data["subclause"] = subclause
        yield data


def build_subclause_body_data(subclause_body: Dict[str, Any], skip_prefix: str) -> Dict[str, Any]:
    """Create a subclause's body data dict for use in the component overview.

    Keys:
        subject: Subclause subject with prefix skipped.
        comparison: Abbreviated comparison (<, <=, ==, >=, >, ++, --).
        bound: Comparison variable or value.
        unit: Comparison value unit.
    """
    result = dict()

    subject = subclause_body.get("subject", "")
    result["subject"] = text.strip_prefix(subject, skip_prefix)

    comparison = subclause_body.get("comparison", None)
    if comparison is not None:
        result["comparison"] = text.abbreviate_comparison(comparison)

    bound = subclause_body.get("bound", None)
    if isinstance(bound, str):  # Other variable
        result["bound"] = text.strip_prefix(bound, skip_prefix)
    elif isinstance(bound, dict):  # value / unit
        result["bound"] = bound.get("value", None)
        result["unit"] = bound.get("unit", None).strip("[]")

    return result
