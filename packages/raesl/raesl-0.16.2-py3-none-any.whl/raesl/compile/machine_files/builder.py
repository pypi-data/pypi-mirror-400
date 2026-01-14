"""Code to construct line matching state machines.

The entry point to create a state machine is calling 'create' on a
StateMachineBuilder instance.

A state machine has locations and edges.

One location in a machine may have an 'initial' option denoting it is the first
location of the machine. Locations may also be accepting, denoting it is a
proper end state. The accepting option takes a name, making it possible to
distinguish which end location of the state machine was reached.

Edges start at a location and end at a location. Edges have a token-name, and
may only be chosen when the input has a token with the same name. An edge may
also have a tag option. The tag-name represents what kind of relevant token it
is. When an edge is taken with a tag-name, the token matching with the edge is
appended to a list associated with the tag-name. In this way, it is possible to
extract relevant information from the matched sentence afterwards.

State machine execution assumes the machine is deterministic. From a location,
each outgoing edge must have a different token-name. Note that a scanner may
not map unique text to a token. The latter is resolved by sorting the edges from
most specific token-name to least specific token-name.


In general, writing code to build locations and edges is bulky and hard to
understand. Instead a text format is defined to allow writing the state
machines as text, and let the computer build the state machine from the
description. The text format accepted by the builder is:

    state-machine ::=
      MACHINE-NAME ":" { loc-def | edge-def }+

    loc-def ::=
      LOC-NAME [ "initial" ] [ "accept" "=" ACCEPT-name ] ";"

    edge-def ::=
      LOC-NAME "->" LOC-NAME "[" TOKEN-NAME "]" [ "tag" "=" TAG-NAME ] ";"

Locations in 'loc-def' must not exist already. Missing locations in 'edge-def'
are silently created. Token names are defined in parsing/scanner.py.
"""

from typing import List, Optional, Tuple, Union

import sly
from raesl import logger
from raesl.compile.machine_files import typing
from raesl.compile.state_machine import Edge, Location, StateMachine
from sly import Lexer, Parser

# Pylint just hates Sly:
# pylint: disable=invalid-name, missing-docstring, no-self-use
# pylint: disable=function-redefined, unused-argument, used-before-assignment
# pylint: disable=undefined-variable, unsupported-assignment-operation
# flake8: noqa
# mypy: ignore-errors


class StateMachineLexer(Lexer):
    """Lexer for tokenizing state machine descriptions.

    Note that SLY and pylint are known not to like each other.
    """

    tokens = {
        NAME,
        ACCEPT_KW,
        INITIAL_KW,
        TAG_KW,
        COMMA_TK,
        SEMICOL_TK,
        EQ_TK,
        ARROW_TK,
        COLON_TK,
        SQ_OPEN,
        SQ_CLOSE,
    }

    ignore = " \t"
    ignore_comment = r"#.*"

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    NAME = "[A-Za-z][A-Za-z0-9_]*"
    NAME["accept"] = ACCEPT_KW
    NAME["initial"] = INITIAL_KW
    NAME["tag"] = TAG_KW

    SQ_OPEN = "\\["
    SQ_CLOSE = "\\]"
    COMMA_TK = ","
    SEMICOL_TK = ";"
    EQ_TK = "="
    COLON_TK = ":"
    ARROW_TK = "->"


class StateMachineParser(Parser):
    tokens = StateMachineLexer.tokens

    def error(self, t):
        if t is None:
            print("Unexpected EOF encountered.")
        else:
            print("Syntax error at line {}, token {}, text={}".format(t.lineno, t.type, t.value))

    @_("NAME COLON_TK mlines")
    def machine(self, p):
        return (p[0], p[2])

    @_("")
    def mlines(self, p):
        return []

    @_("mlines loc_line")
    def mlines(self, p):
        return p[0] + [p[1]]

    @_("mlines edge_line")
    def mlines(self, p):
        return p[0] + [p[1]]

    # Locations

    @_("NAME SEMICOL_TK")
    def loc_line(self, p):
        return ("loc", p[0], [])

    @_("NAME loc_options SEMICOL_TK")
    def loc_line(self, p):
        return ("loc", p[0], p[1])

    @_("loc_option")
    def loc_options(self, p):
        return [p[0]]

    @_("loc_options COMMA_TK loc_option")
    def loc_options(self, p):
        return p[0] + [p[2]]

    @_("INITIAL_KW")
    def loc_option(self, p):
        return ("initial",)

    @_("ACCEPT_KW EQ_TK NAME")
    def loc_option(self, p):
        return ("accept", p[2])

    # Edges

    @_("NAME ARROW_TK NAME SQ_OPEN NAME SQ_CLOSE SEMICOL_TK")
    def edge_line(self, p):
        return ("edge", p[0], p[2], p[4], [])

    @_("NAME ARROW_TK NAME SQ_OPEN NAME SQ_CLOSE edge_options SEMICOL_TK")
    def edge_line(self, p):
        return ("edge", p[0], p[2], p[4], p[6])

    @_("edge_option")
    def edge_options(self, p):
        return [p[0]]

    @_("edge_options COMMA_TK edge_option")
    def edge_options(self, p):
        return p[0] + [p[2]]

    @_("TAG_KW EQ_TK NAME")
    def edge_option(self, p):
        return ("tag", p[2])


