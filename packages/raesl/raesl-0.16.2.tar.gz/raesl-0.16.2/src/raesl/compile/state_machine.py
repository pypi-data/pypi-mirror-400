"""State machine classes to describe an allowed sequences of tokens.

A state machine is a DFA (deterministic finite automaton, always at most one
edge that matches). An edge is associated with a matched token, locations are
decision points between tokens.

An edge may tag occurrences of tokens to simplify extraction of relevant
information for future compiler phases. A location may record matching of
a valid sequence of tokens by accepting.
"""
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from raesl.compile.scanner import get_token_priority

if TYPE_CHECKING:
    from raesl.compile.scanner import Lexer, Token


class Location:
    """Location in a state machine.

    Arguments:
        accept: Name of the rule that could be accepted at this location.
            If None, no such rule exists.
        name: Name of the location, mostly for identifying purposes.

    Attributes:
        out_edges: Outgoing edges, initially empty.
    """

    def __init__(self, name: str, accept: Optional[str] = None):
        self.accept = accept
        self.name = name
        self.out_edges: List[Edge] = []


class Edge:
    """Edge to a next location.

    Arguments:
        dest: Destination of the edge.
        tok_type: The value of the 'tok_type' attribute of a token that can trigger
            this transition.
        tag_name: If not None, the name to use for recording the transition in the
            state machine.
    """

    def __init__(self, dest: Location, tok_type: str, tag_name: Optional[str] = None):
        self.tok_type = tok_type
        self.tag_name = tag_name
        self.dest = dest
        assert isinstance(dest, Location)


class StateMachine:
    """State machine containing locations and edges.

    Note that it only stores the initial location, all other locations and edges
    are reachable from it.

    Arguments:
        name: Name of the state machine, also the name of the matched sequence.

    Attributes:
        initial_loc: Initial location of the state machine. Set after construction.
    """

    def __init__(self, name: str):
        self.name = name
        self.initial_loc: Optional[Location] = None

    def sort_edges(self):
        """Sort edges of the state machine to get specific tokens checked first."""
        done_locs = set([self.initial_loc])
        found_locs = [self.initial_loc]
        while found_locs:
            loc = found_locs.pop()
            loc.out_edges.sort(key=lambda edge: get_token_priority(edge.tok_type))
            for edge in loc.out_edges:
                if edge.dest not in done_locs:
                    done_locs.add(edge.dest)
                    found_locs.append(edge.dest)

    def dump(self, fname: Optional[str] = None):
        """Dump the state machine to a file in Graphviz format.

        Arguments:
            fname: If not None, name of the file to write, else a filename is
                constructed from the name of the state machine.
        """
        processed_locs: Set[Location] = set()
        notdone = [self.initial_loc]
        lines = ["digraph G {"]
        while notdone:
            loc = notdone.pop()
            if loc is None or loc in processed_locs:
                continue

            processed_locs.add(loc)
            if loc.accept:
                lines.append(f'    {loc.name} [shape="box"]')
            else:
                lines.append(f"    {loc.name}")

            for edge in loc.out_edges:
                lines.append(f'    {loc.name} -> {edge.dest.name} [label="{edge.tok_type}"]')
                notdone.append(edge.dest)

        lines.append("}")

        if fname is None:
            fname = self.name + ".dot"
        with open(fname, "w") as handle:
            for line in lines:
                handle.write(line)
                handle.write("\n")

    def match(self, lexer: "Lexer") -> Optional["MatchResult"]:
        """Try to match the machine against tokens from the scanner.

        Arguments:
            lexer: Token stream to match. Instance is useless afterwards, make a copy
                beforehand if you need it again.

        Returns:
            Result of the matching process.

        Note:
            This routine is currently only used for testing.
        """
        assert self.initial_loc
        current_loc: Location = self.initial_loc
        tags: Dict[str, List["Token"]] = {}

        accepted_name = None
        accepted_tags: Dict[str, List["Token"]] = {}
        accepted_lexer: Optional["Lexer"] = None

        while True:
            # Keep stepping until no progress is possible any more.
            match = self.single_step(lexer, current_loc, tags)
            if not match:
                break

            current_loc = match[0]

            # Update acceptance if necessary.
            if current_loc.accept is not None:
                accepted_name = current_loc.accept
                accepted_tags = dict((k, v.copy()) for k, v in tags.items())
                accepted_lexer = lexer.copy()

        # Done, return the result, either just the lexer at the failed state
        # for its position information, or the last accept.
        if accepted_name is None:
            return MatchResult(None, {}, lexer)

        assert accepted_lexer
        return MatchResult(accepted_name, accepted_tags, accepted_lexer)

    def single_step(
        self, lexer: "Lexer", current_loc: Location, tags: Dict[str, List["Token"]]
    ) -> Optional[Tuple["Location", "Token"]]:
        """Try to perform a single step in the state machine.

        Arguments:
            lexer: Token stream to match. Instance is modified in-place if a transition
                is taken.
            current_loc: Location to use for finding edges to try.
            tags: Collected tags so far, may be updated in-place if transition was
                performed.

        Returns:
            New location and the matching token if a transition could be performed,
            else None.
        """
        if not current_loc.out_edges:
            return None

        for edge in current_loc.out_edges:
            token = lexer.find(edge.tok_type)
            if token is None:
                continue

            # Match found. Due to being a DFA and edges being sorted on priority,
            # this is also the one and only match that we should find for this machine.
            #
            # Update tags
            if edge.tag_name is not None:
                edge_tag = tags.get(edge.tag_name)
                if edge_tag is None:
                    tags[edge.tag_name] = [token]
                else:
                    edge_tag.append(token)

            # Pass target location back to the caller.
            return edge.dest, token

        return None


class MatchResult:
    """Result data of a matching process in StateMachine.match().

    Arguments:
        accepted_name: Acceptance name from the last visited accepting location.
        accepted_tags: Collected tag data at the point of accepting.
        lexer: Lexer at the time of the last fail or at the time of the last accept
    """

    def __init__(
        self,
        accepted_name: Optional[str],
        accepted_tags: Dict[str, List["Token"]],
        lexer: "Lexer",
    ):
        self.accepted_name = accepted_name
        self.accepted_tags = accepted_tags
        self.lexer = lexer
