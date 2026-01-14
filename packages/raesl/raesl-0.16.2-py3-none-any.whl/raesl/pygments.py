"""ESL Pygments Lexer module.

A Pygments Lexer for the Elephant Specification Language (ESL). Mainly used for syntax
highlighting in generated documentation using Sphinx.
"""

from pygments.lexer import RegexLexer, include, words
from pygments.token import Comment, Keyword, Name, Text, Whitespace

H = r"([ \t]+)"
CON = r"(?=([ \t]*\.\.\.))"
EOT = r"(?=((\.)|(\s)|(#)))"
SOT = r"((^)|(?<=((\.)|(\s))))"
EOL = r"(?!([ \t]*\.\.\.))(?=([ \t]*($|#)))"
BOL = r"([ \t]*)"

keywords = [
    "world",
    "empty",
    "define",
    "is",
    "be",
    "a",
    "an",
    "with",
    "argument",
    "arguments",
    "goal-requirement",
    "goal-requirements",
    "transformation-requirement",
    "transformation-requirements",
    "design-requirement",
    "design-requirements",
    "behavior-requirement",
    "behavior-requirements",
    "goal-constraint",
    "goal-constraints",
    "transformation-constraint",
    "transformation-constraints",
    "design-constraint",
    "design-constraints",
    "behavior-constraint",
    "behavior-constraints",
    "need",
    "needs",
    "subclause",
    "subclauses",
    "verb",
    "verbs",
    "type",
    "types",
    "component",
    "components",
    "relation",
    "relations",
    "variable",
    "variables",
    "parameter",
    "parameters",
    "comment",
    "comments",
    "shall",
    "must",
    "could",
    "should",
    "won't",
    "or",
    "and",
    "not",
    "equal to",
    "greater than",
    "smaller than",
    "at least",
    "at most",
    "approximately",
    "maximized",
    "minimized",
    ",",
    "end",
    "case",
    "when",
    "then",
    "no other case applies",
    "does",
    "unit",
    "units",
    "requiring",
    "relating",
    "returning",
    "one or more",
    "t.b.d.",
    "bundle of",
    "group of",
    "variable-group",
    "variable-groups",
    "enumeration of",
    "property",
]


class EslLexer(RegexLexer):
    """Elephant Specification Language Lexer."""

    name = "Elephant Specification Language"
    aliases = ["esl", "elephant"]
    filenames = [".esl"]
    tokens = {
        "comments": [(r"#.*\n", Comment)],
        "root": [
            include("comments"),
            (r"\s+", Whitespace),
            (words(keywords, prefix=SOT, suffix=EOT), Keyword.Reserved),
            (r"\.\.\.", Keyword.Reserved),
            (r"[\w-]+", Name),  # Skip current word.
            (r".", Text),  # Skip any character if everything else fails.
        ],
    }
