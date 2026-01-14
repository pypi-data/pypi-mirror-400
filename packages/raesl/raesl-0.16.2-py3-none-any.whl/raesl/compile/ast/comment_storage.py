"""Code for handling documentation comments in AST objects.

The code has two main concepts, namely DocStore which expresses the capability
to find elements that can store doc comments, and DocAddElement which expresses
the capability to actually store such comments.

In general thus, storing a doc comment thus involves two steps. First the correct
element is searched based on a supplied (possibly dotted) name, then the
comment is actually stored if an element could be found.

As the above is pretty minimal, several additional classes exist.
- The DocElement can both store comments and also provide them again.
  (Compound element can't store comments, but forward them to their children and
  thus have no way to retrieve the comments given to them.)
- The DefaultDocElement implements DocElement.
- The DefaultDocStore implements a DocStore as well as DocElement for non-dotted
  names, providing a simple way to add doc comment storage to many of the
  language elements.

Internally, some more classes exist.

- The ProxyDocStore that acts as DocStore elsewhere in the specification. Its
  primary use is in comment sections, pointing to the actual elements to receive
  the doc comments of the section.

- The DummyElement acts as a DocStore for any doc comment, and reports a warning
  about them being ignored. These elements act as barrier and guard against doc
  comments being added to a previous element where that should not happen.
  For example, doc comments after a 'define type' line, should not be added
  to the definitions above that line.

- Finally, DocCommentDistributor implements the distribution of doc comments to all
  elements of the specification after type-checking has been performed.
"""

import itertools
from collections import defaultdict
from typing import Generator, List, Optional

from raesl.compile import diagnostics
from raesl.compile.scanner import Token


class DocAddElement:
    """Interface class of an element that can store doc comments."""

    def add_comment(self, comment_tok: Token) -> None:
        """Add found documentation comment.

        Arguments:
            comment_tok: The raw documentation token to add.
        """
        raise NotImplementedError("Implement me in {}".format(repr(self)))


class DocElement(DocAddElement):
    """Interface class of an element that can store and retrieve doc comments."""

    def get_comment(self) -> List[str]:
        """Retrieve the stored comments."""
        raise NotImplementedError("Implement me in {}".format(repr(self)))


class DefaultDocElement(DocElement):
    """Default implementation for storing and retrieving doc comments.

    Attributes:
        comments: The comments themselves, non-empty text after dropping the leading
            '#<' and surrounding white-space.
    """

    def __init__(self) -> None:
        super(DefaultDocElement, self).__init__()
        self.comments: List[str] = []

    def add_comment(self, comment_tok: Token) -> None:
        """Add found documentation comment.

        Arguments:
            comment_tok: The raw documentation token to add.
        """
        self.comments.extend(decode_doc_comments(comment_tok))

    def get_comment(self) -> List[str]:
        return self.comments


def decode_doc_comments(comment_tok: Token) -> List[str]:
    """Convert a doc comment token to the containing description text.

    Arguments:
        comment_tok: Token with the documentation comment.

    Returns:
        The text (for as far as it exists).
    """
    assert comment_tok.tok_text.startswith("#<")
    text = comment_tok.tok_text[2:].strip()
    if text:
        return [text]
    return []


class DocStore:
    """Interface class that can find where to store doc comments for a given name.
    If doc_tok is None, the element does not get any documentation comments.

    Arguments:
        doc_tok: Token defining the position of the element in the input for
            documenting. Documentation comments after this position and before any
            other existing DocStore.doc_tok will be attached to this element.
    """

    def __init__(self, doc_tok: Optional[Token]):
        self.doc_tok = doc_tok

    def resolve_element(self, name: str) -> Optional[DocAddElement]:
        """Try to find the documentation element indicated by its (dotted) name.

        Arguments:
            name: Name of the element to find.

        Returns:
            The documentation element associated with the provided name if it can be
                resolved.
        """
        raise NotImplementedError("Implement me in {}".format(repr(self)))

    def get_error_position(self, name: str) -> int:
        """Return the index in the given string where an error occurs in resolving the
        name.

        Arguments:
            name: Name of the element to find.

        Returns:
            Approximated index in the string where matching the element fails.
                Returned value has no meaning if resolving succeeds.
        """
        return 0


class DefaultDocStore(DocStore, DefaultDocElement):
    """Class that can store and retrieve doc-comments for non-dotted names.

    Arguments:
        doc_tok: Token defining the position of the element in the input for
            documenting. Documentation comments after this position and before any
            other existing DocStore.doc_tok will be attached to this element.
    """

    def __init__(self, doc_tok: Optional[Token]):
        # Can't use super() due to different argument lists.
        DocStore.__init__(self, doc_tok)
        DefaultDocElement.__init__(self)

    def resolve_element(self, name: str):
        if self.doc_tok is None:
            return None
        if "." in name:
            return None
        if self.doc_tok.tok_text != name:
            return None

        return self

    def get_error_position(self, name: str):
        i = name.find(".")
        if i >= 0:
            return i
        return 0


