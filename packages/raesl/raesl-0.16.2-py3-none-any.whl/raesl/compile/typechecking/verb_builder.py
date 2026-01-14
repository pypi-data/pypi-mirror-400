"""Class to store and check verb / pre-position definitions."""
import collections
from typing import TYPE_CHECKING, Dict, List, Tuple

from raesl.compile import diagnostics
from raesl.compile.ast import verbs

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder


class VerbDefBuilder:
    """Part of the builders to deal with verbs / pre-positions."""

    def __init__(self, ast_builder: "AstBuilder"):
        # Make the builder problem store available locally.
        self.diag_store = ast_builder.diag_store

        # Setup local storage
        self.storage: Dict[Tuple[str, str], List[verbs.VerbPreposDef]]
        self.storage = collections.defaultdict(list)

    def add_verbdef(self, verb_tok: "Token", prepos_tok: "Token"):
        """Store the provided verb/prepos combination."""

        # For error reporting, order storage by the verb and prepos text.
        key = (verb_tok.tok_text.lower(), prepos_tok.tok_text.lower())
        vdef = verbs.VerbPreposDef(verb_tok, prepos_tok)
        self.storage[key].append(vdef)

    def finish(self, spec: "Specification"):
        """Finish collecting by checking the collected verb-prepositions. Store result
        in the provided specification.
        """
        for verb_prepos_text, verbdefs in self.storage.items():
            if len(verbdefs) != 1:
                # More than one definition of the same verb/prepos combination.
                dupes = [vd.verb.get_location() for vd in verbdefs]
                self.diag_store.add(
                    diagnostics.W200(
                        " ".join(verb_prepos_text),
                        "verb-preposition combination",
                        location=dupes[0],
                        dupes=dupes,
                    )
                )

        # spec.verb_prepos = [verbdefs[0] for verbdefs in self.storage.values()]
        # mypy generates false positive on the list comprehension
        spec.verb_prepos = []
        for verbdefs in self.storage.values():
            spec.verb_prepos.append(verbdefs[0])
