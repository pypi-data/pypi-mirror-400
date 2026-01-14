"""Parsing the Elephant Specification Language."""

from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple

from raesl import logger
from raesl.compile import diagnostics, esl_lines
from raesl.compile.scanner import get_token_priority
from raesl.compile.typechecking import ast_builder

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.machine_files.builder import ProcessingStateMachine
    from raesl.compile.scanner import Lexer, Token
    from raesl.compile.state_machine import Location


class LineMachineStepper:
    """Class managing parsing of a line in ESL.

    Arguments:
        machine: Line matching machine to use for recognizing the line.
        lexer: Lexer to use in the matching process.
        dest_loc: New specification location if a match was found.

    Attributes:
        current_loc: Current location in the line machine.
        tags: Relevant data extracted from the text line during the parsing process.
        matched_tokens: Tokens used for matching the line thus far.
    """

    def __init__(self, machine: "ProcessingStateMachine", lexer: "Lexer", dest_loc: "Location"):
        self.machine = machine
        self.lexer = lexer
        self.current_loc: Optional["Location"] = machine.initial_loc
        self.tags: Dict[str, List["Token"]] = {}
        self.matched_tokens: List["Token"] = []

        self.dest_loc = dest_loc

    def try_step(self) -> bool:
        """Try to match the next token.

        Returns:
            Whether progress was made.
        """
        if not self.current_loc:
            return False

        match = self.machine.single_step(self.lexer, self.current_loc, self.tags)
        if not match:
            self.current_loc = None
            return False

        self.current_loc = match[0]
        self.matched_tokens.append(match[1])
        return True

    def is_accepting(self) -> bool:
        """Is the machine in an accepting location?"""
        assert self.current_loc
        return self.current_loc.accept is not None

    def get_accept_name(self) -> str:
        """Get the acceptance name associated with the accepting location.

        Returns:
            Name of the accepted 'rule'.
        """
        assert self.current_loc
        assert self.current_loc.accept is not None
        return self.current_loc.accept


def parse_line(
    spec_state: "Location",
    lexer: "Lexer",
    builder: ast_builder.AstBuilder,
    diag_store: diagnostics.DiagnosticStore,
) -> Tuple[Optional["Location"], Optional["Lexer"]]:
    """Parse a text-line in ESL.

    For debugging line selection, set scanner.PARSER_DEBUG to True, which enables
    printing debug information to the std output. For best results, use a *small*
    input specification, output is quite verbose.

    Arguments:
        spec_state: Location in the ESL language state machine.
        lexer: Lexer pointing at the start of the next line to match.
        builder: Class storing extracted parse data.
        diag_store: Storage for reported diagnostics.

    Returns:
        Next state in the ESL state machine unless successfully finished, next lexer to
        use if next step can be performed.
    """
    reachable_locs = collect_locations(spec_state)
    logger.debug(f"** line {lexer.line_num + 1} (1-based) *************************")
    rloc_names = ",".join(rl.name for rl in reachable_locs)
    logger.debug(f"** parse_line({spec_state.name} -> [{rloc_names}])")

    # Skip over empty lines.
    while lexer.find("NL_TK"):
        continue

    # Check for EOF.
    if lexer.find("EOF_TK"):
        if any(loc.accept for loc in reachable_locs):
            return None, lexer  # Reached EOF at an accepting state, success!

        # EOF but not expecting it, report a problem.
        diag_store.add(diagnostics.E100(lexer.get_location()))
        return spec_state, None

    # Found a line of text. Find a match.
    #
    # Create line steppers for all possible matches.
    steppers = []
    for spec_loc in reachable_locs:
        for edge in spec_loc.out_edges:
            if edge.tok_type == "epsilon":
                continue

            machine = esl_lines.get_line_machine(edge.tok_type)
            logger.debug(f"** Add '{machine.name}' line machine.")
            steppers.append(LineMachineStepper(machine, lexer.copy(), edge.dest))

    assert steppers  # There should be at least one stepper.

    # Take steps, silently dropping steppers that don't match, until all don't match or
    # at least one stepper is accepting.
    acceptors = []
    while steppers:
        prev_steppers = steppers
        steppers = []
        logger.debug("** -----")
        steppers_text = ", ".join(s.machine.name for s in prev_steppers)
        logger.debug(f"** Steppers remaining: {steppers_text}")
        for stepper in prev_steppers:
            if not stepper.try_step():
                logger.debug(f"** Stepper {stepper.machine.name} didn't match.")
                continue  # Next token didn't match, drop the stepper silently.
            if stepper.is_accepting():
                # Stepper has reached the end, continue with the others.
                logger.debug(f"** Stepper {stepper.machine.name} has reached the end.")
                acceptors.append(stepper)
                continue

            logger.debug(f"** Stepper {stepper.machine.name} matched.")

            steppers.append(stepper)

    # All steppers either failed or finished in an accepting location.
    best_acceptor: Optional[LineMachineStepper]
    if acceptors:
        if len(acceptors) == 1:
            # Life is simple, pick the one and only match.
            best_acceptor = acceptors[0]
        else:
            # Multiple lines match. Filter on the most specific match.
            best_match = None
            best_acceptor = None
            for acceptor in acceptors:
                match_prio = [get_token_priority(tok.tok_type) for tok in acceptor.matched_tokens]
                if best_match is None or match_prio < best_match:
                    best_match = match_prio
                    best_acceptor = acceptor
                elif best_acceptor is not None and match_prio == best_match:
                    ambi_acceptors = (
                        best_acceptor.get_accept_name(),
                        acceptor.get_accept_name(),
                    )
                    best_acceptor = None  # Ambiguous best match (until now)

            # Sanity check and raise an Exception if it fails.
            if best_acceptor is None:
                diag_store.add(diagnostics.E101(ambi_acceptors, location=lexer.get_location()))

        # Store information of the line into the ast builder instance.
        assert best_acceptor is not None
        processing_func = best_acceptor.machine.processing_func
        if processing_func:
            tags = best_acceptor.tags
            accept = best_acceptor.get_accept_name()
            processing_func(tags, accept, builder)

        # Line done.
        return best_acceptor.dest_loc, best_acceptor.lexer

    # No acceptors, thus they all failed to match. Find a stepper that got the furthest.
    # mypy fails on lambdas
    # best_stepper = max(prev_steppers, key=lambda s: s.lexer.get_linecol())
    def linecol_value(line_stepper: LineMachineStepper) -> Tuple[int, int]:
        return line_stepper.lexer.get_linecol()

    # Report a syntax error
    best_stepper = max(prev_steppers, key=linecol_value)
    diag_store.add(diagnostics.E102(location=best_stepper.lexer.get_location()))

    return spec_state, None


