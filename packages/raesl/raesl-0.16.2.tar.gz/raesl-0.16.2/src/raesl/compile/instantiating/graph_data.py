"""Classes for the instantiated component graph."""
from typing import TYPE_CHECKING, List

from raesl.compile import diagnostics

if TYPE_CHECKING:
    from raesl.compile.ast.components import VarParam


class InstNode:
    """Instance node that connects one or more elementary nodes that are connected
    through parameters.

    Arguments:
        name: Dotted variable name of the associated elementary type.
        variable: Variable that created the node.

    Attributes:
        number: Unique number for each instance nodes, mostly useful for debugging.
        params: Parameters connected to the variable through this node.
        comments: Comments from the connected variable and parameters.
    """

    next_num = 1000

    def __init__(self, name: str, variable: "VarParam"):
        self.number = InstNode.next_num
        InstNode.next_num = self.number + 1

        self.name = name
        self.variable = variable
        self.params: List["VarParam"] = []
        self.comments: List[str] = []

    def add_param(self, param: "VarParam"):
        assert not param.is_variable
        self.params.append(param)

    def add_comment(self, words: List[str]):
        self.comments.extend(words)

    def owners(self):
        return [param for param in self.params if param.is_property]

    def check_owner(self, diag_store: diagnostics.DiagnosticStore):
        owners = self.owners()
        if len(owners) > 1:
            # Multiple property owners
            diag_store.add(
                diagnostics.E400(
                    self.name,
                    location=self.variable.name_tok.get_location(),
                    owners=[owner.name_tok.get_location() for owner in owners],
                )
            )

    def get_comment(self):
        return [p.comments for p in self.params]

    def __repr__(self):
        return "InstNode[" + str(self.number) + "]"
