"""Not really tests, but sanity checks for required properties of the state machines.
(Mostly the line matcher machines, but also a few for the high level ESL_MACHINE.)
"""
from typing import TYPE_CHECKING

from raesl.compile import esl_lines, scanner

if TYPE_CHECKING:
    from raesl.compile.state_machine import Location


def collect_locations(loc: "Location"):
    """Collect locations of a state machine.

    Arguments:
        loc: First location.

    Returns:
        All reachable locations from 'loc'.
    """
    seen_locs = set([loc])
    notdone_locs = [loc]
    while notdone_locs:
        loc = notdone_locs.pop()
        for edge in loc.out_edges:
            if edge.dest not in seen_locs:
                seen_locs.add(edge.dest)
                notdone_locs.append(edge.dest)
    return seen_locs


def collect_tok_types(loc: "Location"):
    """Collect used token types of locations reachable from the given start location."""
    tok_types = set()
    for loc in collect_locations(loc):
        for edge in loc.out_edges:
            tok_types.add(edge.tok_type)

    return tok_types


def test_tokens_exist():
    """Check that tokens used in the line state machines actually exist."""
    TOKEN_NAMES = set(scanner.TOKENS.keys()) | set(["NL_TK", "EOF_TK", "epsilon"])

    bad = False
    for machine in esl_lines.get_all_line_machines():
        tok_types = collect_tok_types(machine.initial_loc)
        for tok_type in tok_types:
            if tok_type not in TOKEN_NAMES:
                msg = "Token {} is used in machine {}, but not defined in the scanner."
                print(msg.format(tok_type, machine.name))
                bad = True

    assert not bad


def test_tokens_used():
    """Check that existing tokens in the scanner are actually used."""
    available = set(scanner.TOKENS.keys()) | set(["NL_TK"])
    # 'EOF_TK' and 'epsilon' are both not explicitly used in line matchers.

    for machine in esl_lines.get_all_line_machines():
        tok_types = collect_tok_types(machine.initial_loc)
        available.difference_update(tok_types)

    assert not available


def test_final_accept():
    """Check that an accepting state is also the final state, no further tokens are
    allowed.
    """
    bad = False
    for machine in esl_lines.get_all_line_machines():
        for loc in collect_locations(machine.initial_loc):
            if loc.accept:
                if loc.out_edges:
                    msg = "Accepting location {} in machine {} has outgoing edges."
                    print(msg.format(loc.name, machine.name))
                    bad = True

    assert not bad


def test_accept_final():
    """Check that a final state (no outgoing edges) is also an accepting state."""
    bad = False
    for machine in esl_lines.get_all_line_machines():
        for loc in collect_locations(machine.initial_loc):
            if not loc.out_edges:
                if not loc.accept:
                    msg = (
                        "Deadlock location {} in machine {}: not accepting and "
                        "no outgoing edges."
                    )
                    print(msg.format(loc.name, machine.name))
                    bad = True

    assert not bad


def test_dfa():
    """Check that the line machines are deterministic with respect to tokens."""
    bad = False
    for machine in esl_lines.get_all_line_machines():
        for loc in collect_locations(machine.initial_loc):
            tok_types = set(edge.tok_type for edge in loc.out_edges)
            if len(tok_types) != len(loc.out_edges):
                msg = "Location {} in machine {} is not deterministic."
                print(msg.format(loc.name, machine.name))
                bad = True

    assert not bad


def test_esl_lang_machine():
    """Check that the language state machine only uses tokens representing line
    machines or 'epsilon'.
    """
    bad = False
    line_machine_names = esl_lines.get_line_machine_names()
    for loc in collect_locations(esl_lines.ESL_MACHINE.initial_loc):
        for edge in loc.out_edges:
            if edge.tok_type == "epsilon":
                continue
            if edge.tok_type in line_machine_names:
                continue

            msg = "Location {} in the ESL language machine uses invalid token {}."
            print(msg.format(loc.name, edge.tok_type))
            bad = True

    assert not bad


def test_esl_lang_no_deadlock():
    """Check that the final state (no outgoing edges) is an accepting state."""
    bad = False
    machine = esl_lines.ESL_MACHINE
    for loc in collect_locations(machine.initial_loc):
        if not loc.out_edges:
            if not loc.accept:
                msg = (
                    "Deadlock location '{}' in machine '{}': not accepting and "
                    "no outgoing edges."
                )
                print(msg.format(loc.name, machine.name))
                bad = True

    assert not bad