class ProxyDocStore(DocStore):
    """Proxy element that represents a real DocStore element except at a different
    position in the specification. This is useful in 'comment' sections where names of
    elements are provided that exist elsewhere in the component.

    Arguments:
        doc_tok: Token defining the position of the element in the input for
            documenting. Documentation comments after this position and before any
            other existing DocStore.doc_tok will be attached to this element.
        real_element: Real element which is symbolically at the 'doc_tok' position, too.
    """

    def __init__(self, doc_tok: Token, real_element: DocStore):
        super(ProxyDocStore, self).__init__(doc_tok)
        self.real_element = real_element

    def resolve_element(self, name: str):
        return self.real_element.resolve_element(name)

    def get_error_position(self, name: str):
        return self.real_element.get_error_position(name)


class DummyElement(DocStore, DocElement):
    """Class for catching documentation elements that have no proper owner. Used for
    reporting warnings that such documentation is ignored.

    Arguments:
        doc_tok: Token defining the position of the element in the input for
            documenting. Documentation comments after this position and before any
            other existing DocStore.doc_tok will be attached to this element.
        report_errors: Whether to add errors to the problem storage.
    """

    def __init__(self, doc_tok: Token, report_errors: bool = True):
        super(DummyElement, self).__init__(doc_tok)
        self.raw_comments: List[Token] = []
        self.report_errors = report_errors

    def resolve_element(self, name: str):
        # We don't actually care about the name, as anything ending up here is reported
        # as error.
        return self

    def get_error_position(self, name: str):
        # resolve_element() never fails, so the returned value has no meaning anyway.
        return 0

    def add_comment(self, comment_tok: Token):
        # Do not convert to text to preserve the precise position of the comment.
        self.raw_comments.append(comment_tok)

    def get_comment(self):
        assert False, "Comments are not usable, call self.report() instead."

    def report(self, diag_store: diagnostics.DiagnosticStore):
        """Report a warning about all received documentation comments.

        Arguments:
            diag_store: Storage for reported diagnostics.
        """
        if not self.raw_comments or not self.report_errors:
            return

        locs = [tok.get_location() for tok in self.raw_comments]
        diag_store.add(diagnostics.W300(location=locs[0], comments=locs))


