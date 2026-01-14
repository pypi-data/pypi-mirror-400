"""Lexer for on-demand recognition of tokens.

As the language has unrestrained text in its needs, lexing beforehand is not
going to work in all cases. Instead, the scanner tries to match tokens on demand.

Also there is overlap in matching between tokens (a NONSPACE expression matches
almost all other tokens as well, and a NAME expression matches all keywords).
The rule applied here (by means of sorting edges in the state machines) is that
specific wins from generic. For example, if at some point both the OR_KW and
the NONSPACE token may be used, and the text is "or", the OR_KW token is chosen.
"""
import re
from functools import partial
from typing import Dict, List, Optional, Pattern, Tuple

from raesl import logger, utils
from raesl.types import Location

# Whitespace matching RE.
SPACE_RE = re.compile("[ \\t\\r]+")

# A letter, followed by letters, digits or dashes, where it may not end with a dash.
_FIRST_NAME_PAT = "[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*"
# Like _FIRST_NAME_PAT, but allow both letters and digits as first character.
_OTHER_NAME_PAT = "[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*"
# A _FIRST_NAME_PAT followed by zero or more _OTHER_NAME_PAT, separated by dots.
_DOTTED_NAME_PAT = _FIRST_NAME_PAT + "(?:\\." + _OTHER_NAME_PAT + ")*"
# Characters that should not appear after most tokens (they should be part of them).
_KWORD_AVOID_PAT = "(?![-_A-Za-z0-9])"
# Characters that should not appear after names (it is less restrictive than
# _KWORD_AVOID_PAT).
_NAME_AVOID_PAT = "(?![A-Za-z0-9])"


# Helper method to reduce clutter.
comp = partial(re.compile, flags=re.IGNORECASE)