def parse_lexer(
    lexer: "Lexer",
    diag_store: Optional[diagnostics.DiagnosticStore],
    builder: Optional[ast_builder.AstBuilder],
    doc_comments: Optional[List["Token"]],
) -> Tuple[diagnostics.DiagnosticStore, ast_builder.AstBuilder, List["Token"], bool]:
    """Parse an ESL lexer, storing collected information in the builder.

    Arguments:
        lexer: Lexer pointing at the start of the specification text.
        diag_store: Diagnostic store if one already has been created.
        builder: Builder if one already has been created.
        doc_comments: Doc comments if any have been found yet.

    Returns:
        Diagnostic store instance.
        Builder instance.
        Found doc comments.
        Whether there has been an error.
    """
    diag_store = diagnostics.DiagnosticStore() if diag_store is None else diag_store
    builder = ast_builder.AstBuilder(diag_store) if builder is None else builder
    doc_comments = [] if doc_comments is None else doc_comments

    assert esl_lines.ESL_MACHINE.initial_loc is not None
    spec_state: Location = esl_lines.ESL_MACHINE.initial_loc
    while True:
        new_spec_state, new_lexer = parse_line(spec_state, lexer, builder, diag_store)
        if new_lexer is None:
            # Something bad happened, message should be in problem storage.
            doc_comments.extend(lexer.doc_comments)
            return diag_store, builder, doc_comments, True

        if new_spec_state is None:
            # EOF reached in an accepting state, done!
            # Check the collected data and construct an AST, return the found
            # diagnostics and the created specification if possible.
            doc_comments.extend(lexer.doc_comments)
            return diag_store, builder, doc_comments, False

        # Else, matched one line, do the next.
        spec_state = new_spec_state
        lexer = new_lexer


def parse_spec(
    lexers: Iterable["Lexer"], diag_store: Optional[diagnostics.DiagnosticStore] = None
) -> Tuple[diagnostics.DiagnosticStore, Optional["Specification"]]:
    """Parse an ESL specification, storing collected information in the builder.

    Arguments:
        lexers: Lexers pointing at the start of their respective texts (e.g. per-file).

    Returns:
        The found diagnostics, and if successful, the type-checked output.
    """
    diag_store = diagnostics.DiagnosticStore() if diag_store is None else diag_store
    builder = ast_builder.AstBuilder(diag_store)
    doc_comments: List["Token"] = []

    for lexer in lexers:
        diag_store, builder, doc_comments, error = parse_lexer(
            lexer, diag_store, builder, doc_comments
        )
        if error:
            return diag_store, None

    spec = builder.finish_parse(doc_comments)
    return diag_store, spec


def collect_locations(spec_state: "Location") -> List["Location"]:
    """Collect the set reachable states from 'spec_state' without taking only 'epsilon'
    transitions.
    """
    reachables = [spec_state]
    notdone = [spec_state]
    while notdone:
        spec_loc = notdone.pop()
        for edge in spec_loc.out_edges:
            if edge.tok_type == "epsilon":
                new_loc = edge.dest
                if (
                    new_loc not in reachables
                ):  # Assuming a msall number of location in 'reachables'.
                    reachables.append(new_loc)
                    notdone.append(new_loc)
    return reachables