class ProcessingStateMachine(StateMachine):
    """Extended StateMachine that also holds a callback function to add extracted
    parsing information into the ast.

    Arguments:
        name: Name of the state machine, also the name of the matched sequence.
        processing_func: If not None, function that inserts relevant information from
            the matched line into the ast that is constructed.
    """

    def __init__(self, name: str, processing_func: Optional[typing.ProcessingFunc] = None):
        super().__init__(name)
        self.processing_func = processing_func


class StateMachineBuilder:
    """Class for easily constructing a state machine from a textual description.

    Attributes:
        lexer: Lexer to tokenize the input text.
        parser: Parser to interpret the tokens.
        machine: State machine to be built.
        locs: Temporary location map filled while building the state machine.
    """

    def __init__(self):
        self.lexer = StateMachineLexer()
        self.parser = StateMachineParser()
        self.machine = None
        self.locs = None

    def ensure_loc(self, name: str) -> Location:
        """Make sure a location with the provided name exists. If it doesn't, create it.

        Arguments:
            name: Name of the location to ensure.

        Returns:
            The location with the provided name.
        """
        loc = self.locs.get(name)
        if loc is not None:
            return loc

        return self.create_loc(name, [])

    def create_loc(self, name: str, opts: List[Union[Tuple[str], Tuple[str, str]]]) -> Location:
        """Create a new location.

        Arguments:
            name: Name of the location to create.
            opts: Location options, list of ('initial',) and/or ('accept', str) .

        Returns:
            The created location.
        """
        initial = False
        accept = None
        for opt in opts:
            if opt[0] == "initial":
                initial = True
            elif opt[0] == "accept":
                accept = opt[1]
            else:
                assert False, "Unexpected loc option " + repr(opt)

        loc = Location(name, accept)
        assert name not in self.locs
        self.locs[name] = loc
        if initial:
            self.machine.initial_loc = loc
        return loc

    def create(
        self, machine_text: str, processing_func: Optional[typing.ProcessingFunc] = None
    ) -> ProcessingStateMachine:
        """Create a state machine by interpreting the provided state machine text.

        Arguments:
            machine_text: Description of the state machine as defined by
                StateMachineLexer and StateMachineParser.
            processing_func: Optional processing function to copy relevant
                information into the abstract syntax tree.

        Returns:
            The state machine that implements the description.
        """
        try:
            parsed = self.parser.parse(self.lexer.tokenize(machine_text))
        except sly.lex.LexError as ex:
            logger.error(f"LEX ERROR: {ex}")
            parsed = None

        # DEBUG: Dump input text with line numbers is parsing of input text fails.
        if not parsed:
            for i, line in enumerate(machine_text.split("\n")):
                logger.debug(f"{i + 1:3d}: {line}")

        assert parsed

        mname, mlines = parsed
        self.machine = ProcessingStateMachine(mname, processing_func)
        self.locs = {}

        for mline in mlines:
            if mline[0] == "loc":
                loc_name = mline[1]
                loc_opts = mline[2]
                self.create_loc(loc_name, loc_opts)

            elif mline[0] == "edge":
                edge_source = mline[1]
                edge_dest = mline[2]
                edge_toktype = mline[3]
                edge_opts = mline[4]

                source = self.ensure_loc(edge_source)
                dest = self.ensure_loc(edge_dest)
                tag = None
                for opt in edge_opts:
                    assert opt[0] == "tag"
                    tag = opt[1]
                    break

                edge = Edge(dest, edge_toktype, tag)
                source.out_edges.append(edge)

            else:
                assert False, "Unexpected machine line " + repr(mline)

        # Some sanity checks.
        assert self.machine.initial_loc  # There should be an initial location.

        self.machine.sort_edges()
        machine = self.machine
        self.machine = None
        self.locs = None
        return machine
