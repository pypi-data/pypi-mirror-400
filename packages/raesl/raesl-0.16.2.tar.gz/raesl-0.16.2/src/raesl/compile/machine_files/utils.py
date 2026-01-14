"""Utility functions."""
from typing import Dict, List, Optional

from raesl.compile.scanner import Token


def make_loc_names(prefix: str, name: str, count: int) -> Dict[str, str]:
    """Make a dict with 'count' names by combining the prefix, name, and a number."""
    return dict((name + str(num), prefix + name + str(num)) for num in range(1, count + 1))


def _in_range(tok: Token, start_offset: Optional[int], end_offset: Optional[int]) -> bool:
    """Is the given token offset positioned between and not at 'start_offset' and
    'end_offset'? If start_offset or end_offset is None, use -1 and infinity as offsets,
    respectively.

    Returns:
        Whether the provided token is between (not at) the start_offset and end_offset.
    """
    if start_offset is not None and tok.offset <= start_offset:
        return False
    if end_offset is not None and tok.offset >= end_offset:
        return False
    return True


def get_one(tokens: List[Token], start_offset: Optional[int], end_offset: Optional[int]) -> Token:
    """Filter tokens on the provided start and end offsets, and return the only token
    between the positions.
    """
    matches = [tok for tok in tokens if _in_range(tok, start_offset, end_offset)]
    assert len(matches) == 1
    return matches[0]


def get_optional(
    tokens: List[Token], start_offset: Optional[int], end_offset: Optional[int]
) -> Optional[Token]:
    """Filter tokens on the provided start and end offsets, and return the only token
    between the positions.
    """
    matches = [tok for tok in tokens if _in_range(tok, start_offset, end_offset)]
    assert len(matches) < 2
    if matches:
        return matches[0]
    return None