class DocCommentDistributor:
    """Class for assigning documentation comments to relevant elements in the
    specification.

    Arguments:
        diag_store: Storage for reported diagnostics.

    Attributes:
        elements: Elements interested in receiving documentation comments.
        dummy_elements: Elements that catch documentation comments without a proper
            home, for warning the user about such comments.
    """

    def __init__(self, diag_store: diagnostics.DiagnosticStore):
        self.diag_store = diag_store
        self.elements: List[DocStore] = []
        self.dummy_elements: List[DummyElement] = []

        # This 'tok' violates pretty much all assumptions of Token, do not try to use
        # it outside the distributor context.
        tok = Token(
            tok_type="DUMMY_TK",
            tok_text="",
            fname=None,
            offset=-1,
            line_offset=-1,
            line_num=-1,
        )
        self.add_dummy_element(tok)

    def add_dummy_element(self, doc_tok: Token, report_errors: bool = True):
        """Insert a dummy element based on the provided token.

        Arguments:
            doc_tok: Token that defines the position of the dummy element.
            report_errors: Whether to report errors for comments that get attached to
                the dummy element.
        """
        dds = DummyElement(doc_tok, report_errors)
        self.dummy_elements.append(dds)
        self.add_element(dds)

    def add_element(self, element: DocStore):
        """Add the provided element to the elements interested in getting doc comments.

        Arguments:
            element: Element to add.
        """
        self.elements.append(element)

    def resolve(self, doc_comments: List[Token]):
        """Distribute the provided documentation comments to the interested elements,
        and report any documentation comments that get assigned in a DummyElement,
        as those are at the wrong spot in the specification.

        Arguments:
            doc_comments: Documentation comments found in the input specification.
        """
        if not doc_comments:  # No comments, nothing to do.
            return

        # At this point, there is
        # - the provided doc_comments, a mostly sorted list of 'DOC_COMMENT_TK' tokens
        #   containing the documentation comments.
        # - the self.elements list, the interested elements, including all dummy
        #   elements for reporting about doc comments at weird places. The tokens of the
        #   former must be assigned to the latter based on offset information and file.
        #   All doc comments must be assigned to that element with the largest offset
        #   less than the offset of the comment within the same file.

        # Sort the comments on file name and offset.
        dc_dict = defaultdict(list)
        for dc in doc_comments:
            dc_dict[dc.fname].append(dc)

        for val in dc_dict.values():
            val.sort(key=lambda tok: tok.offset)

        # The tricky part is that the element list may have several elements at the
        # same offset, due to blindly inserting dummy elements. This can be resolved by
        # either being more careful about offsets of dummy elements, or by filtering
        # such duplicates afterwards.
        #
        # The code here does the latter. Sort the interested elements, and filter the
        # dummy duplicate elements out of it. Also append a None element to notify
        # about the end of the list.

        # Sort the elements on file name and offset.
        elm_dict = defaultdict(list)
        for elm in self.elements:
            fname = getattr(elm.doc_tok, "fname", "unknown-file")
            elm_dict[fname].append(elm)

        for key, val in elm_dict.items():
            offsets = [v.doc_tok.offset for v in val]
            sequence = [idx for _, idx in sorted(zip(offsets, range(len(val))))]
            elm_dict[key] = [val[idx] for idx in sequence]

        nondup_elm_dict = {}
        for key, val in elm_dict.items():
            nondup_elm_dict[key] = list(_drop_dup_dummies(val))

        # Last element before the position at 'doc_index'.
        cur_elem: Optional[DocStore] = None

        # Next element after cur_elem, or None if not initialized or at the end.
        next_elem: Optional[DocStore] = None

        for cur_file in nondup_elm_dict:
            if cur_file not in dc_dict:
                continue

            dc_list = dc_dict[cur_file]
            doc_index = 0
            cur_elem = None
            next_elem = None

            for elem in itertools.chain(nondup_elm_dict[cur_file], _gen_none()):
                if cur_elem is None and next_elem is None:
                    # At startup, setup next_elem for the next iteration
                    next_elem = elem
                    # Holds as the distributor inserts a dummy element at offset -1
                    # thus it is always a non-empty list.
                    assert next_elem is not None

                    # Paranoia check, first comment should be at or after that element.
                    comment_offset = dc_list[doc_index].offset
                    assert next_elem.doc_tok
                    if comment_offset < next_elem.doc_tok.offset:
                        loc = dc_list[doc_index].get_location(comment_offset)
                        self.diag_store.add(
                            diagnostics.W300(element=None, location=loc, comments=[loc])
                        )

                    continue

                # Regular iteration
                cur_elem = next_elem
                next_elem = elem  # Might be None
                # Find the document element pointed at by 'cur_elem'.
                assert cur_elem is not None
                assert cur_elem.doc_tok is not None
                cur_doc_element = cur_elem.resolve_element(cur_elem.doc_tok.tok_text)
                if cur_doc_element is None:
                    # Element name cannot be resolved, throw an error and ignore it
                    # further.
                    offset = cur_elem.get_error_position(cur_elem.doc_tok.tok_text)
                    loc = cur_elem.doc_tok.get_location(offset)
                    name = cur_elem.doc_tok.tok_text
                    self.diag_store.add(diagnostics.W300(element=name, location=loc))

                # Process the doc comments belonging to the current element.
                while doc_index < len(dc_list):
                    comment_offset = dc_list[doc_index].offset

                    # If next comment is at or after the next element, cur_elem is done.
                    if (
                        next_elem is not None
                        and next_elem.doc_tok is not None
                        and comment_offset >= next_elem.doc_tok.offset
                    ):
                        break

                    if cur_doc_element is not None:
                        # Reported a problem about failing to resolve already, thus
                        # silently skipping is fine.
                        cur_doc_element.add_comment(dc_list[doc_index])

                    doc_index = doc_index + 1

                # If all comments have been processed, ignore the remaining elements.
                if doc_index >= len(dc_list):
                    break

            # All doc comments distributed, check that nothing ended up at a weird spot.
            for elem in self.dummy_elements:
                elem.report(self.diag_store)


def _drop_dup_dummies(gen: List[DocStore]) -> Generator[DocStore, None, None]:
    """Drop dummy elements at the same offset as a non-dummy element."""
    element = None
    for elm in gen:
        if element is None:
            element = elm
            continue

        if elm.doc_tok.offset > element.doc_tok.offset:
            yield element
            element = elm
            continue

        assert elm.doc_tok.offset == element.doc_tok.offset
        if isinstance(element, DummyElement) and elm.doc_tok.fname == element.doc_tok.fname:
            element = elm  # 'element' is not useful, 'elm' cannot be worse!
            continue

    if element is not None:
        yield element


def _gen_none() -> Generator[None, None, None]:
    """Generate a stream consisting of a single 'None' value."""
    yield None
