"""Functions for instantiating the component tree."""
from typing import Optional

from ragraph.graph import Graph

from raesl.compile import diagnostics
from raesl.compile.ast.specification import Specification
from raesl.compile.instantiating.edge_building import EdgeFactory
from raesl.compile.instantiating.node_building import NodeFactory


class GraphFactory:
    """Graph factory class.

    Converts a specification into a graph containing a node hierarchy and edges for
    derived dependencies between nodes.

    Arguments:
        diag_store: Storage for found diagnostics during the process.

    Attributes:
        node_factory: Factory that parses spec into Node objects.
        edge_factory: Factory that derives edges from found Node objects.
    """

    def __init__(
        self,
        diag_store: diagnostics.DiagnosticStore,
        spec: Optional[Specification] = None,
    ):
        self.diag_store = diag_store
        self.spec = spec
        self.node_factory = NodeFactory(self.diag_store, spec=spec)
        self.edge_factory = EdgeFactory(self.diag_store, node_store=self.node_factory.node_store)

    def make_graph(self, spec: Optional[Specification] = None) -> Optional[Graph]:
        """Instantiate the tree defined in the specification, and build a graph for it.

        Arguments:
            spec: Specification object holding parsed ESL data.

        Returns:
            None if no root is available, else the constructed graph.

        Note:
            Problems may be reported during instantiation and added to self.diag_store.
        """
        self.spec = self.spec if spec is None else spec
        if self.spec is None or self.spec.world is None:
            return None

        node_dict = self.node_factory.make_nodes(self.spec)
        edges = self.edge_factory.make_edges()

        return Graph(nodes=node_dict.values(), edges=edges)
