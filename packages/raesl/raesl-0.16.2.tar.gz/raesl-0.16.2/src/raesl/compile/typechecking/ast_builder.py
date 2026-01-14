"""Classes to collect and store information from the parsing process, perform checking
on the information for being correct, and construct an AST as result along with a log of
found diagnostics.

The AstBuilder operates at top section level (types, verbs, relation definitions, and
component definitions). It leaves all the details of each section to dedicated child
builders (thus creating a highly modular checker), and acts as call dispatcher and
global controller in the type-checking and ast building process once parsing has
finished.

Notable parts in the class are
- Child builders for each top section part.
- Diagnostics store shared with all the child builders.
- Storage of doc-comments in the input for attaching them to the correct parts of the
  produced specification after parsing.
- Call dispatcher for the child builders that a new top or sub-section has been found,
  allowing them to clean up processing if needed.
- Entry points for the parser to push found information to the child builders.
- The 'finish_parse' entry point to perform all type checking, and produce the AST and
  found diagnostics.
"""

from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from raesl.compile import diagnostics
from raesl.compile.ast import exprs, specification
from raesl.compile.ast.comment_storage import DocCommentDistributor
from raesl.compile.typechecking.compdef_builder import ComponentDefBuilder
from raesl.compile.typechecking.reldef_builder import RelationDefBuilder
from raesl.compile.typechecking.type_builder import TypeBuilder
from raesl.compile.typechecking.verb_builder import VerbDefBuilder

if TYPE_CHECKING:
    from raesl.compile.scanner import Token


class AstBuilder:
    """Builder to collect information from the parse process, perform type
    checking, and produce an AST and reported diagnostics.

    Arguments:
        diag_store: Storage for diagnostics while building the AST.

    Attributes:
        doc_distributor: Object that distributes doc comments to interested elements of
            the specification.
        section_notify_list: Builders to notify of a new section.
        type_builder: Builder for constructing types.
        verb_builder: Builder for constructing verb/prepositions.
        reldef_builder: Builder for constructing relations.
        compdef_builder: Builder for constructing components.
    """

    def __init__(self, diag_store: diagnostics.DiagnosticStore):
        self.diag_store = diag_store
        self.doc_distributor = DocCommentDistributor(self.diag_store)
        self.section_notify_list: List[
            Union[TypeBuilder, RelationDefBuilder, ComponentDefBuilder]
        ] = []

        self.type_builder = TypeBuilder(self)
        self.verb_builder = VerbDefBuilder(self)
        self.reldef_builder = RelationDefBuilder(self)
        self.compdef_builder = ComponentDefBuilder(self)

    def add_typedef(
        self,
        type_name: "Token",
        parent_name: Optional["Token"],
        enum_spec: Optional[List[exprs.Value]],
        unit_spec: Optional[List["Token"]],
        ival_spec: Optional[List[Tuple[Optional[exprs.Value], Optional[exprs.Value]]]],
        cons_spec: Optional[exprs.Value],
    ):
        """Forward call to type builder."""
        self.type_builder.add_typedef(
            type_name, parent_name, enum_spec, unit_spec, ival_spec, cons_spec
        )

    def new_bundle_type(self, bundle_name: "Token"):
        """Forward call to type builder."""
        self.type_builder.new_bundle_type(bundle_name)

    def add_bundle_field(
        self,
        field_name: "Token",
        type_name: Optional["Token"],
    ):
        """Forward call to type builder."""
        self.type_builder.add_bundle_field(
            field_name,
            type_name,
        )

    def add_verbdef(self, verb_tok: "Token", prepos_tok: "Token"):
        """Forward call to verb definition builder."""
        self.verb_builder.add_verbdef(verb_tok, prepos_tok)

    def add_reldef(self, name: "Token"):
        """Forward call to relation definition builder."""
        self.reldef_builder.add_reldef(name)

    def reldef_param_header(self, header_tok: "Token", direction: str):
        """Forward call to relation definition builder."""
        self.reldef_builder.reldef_param_header(header_tok, direction)

    def reldef_add_param(self, name: "Token", type_name: "Token", multi: bool):
        """Forward call to relation definition builder."""
        self.reldef_builder.reldef_add_param(name, type_name, multi)

    def register_new_section(self, other_builder):
        """Entry point for a child builder to declare interest in receiving
        notifications about new sections in the file.
        """
        self.section_notify_list.append(other_builder)

    def notify_new_section(self, tok: Optional["Token"], new_top_section: bool):
        """Parser has started a new section, finish all 'in-progress' definitions.

        Arguments:
            tok: Token indicating the position of the new section. None is used for EOF.
            new_top_section: If set, a new type, verbs, or component definition has
                been found, else a new section within a component has been detected.
        """
        if tok:
            # New section started, documentation after this point doesn't belong
            # to a previous element.
            self.doc_distributor.add_dummy_element(tok)

        for builder in self.section_notify_list:
            builder.notify_new_section(new_top_section)

    def finish_parse(self, doc_comments: List["Token"]) -> Optional[specification.Specification]:
        """Finish processing the collected information, that is, perform type checking.

        Arguments:
            doc_comments: Raw documentation comments rescued from the scanner.
        """
        # Tell all builders current section is done.
        self.notify_new_section(None, True)

        # Convert collected information to AST.
        spec = specification.Specification()
        self.verb_builder.finish(spec)
        self.type_builder.finish(spec)
        self.reldef_builder.finish(spec)  # Requires types.
        self.compdef_builder.finish(spec, self.doc_distributor)  # Requires types, verbs, reldefs.

        # Add specification elements to the doc distributor.
        for elem in specification.get_doc_comment_spec_elements(spec):
            self.doc_distributor.add_element(elem)

        # Hand out all doc comments.
        self.doc_distributor.resolve(doc_comments)
        return spec