TOKENS: Dict[str, Pattern] = {
    "A_KW": comp("an?" + _KWORD_AVOID_PAT),
    "AND_KW": comp("and" + _KWORD_AVOID_PAT),
    "APPLIES_KW": comp("applies" + _KWORD_AVOID_PAT),
    "APPROXIMATELY_KW": comp("approximately" + _KWORD_AVOID_PAT),
    "ARGUMENT_KW": comp("arguments?" + _KWORD_AVOID_PAT),
    "AT_KW": comp("at" + _KWORD_AVOID_PAT),
    "BE_KW": comp("be" + _KWORD_AVOID_PAT),
    "BEHAVIOR_CONSTRAINT_KW": comp("behavior-constraints?" + _KWORD_AVOID_PAT),
    "BEHAVIOR_REQUIREMENT_KW": comp("behavior-requirements?" + _KWORD_AVOID_PAT),
    "BUNDLE_KW": comp("bundle" + _KWORD_AVOID_PAT),
    "CASE_KW": comp("case" + _KWORD_AVOID_PAT),
    "COLON_TK": comp(":"),
    "COMMA_TK": comp(","),
    "COMMENT_KW": comp("comments?" + _KWORD_AVOID_PAT),
    "COMPONENT_KW": comp("components?" + _KWORD_AVOID_PAT),
    "COULD_KW": comp("could" + _KWORD_AVOID_PAT),
    "DEFINE_KW": comp("define" + _KWORD_AVOID_PAT),
    "DESIGN_CONSTRAINT_KW": comp("design-constraints?" + _KWORD_AVOID_PAT),
    "DESIGN_REQUIREMENT_KW": comp("design-requirements?" + _KWORD_AVOID_PAT),
    "DOES_KW": comp("does" + _KWORD_AVOID_PAT),
    "EMPTY_KW": comp("empty" + _KWORD_AVOID_PAT),
    "ENUMERATION_KW": comp("enumeration" + _KWORD_AVOID_PAT),
    "EQUAL_KW": comp("equal" + _KWORD_AVOID_PAT),
    "GOAL_CONSTRAINT_KW": comp("goal-constraints?" + _KWORD_AVOID_PAT),
    "GOAL_REQUIREMENT_KW": comp("goal-requirements?" + _KWORD_AVOID_PAT),
    "GREATER_KW": comp("greater" + _KWORD_AVOID_PAT),
    "GROUP_KW": comp("group" + _KWORD_AVOID_PAT),
    "IS_KW": comp("(?:is|are)" + _KWORD_AVOID_PAT),
    "LEAST_KW": comp("least" + _KWORD_AVOID_PAT),
    "MAXIMIZED_KW": comp("maximized" + _KWORD_AVOID_PAT),
    "MINIMIZED_KW": comp("minimized" + _KWORD_AVOID_PAT),
    "MORE_KW": comp("more" + _KWORD_AVOID_PAT),
    "MOST_KW": comp("most" + _KWORD_AVOID_PAT),
    "MUST_KW": comp("must" + _KWORD_AVOID_PAT),
    "NEED_KW": comp("needs?" + _KWORD_AVOID_PAT),
    "NO_KW": comp("no" + _KWORD_AVOID_PAT),
    "NOT_KW": comp("not" + _KWORD_AVOID_PAT),
    "OF_KW": comp("of" + _KWORD_AVOID_PAT),
    "ONE_KW": comp("one" + _KWORD_AVOID_PAT),
    "OR_KW": comp("or" + _KWORD_AVOID_PAT),
    "OTHER_KW": comp("other" + _KWORD_AVOID_PAT),
    "PARAMETER_KW": comp("parameters?" + _KWORD_AVOID_PAT),
    "PROPERTY_KW": comp("property" + _KWORD_AVOID_PAT),
    "RELATION_KW": comp("relations?" + _KWORD_AVOID_PAT),
    "RELATING_KW": comp("relating" + _KWORD_AVOID_PAT),
    "REQUIRING_KW": comp("requiring" + _KWORD_AVOID_PAT),
    "RETURNING_KW": comp("returning" + _KWORD_AVOID_PAT),
    "SHALL_KW": comp("shall" + _KWORD_AVOID_PAT),
    "SHOULD_KW": comp("should" + _KWORD_AVOID_PAT),
    "SMALLER_KW": comp("smaller" + _KWORD_AVOID_PAT),
    "STAR_TK": comp("\\*"),
    "SUB_CLAUSES_KW": comp("subclauses?" + _KWORD_AVOID_PAT),
    "THAN_KW": comp("than" + _KWORD_AVOID_PAT),
    "THEN_KW": comp("then" + _KWORD_AVOID_PAT),
    "TO_KW": comp("to" + _KWORD_AVOID_PAT),
    "TRANSFORM_CONSTRAINT_KW": comp("transformation-constraints?" + _KWORD_AVOID_PAT),
    "TRANSFORM_REQUIREMENT_KW": comp("transformation-requirements?" + _KWORD_AVOID_PAT),
    "TYPE_KW": comp("types?" + _KWORD_AVOID_PAT),
    "UNIT_KW": comp("units?" + _KWORD_AVOID_PAT),
    "VARIABLE_KW": comp("variables?" + _KWORD_AVOID_PAT),
    "VARIABLE_GROUP_KW": comp("variable-groups?" + _KWORD_AVOID_PAT),
    "VERB_KW": comp("verbs?" + _KWORD_AVOID_PAT),
    "WHEN_KW": comp("when" + _KWORD_AVOID_PAT),
    "WITH_KW": comp("with" + _KWORD_AVOID_PAT),
    "WONT_KW": comp("won'?t" + _KWORD_AVOID_PAT),
    "WORLD_KW": comp("world" + _KWORD_AVOID_PAT),
    "NAME": comp(_FIRST_NAME_PAT + _NAME_AVOID_PAT),
    "DOTTEDNAME": comp(_DOTTED_NAME_PAT + _NAME_AVOID_PAT),
    "NONCOMMA": comp("[^, \\t\\r\\n]+(?:,+[^, \\t\\r\\n]+)*"),
    "NONSPACE": comp("[^ \\t\\r\\n]+"),
    # NL_TK is a special case
    # EOF_TK is a special case
    # DOC_COMMENT_TK is used to store documentation comments internally.
}


def get_token_priority(tok_type: str) -> int:
    """Priority of the tokens. Higher value is less specific.

    Arguments:
        tok_type: Name of the token type.

    Returns:
        Priority of the token.
    """
    tok_prios = {"NONSPACE": 4, "NONCOMMA": 3, "NAME": 2, "DOTTEDNAME": 2, "epsilon": 0}
    return tok_prios.get(tok_type, 1)  # Default priority is 1


