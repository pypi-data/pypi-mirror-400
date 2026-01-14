"""Relation definition and instantiation."""
from typing import TYPE_CHECKING, List, Optional

from raesl.compile.ast.comment_storage import DefaultDocStore

if TYPE_CHECKING:
    from raesl.compile.ast.types import BaseType
    from raesl.compile.scanner import Token

INPUT = "input"
OUTPUT = "output"
INPOUT = "inp_out"


class RelationDefParameter:
    """Parameter of a relation definition.

    Arguments:
        name: Name of the parameter.
        type_name: Name of the type of the parameter.
        direction: Direction of the parameter.
        multi: If set, parameter may be specified more than once.

    Attributes:
        type: Actual type of the parameter.
    """

    def __init__(self, name: "Token", type_name: "Token", direction: str, multi: bool):
        self.name = name
        self.type_name = type_name
        self.direction = direction
        self.multi = multi

        self.type: Optional["BaseType"] = None


class RelationDefinition(DefaultDocStore):
    """Relation definition.

    Arguments:
        name: Name of the relation definition.

    Attributes:
        params: Parameters of the definition.
    """

    def __init__(self, name: "Token"):
        super(RelationDefinition, self).__init__(name)
        self.name = name
        self.params: List[RelationDefParameter] = []
