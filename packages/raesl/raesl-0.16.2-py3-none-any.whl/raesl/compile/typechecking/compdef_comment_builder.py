"""Deal with the comment sections in a component definition."""
from typing import TYPE_CHECKING, List

from raesl.compile import diagnostics
from raesl.compile.ast import comment_storage
from raesl.compile.ast.components import get_doc_comment_comp_elements

if TYPE_CHECKING:
    from raesl.compile.ast.comment_storage import DocCommentDistributor
    from raesl.compile.ast.components import ComponentDefinition
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.compdef_builder import CompDefChildBuilders


class CompDefCommentBuilder:
    """Collect the names in the 'comments' section, and hook them into the doc comments
    distributor.

    Arguments:
        comp_child_builders: Component definition's section builders storage.

    Attributes:
        diag_store: Diagnostics storage of component definition child builders.
        name_toks: Names occurring in a comment section, collected during parsing.
    """

    def __init__(self, comp_child_builders: "CompDefChildBuilders"):
        self.diag_store = comp_child_builders.diag_store
        self.name_toks: List["Token"] = []

    def add_comment(self, name_tok: "Token"):
        """Parser found a name in a comments section, store it for future processing."""
        self.name_toks.append(name_tok)

    def finish_comp(
        self, comp_def: "ComponentDefinition", doc_distributor: "DocCommentDistributor"
    ):
        """Process all collected names. This method should be the final step in
        processing a component definition, as it needs all elements that take doc
        comments.

        Arguments:
            comp_def: Component definition to finish.
            doc_distributor: Object that distributes doc comments to interested elements
                of the specification.
        """
        comp_def_doc_elements = get_doc_comment_comp_elements(comp_def)
        available = {}  # Available elements in the specification, ordered by their name.
        for elm in comp_def_doc_elements:
            assert elm.doc_tok is not None
            available[elm.doc_tok.tok_text] = elm

        for name_tok in self.name_toks:
            # Find language elements to point to by their main name only.
            i = name_tok.tok_text.find(".")
            if i < 0:
                main_name = name_tok.tok_text
            else:
                main_name = name_tok.tok_text[:i]

            opt_elm = available.get(main_name)
            if opt_elm is None:
                # Report an error if an element is not available.
                if comp_def.name_tok is None:
                    comp_name = "world"
                else:
                    comp_name = comp_def.name_tok.tok_text

                # Can't find doc element in component.
                self.diag_store.add(
                    diagnostics.E205(
                        f"element '{name_tok.tok_text}'",
                        f"component '{comp_name}'",
                        name_tok.get_location(),
                    )
                )

                # Construct a dummy element so any comment after it is caught.
                # No errors to report as the above already reported one.
                doc_distributor.add_dummy_element(name_tok, False)

            else:
                # Add a proxy, redirecting doc comments to the correct element.
                doc_distributor.add_element(comment_storage.ProxyDocStore(name_tok, opt_elm))
