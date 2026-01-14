"""RaESL GraphViz diagram plotting module."""

from typing import Any, Dict, Optional, Union

from ragraph.generic import Mapping, field
from ragraph.plot.generic import Style as RaGraphStyle


class DiagramStyle(Mapping):
    """RaESL Graphviz diagram style mapping."""

    _defaults = dict(
        digraph=dict(filename="raesl.dot"),
        orientation="TD",
        node_shapes=dict(
            component="rectangle",
            goal="hexagon",
            transformation="ellipse",
        ),
        edge_styles=dict(
            functional_dependency="solid",
            logical_dependency="dashed",
            traceability_dependency="dotted",
            mapping_dependency="solid",
            composition_dependency="solid",
        ),
        show_hierarchy=True,
        list_variables=False,
        show_root_children=False,
        show_neighbor_children=False,
        show_function_dependencies=False,
    )

    def __init__(
        self,
        digraph: Optional[Dict[str, Any]] = None,
        orientation: Optional[str] = None,
        node_shapes: Optional[Dict[str, str]] = None,
        edge_styles: Optional[Dict[str, str]] = None,
        show_hierarchy: Optional[bool] = None,
        list_variables: Optional[bool] = None,
        show_root_children: Optional[bool] = None,
        show_neighbor_children: Optional[bool] = None,
        show_function_dependencies: Optional[bool] = None,
    ):
        super().__init__(
            digraph=digraph,
            orientation=orientation,
            node_shapes=node_shapes,
            edge_styles=edge_styles,
            show_hierarchy=show_hierarchy,
            list_variables=list_variables,
            show_root_children=show_root_children,
            show_neighbor_children=show_neighbor_children,
            show_function_dependencies=show_function_dependencies,
        )

    @field
    def digraph(self) -> Dict[str, Any]:
        """Options for the :obj:`graphviz.Digraph` object."""

    @field
    def orientation(self) -> str:
        """Orientation of the layout of the graph. One of 'LR' (left-to-right) or
        'TD' (top-down)."""

    @field
    def node_shapes(self) -> Dict[str, str]:
        """Dictionary of node kinds to Graphviz node shapes."""

    @field
    def edge_styles(self) -> Dict[str, str]:
        """Dictionary of edge kind to Graphviz edge styles."""

    @field
    def show_hierarchy(self) -> bool:
        """Whether to draw the nested hierarchical structure."""

    @field
    def list_variables(self) -> bool:
        """Whether to list the variables of goal- and transformation specifications."""

    @field
    def show_root_children(self) -> bool:
        """Whether to display the children of the root component within a functional
        context diagram."""

    @field
    def show_neighbor_children(self) -> bool:
        """Whether to display the children of the neighbor components within a
        functional context diagram."""

    @field
    def show_function_dependencies(self) -> bool:
        """Whether to display dependencies between functions within a traceability
        diagram."""


class Style(Mapping):
    """RaESL plotting style mapping."""

    _defaults = dict(
        diagram=DiagramStyle(),
        ragraph=RaGraphStyle(piemap={"display": "labels", "mode": "relative"}),
    )

    def __init__(
        self,
        diagram: Optional[Union[DiagramStyle, Dict[str, Any]]] = None,
        ragraph: Optional[Union[RaGraphStyle, Dict[str, Any]]] = None,
    ):
        super().__init__(
            diagram=diagram,
            ragraph=ragraph,
        )

    @field
    def diagram(self) -> DiagramStyle:
        """Graphviz diagram style."""

    @field
    def ragraph(self) -> RaGraphStyle:
        """RaGraph style options, used for Multi-Domain matrices."""
