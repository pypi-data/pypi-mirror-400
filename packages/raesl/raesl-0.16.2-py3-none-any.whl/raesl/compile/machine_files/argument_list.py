"""Line matcher for argument lists.

Note this file is imported from other machine files rather than providing argument list
processing itself.
"""
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from raesl.compile.scanner import Token

ARGUMENT_LINE_SPEC = """
argument_line:
    start initial;
    start -> s1 [STAR_TK];
    s1 -> s2 [DOTTEDNAME] tag=argument;
    s2 -> s1 [COMMA_TK];

    end accept=argument_line;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def process_argument_list_line(tags: Dict[str, List["Token"]]) -> List["Token"]:
    """Extract the argument names from the collected tags."""
    return tags["argument"]
