"""Some general types, inspired by the Language Server Protocol.

Reference:
    https://microsoft.github.io/language-server-protocol/
"""
import enum
from pathlib import Path
from typing import List, Tuple


class Position:
    """Position in a text document expressed as zero-based line and character offset.

    A position is between two characters like an 'insert' cursor in an editor. Special
    values like for example -1 to denote the end of a line are not supported.

    Arguments:
        line: Line position in a document (zero-based).
        character: Character offset on a line in a document (zero-based). Assuming that
            the line is represented as a string, the 'character' value represents the
            gap between 'character' and 'character + 1'.
    """

    def __init__(self, line: int = 0, character: int = 0):
        self.line = line
        self.character = character

    def __eq__(self, other):
        return (
            isinstance(other, Position)
            and self.line == other.line
            and self.character == other.character
        )

    def __ge__(self, other):
        line_gt = self.line > other.line

        if line_gt:
            return line_gt

        if self.line == other.line:
            return self.character >= other.character

        return False

    def __gt__(self, other):
        line_gt = self.line > other.line

        if line_gt:
            return line_gt

        if self.line == other.line:
            return self.character > other.character

        return False

    def __le__(self, other):
        line_lt = self.line < other.line

        if line_lt:
            return line_lt

        if self.line == other.line:
            return self.character <= other.character

        return False

    def __lt__(self, other):
        line_lt = self.line < other.line

        if line_lt:
            return line_lt

        if self.line == other.line:
            return self.character < other.character

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.line, self.character))

    def __iter__(self):
        return iter((self.line, self.character))

    def __repr__(self):
        # Debug/internal: 0-based.
        return f"{self.line}:{self.character}"

    def __str__(self):
        # Display: 1-based.
        return f"{self.line + 1}:{self.character + 1}"


class Range:
    """A range in a text document expressed as (zero-based) start and end positions.

    A range is comparable to a selection in an editor. Therefore the end position is
    exclusive. If you want to specify a range that contains a line including the ending
    character(s) then use an end position denoting the start of the next line.

    Arguments:
        start: The range's start position.
        end: The range's end position.
    """

    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return isinstance(other, Range) and self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash((self.start, self.end))

    def __iter__(self):
        return iter((self.start, self.end))

    def __repr__(self):
        # Debug/internal: 0-based.
        return f"{repr(self.start)}-{repr(self.end)}"

    def __str__(self):
        # Display: 1-based.
        return f"{str(self.start)}-{str(self.end)}"


class Location:
    """Represents a location inside a resource. Such as a line inside a text file.

    Arguments:
        uri: URI of this location.
        range: Range of this location.
    """

    def __init__(self, uri: str, range: Range):
        self.uri = uri
        self.range = range

    def get_key(self) -> Tuple[str, int, int]:
        """Get a tuple with identification for this position."""
        return self.uri, self.range.start.line, self.range.start.character

    def __eq__(self, other):
        return isinstance(other, Location) and self.uri == other.uri and self.range == other.range

    def __lt__(self, other: "Location"):
        return self.get_key() < other.get_key()

    def __le__(self, other: "Location"):
        return self.get_key() <= other.get_key()

    def __gt__(self, other: "Location"):
        return self.get_key() > other.get_key()

    def __ge__(self, other: "Location"):
        return self.get_key() >= other.get_key()

    def __repr__(self):
        # Debug/internal: 0-based.
        return f"{Path(self.uri).as_posix()}:{repr(self.range)}"

    def __str__(self):
        # Display: 1-based.
        return f"{Path(self.uri).as_posix()}:{str(self.range)}"


class DiagnosticSeverity(enum.IntEnum):
    Error = 1  # Reports an error.
    Warning = 2  # Reports a warning.
    Information = 3  # Reports an information.
    Hint = 4  # Reports a hint.


class DiagnosticRelatedInformation:
    """Represents a related message and source code location for a diagnostic.

    This should be used to point to code locations that cause or are related to a
    diagnostic, e.g when duplicating a symbol in a scope.

    Arguments:
        location: The location of this related diagnostic information.
        message: The message of this related diagnostic information.
    """

    def __init__(self, location: Location, message: str):
        self.location = location
        self.message = message

    def __repr__(self):
        return f"{self.message} at {repr(self.location)}"

    def __str__(self):
        return f"{self.message} at {str(self.location)}"


class Diagnostic:
    """Represents a diagnostic, such as a compiler error or warning.

    Diagnostic objects are only valid in the scope of a resource.

    Arguments:
        message: The diagnostic's message.
        range: The range at which the message applies.
        severity: The diagnostic's severity. Can be omitted. If omitted it is up to the
            client to interpret diagnostics as error, warning, info or hint.
        code: The diagnostic's code, which might appear in the user interface.
        source: A human-readable string describing the source of this diagnostic, e.g.
            'esl', or 'esl compiler'.
        related_information: A list of related diagnostic information, e.g. when
            symbol-names within a scope collide you can mark all definitions via this
            property.
    """

    def __init__(
        self,
        message: str,
        range: Range,
        severity: DiagnosticSeverity = DiagnosticSeverity.Error,
        code: str = None,
        source: str = None,
        related_information: List[DiagnosticRelatedInformation] = None,
    ):
        self.message = message
        self.range = range
        self.severity = severity
        self.code = code
        self.source = source
        self.related_information = related_information

    def __repr__(self):
        # Debug/internal: 0-based.
        return self._print(style=repr)

    def __str__(self):
        # Display: 1-based.
        return self._print(style=str)

    def _print(self, style=repr):
        delim = "\n    "
        headline = (
            f"{self.severity.name.upper()} {self.source} [{self.code}]"
            + f" at {style(self.range)}\n  {self.message}"
        )
        sublines = (
            delim.join(style(i) for i in self.related_information)
            if self.related_information is not None
            else None
        )
        if sublines is None:
            return headline
        else:
            return headline + delim + sublines
