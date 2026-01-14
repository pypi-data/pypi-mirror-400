"""Line matcher state machines for verb and pre-position definitions."""
from typing import TYPE_CHECKING

from raesl.compile.machine_files import typing

if TYPE_CHECKING:
    from raesl.compile.typechecking.ast_builder import AstBuilder


_DEFINE_VERB_SPEC = """
define_verb:
    start initial;
    start -> s1 [DEFINE_KW] tag=define;
    s1 -> s2 [VERB_KW];

    end accept=define_verb;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def _process_define_verb(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    builder.notify_new_section(tags["define"][0], True)


_VERB_PREPOS_SPEC = """
verb_prepos:
    start initial;
    start -> s1 [NAME] tag=verb;
    s1 -> s2 [NAME] tag=prepos;

    end accept=verb_is_verb;
    s2 -> end [NL_TK];
    s2 -> end [EOF_TK];
"""


def _process_verb_def(tags: typing.TokensDict, _accept: str, builder: "AstBuilder") -> None:
    verb = tags["verb"][0]
    prepos = tags["prepos"][0]
    builder.add_verbdef(verb, prepos)


MACHINES: typing.MachineTripletList = [
    ("DEFINE_VERB_MACHINE", _DEFINE_VERB_SPEC, _process_define_verb),
    ("VERB_PREPOS_MACHINE", _VERB_PREPOS_SPEC, _process_verb_def),
]
