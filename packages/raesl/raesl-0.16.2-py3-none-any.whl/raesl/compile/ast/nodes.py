"""Node classes representing elementary and combined flows."""
from typing import TYPE_CHECKING, List, Optional

from raesl.compile.ast import comment_storage
from raesl.utils import split_first_dot

if TYPE_CHECKING:
    from raesl.compile.ast.types import BaseType
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import Counter


class Node:
    """Abstract class for nodes.

    Note that a Node only has a name. The typed sub-tree starts with VarNode.

    Arguments:
        name_tok: Name of the node.
    """

    def __init__(self, name_tok: "Token"):
        self.name_tok = name_tok


class VarNode(Node):
    """Abstract base class of a variable or parameter node that can be shared with
    variable groups and other users such as transformations and goals.

    Arguments:
        name_tok: Token with the name/location of the variable or parameter.
        the_type: Type of the variable or parameter.
    """

    def __init__(self, name_tok: "Token", the_type: "BaseType"):
        super(VarNode, self).__init__(name_tok)
        self.the_type = the_type

        assert name_tok.tok_type == "NAME"  # Should be a plain identifier.

    def resolve_node(self, name: str) -> Optional["VarNode"]:
        """Find the varparam (sub)node that matches the provided dotted 'name'.

        Arguments:
            name: Possibly dotted name that should point at an existing sub-node.
                The empty string denotes 'self'.

        Returns:
            The node that matches the name, or None if no such node exists. In the
                latter case, use 'self.get_error_position(name)' to get an indication
                where the match fails in the name.
        """
        raise NotImplementedError("Implement me in {}.".format(repr(self)))

    def get_error_position(self, name: str) -> int:
        """Return the index in the given string where an error occurs in resolving the
        node.

        Arguments:
            name: Name of the element to find.

        Returns:
            Approximated index in the string where matching the element fails.
                Returned value has no meaning if resolving a node succeeds.
        """
        raise NotImplementedError("Implement me in {}.".format(repr(self)))

    def add_comment(self, comment_tok: "Token"):
        """Add found documentation comment.

        Arguments:
            comment_tok: The raw documentation token to add.
        """
        raise NotImplementedError("Implement me in {}.".format(repr(self)))


class ElementaryVarNode(VarNode, comment_storage.DocElement):
    """Elementary variable/parameter node.

    Arguments:
        name_tok: Token with the name/position of the variable or parameter.
        the_type: Type of the variable or parameter.
        counter: Object to give out unique identification numbers, yet be resistant
            against re-use of imported modules.

    Attributes:
        id: Unique number of the node, mostly useful for dumps and debugging.
        comments: Stored comments of the node.
    """

    def __init__(self, name_tok: "Token", the_type: "BaseType", counter: "Counter"):
        super(ElementaryVarNode, self).__init__(name_tok, the_type)
        self.id = counter.next()
        self.comments: List[str] = []

    def resolve_node(self, name: str) -> Optional[VarNode]:
        if name != "":
            return None
        return self

    def get_error_position(self, name: str) -> int:
        return 0

    def add_comment(self, comment_tok: "Token"):
        """Add found documentation comment.

        Arguments:
            comment_tok: The raw documentation token to add.
        """
        self.comments.extend(comment_storage.decode_doc_comments(comment_tok))

    def get_comment(self):
        return self.comments

    def __repr__(self):
        return "ElementaryVarNode[" + str(self.id) + "]"


class CompoundVarNode(VarNode, comment_storage.DocAddElement):
    """Grouped variable/parameter node.

    Arguments:
        name_tok: Token with the name/position of the variable or parameter.
        the_type: Type of the variable or parameter.
        child_nodes: Child nodes of the group.

    Attributes:
        name_index: Mapping of name to the associated VarNode instance.
    """

    def __init__(self, name_tok: "Token", the_type: "BaseType", child_nodes: List[VarNode]):
        super(CompoundVarNode, self).__init__(name_tok, the_type)
        self.child_nodes = child_nodes
        self.name_index = dict((cn.name_tok.tok_text, cn) for cn in child_nodes)

        assert isinstance(self.child_nodes, list)

        # Bundle doesn't have duplicate child names.
        assert len(child_nodes) == len(self.name_index)

    def resolve_node(self, name: str) -> Optional[VarNode]:
        local_name, remaining_name, _dot_length = split_first_dot(name)
        if local_name == "":
            return self

        child_node = self.name_index.get(local_name)
        if child_node is None:
            return None
        return child_node.resolve_node(remaining_name)

    def get_error_position(self, name: str) -> int:
        local_name, remaining_name, dot_length = split_first_dot(name)

        child_node = self.name_index.get(local_name)
        if child_node is None:
            return 0  # Local name == first name is wrong.
        else:
            # Ask child about the position of the error.
            offset = child_node.get_error_position(remaining_name)
            return offset + len(local_name) + dot_length

    def add_comment(self, comment_tok: "Token"):
        """Compound node doesn't own a store, push comment down to all children."""
        for child in self.child_nodes:
            child.add_comment(comment_tok)


class GroupNode(Node):
    """Class describing content of a variable group. Unlike the VarNode above,
    a group node has no type of its own.

    Arguments:
        name_tok: Name of the group node.
        child_nodes: Elements of the group.
    """

    def __init__(self, name_tok: "Token", child_nodes: List[Node]):
        super(GroupNode, self).__init__(name_tok)
        self.child_nodes = child_nodes