class Token:
    """Data of a matched token.

    Arguments:
        tok_type: Type name of the token.
        tok_text: Text of the token.
        fname: Name of the file containing the text.
        offset: Offset of the current position in the input text.
        line_offset: Offset of the first character of the current line in the input
            text.
        line_num: Line number of the current line.
    """

    def __init__(
        self,
        tok_type: str,
        tok_text: str,
        fname: Optional[str],
        offset: int,
        line_offset: int,
        line_num: int,
    ):
        self.tok_type = tok_type
        self.tok_text = tok_text
        self.fname = fname
        self.offset = offset
        self.line_offset = line_offset
        self.line_num = line_num

    def get_location(self, offset: int = 0) -> Location:
        """Get this token's Location."""
        fname = self.fname if self.fname is not None else "unknown-file"

        if offset < 0:
            offset = 0
        elif offset >= len(self.tok_text):
            offset = len(self.tok_text)

        line, col = self.line_num, self.offset - self.line_offset
        return utils.get_location(
            uri=fname,
            start_line=line,
            start_character=col,
            end_line=line,
            end_character=col + offset,
        )

    def __str__(self) -> str:
        return 'Token["{}", {}]'.format(self.tok_type, repr(self.tok_text))


class Lexer:
    """On-demand scanner.

    For debugging token matching, enable the PARSER_DEBUG flag near the top
    of the file. That also enables debug output in the parser.parse_line to
    understand what line is being tried, and which line match steppers are
    running.

    Arguments;
        fname: Name of the file containing the text, may be None.
        text: Input text.
        length: Length of the text.
        offset: Offset of the current position in the text.
        line_offset: Offset of the first character of the current line in the input
            text.
        line_num: Line number of the current line.
        doc_comments: Documentation comments found so far, shared between all scanners.
    """

    def __init__(
        self,
        fname: Optional[str],
        text: str,
        offset: int,
        line_offset: int,
        line_num: int,
        doc_comments: List[Token],
    ):
        self.fname = fname
        self.text = text
        self.length = len(text)
        self.offset = offset
        self.line_offset = line_offset
        self.line_num = line_num
        self.doc_comments = doc_comments

    def copy(self) -> "Lexer":
        """Make copy of self. New scanner at the same position as self."""
        return Lexer(
            self.fname,
            self.text,
            self.offset,
            self.line_offset,
            self.line_num,
            self.doc_comments,
        )

    def get_location(self) -> Location:
        """Get location information of the next token. Note that such a position may be
        at an unexpected place since new-lines are significant. For example, it may be
        at the end of a comment.

        Returns:
            Location information of the next token.
        """
        fname = self.fname if self.fname is not None else "unknown-file"
        line, col = self.get_linecol()
        return utils.get_location(uri=fname, start_line=line, start_character=col)

    def get_linecol(self) -> Tuple[int, int]:
        """Get line and column information of the next token. Note that as new-lines
        are significant, such a position may be at an unexpected place, for example at
        the end of a comment.

        Returns:
            Line and column information of the next token.
        """
        return self.line_num, self.offset - self.line_offset

    def find(self, tok_type: str) -> Optional[Token]:
        """Try to find the requested token.

        Arguments:
            tok_type: Type name of the token.

        Returns:
            Found token, or None.
        """
        self.skip_white()
        pat = TOKENS.get(tok_type)
        if pat:
            match = pat.match(self.text, self.offset)
            if not match:
                logger.debug("Lexer failed {}".format(tok_type))
                return None

            tok = Token(
                tok_type,
                match[0],
                self.fname,
                self.offset,
                self.line_offset,
                self.line_num,
            )
            self.offset = match.end()
            logger.debug("Lexer matched {}".format(tok))
            return tok

        elif tok_type == "NL_TK":
            if self.offset < self.length and self.text[self.offset] == "\n":
                tok = Token(
                    tok_type,
                    "\n",
                    self.fname,
                    self.offset,
                    self.line_offset,
                    self.line_num,
                )
                self.offset = self.offset + 1
                self.line_offset = self.offset
                self.line_num = self.line_num + 1
                logger.debug("Lexer matched {}".format(tok))
                return tok

            logger.debug("Lexer failed {}".format(tok_type))
            return None

        else:
            assert tok_type == "EOF_TK", "Found unrecognized token {}.".format(tok_type)
            if self.offset >= self.length:
                tok = Token(
                    tok_type,
                    "",
                    self.fname,
                    self.length,
                    self.line_offset,
                    self.line_num,
                )
                logger.debug("Lexer matched {}".format(tok))
                return tok

            logger.debug("Lexer failed {}".format(tok_type))
            return None

    def skip_white(self):
        """Skip white space, triple dots, newlines, and comments. Implements the
        following Graphviz diagram:

        digraph white {
            1 -> 1 [label="spc+"]
            1 -> 99 [label="eof"]
            1 -> 4 [label="#.*"]
            1 -> 5 [label="..."]
            1 -> 99 [label="other"]

            4 -> 99 [label="eof"]
            4 -> 99 [label="nl"]

            5 -> 5 [label="spc+"]
            5 -> 99 [label="eof"]
            5 -> 1 [label="nl"]
            5 -> 6 [label="#.*"]
            5 -> REV [label="..."]
            5 -> REV [label="other"]

            6 -> 99 [label="eof"]
            6 -> 1 [label="nl"]
        }

        Jump to non-99 location eats the recognized text, REV means the
        last found "..." was a false positive and must be reverted to just
        before that position.

        Note that \n is a significant token, so it is not skipped everywhere.
        """
        while True:
            # 1:
            match = SPACE_RE.match(self.text, self.offset)
            if match:
                self.offset = match.end(0)

            if self.offset >= self.length:
                return

            if self.text[self.offset] == "#":
                # 4, starting with matching ".*":
                i = self.text.find("\n", self.offset + 1)
                self._save_doc_comment(self.offset, i)
                if i < 0:
                    self.offset = self.length
                    return
                else:
                    self.offset = i  # A '\n' is needed to end the current line in the parser!
                    return

            if self.text.startswith("...", self.offset):
                # 5:
                # Switch to using 'tmp_offset' as the offset, as we may have
                # to revert skipping ... .
                tmp_offset = self.offset + 3
                match = SPACE_RE.match(self.text, tmp_offset)
                if match:
                    tmp_offset = match.end(0)

                if tmp_offset >= self.length:
                    self.offset = self.length
                    return

                char = self.text[tmp_offset]
                if char == "\n":  # "... \n" found
                    self.offset = tmp_offset + 1
                    self.line_offset = self.offset
                    self.line_num = self.line_num + 1
                    continue

                if char == "#":  # "... #.*\n" found?
                    # 6, starting with matching ".*":
                    i = self.text.find("\n", tmp_offset + 1)
                    self._save_doc_comment(tmp_offset, i)
                    if i < 0:
                        self.offset = self.length
                        return
                    else:
                        self.offset = i + 1
                        self.line_offset = self.offset
                        self.line_num = self.line_num + 1
                        continue

                # Continuation of 5.
                # Found more text, '...' was a false positive, don't skip it.
                return

            # Continuation of 1, 'other' case
            return

    def _save_doc_comment(self, hash_char_offset: int, nl_offset: int):
        """Inspect a comment and rescue doc-comments.

        Arguments:
            hash_char_offset: Offset of the '#' character in the text.
            nl_offset: Offset of the next '\n' in the text, negative value means
                no '\n' was found.
        """
        if nl_offset < 0:
            nl_offset = self.length

        if hash_char_offset + 1 >= nl_offset:
            # Was '#\n' or '#<EOF>', definitely not a '#<'
            return

        if self.text[hash_char_offset + 1] != "<":
            return  # Normal comment, don't save.

        if self.doc_comments and self.doc_comments[-1].offset >= hash_char_offset:
            # Several scanners may run in parallel, so it is feasible that the same
            # doc comment is found several times. Skip this comment if it has been
            # seen before.
            return

        comment_text = self.text[hash_char_offset:nl_offset]
        if not comment_text[2:].strip():
            return  # '#<' was empty or just white-space.

        doc_tok = Token(
            "DOC_COMMENT_TK",
            comment_text,
            self.fname,
            hash_char_offset,
            self.line_offset,
            self.line_num,
        )
        self.doc_comments.append(doc_tok)
