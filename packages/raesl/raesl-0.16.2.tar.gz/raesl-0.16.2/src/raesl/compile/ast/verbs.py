"""Verb / preposition definitions in ESL."""
from typing import TYPE_CHECKING

from raesl.compile.ast.comment_storage import DefaultDocStore

if TYPE_CHECKING:
    from raesl.compile.scanner import Token


class VerbPreposDef(DefaultDocStore):
    """A verb and a pre-position definition.

    Arguments:
        verb: Verb token.
        prepos: Pre-position token.
    """

    def __init__(self, verb: "Token", prepos: "Token"):
        super(VerbPreposDef, self).__init__(verb)
        self.verb = verb
        self.prepos = prepos

    def __str__(self):
        return "VerbPrepos('{}', '{}')".format(self.verb.tok_text, self.prepos.tok_text)
