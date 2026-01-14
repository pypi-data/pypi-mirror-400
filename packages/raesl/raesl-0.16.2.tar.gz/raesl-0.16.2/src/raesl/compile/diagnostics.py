"""ESL compiler Diagnostics.

Diagnostic code scheme:

    Severity:

        E###: ERROR
        W###: WARNING
        I###: INFO
        H###: HINT


    Origin:

        #000: General
        #100: Scanning/Parsing
        #200: Typechecking
        #300: AST Builder
        #400: Instance/output builder
"""

import sys
from typing import IO, Iterable, List, Optional

import click

from raesl import logger, utils
from raesl.types import Diagnostic, DiagnosticRelatedInformation, DiagnosticSeverity, Location

# Proxies
ERROR = DiagnosticSeverity.Error
WARN = DiagnosticSeverity.Warning
INFO = DiagnosticSeverity.Information
HINT = DiagnosticSeverity.Hint
_NON_SEVERE = {WARN, INFO, HINT}
EslRelated = DiagnosticRelatedInformation


class EslDiagnostic(Diagnostic):
    """An unscoped diagnostic as ESL works with multiple text documents at once.

    Arguments:
        message: The diagnostic's message.
        location: The location at which the message applies.
        severity: The diagnostic's severity. Can be omitted. If omitted it is up to the
            client to interpret diagnostics as error, warning, info or hint.
        code: The diagnostic's code, which might appear in the user interface.
        source: A human-readable string describing the source of this diagnostic, e.g.
            'esl', or 'esl compiler'.
        related_information: A list of related diagnostic information, e.g. when
            symbol-names within a scope collide you can mark all definitions via this
            property.

    Attributes:
        range: The range at which the message applies.
    """

    def __init__(
        self,
        message: str,
        location: Location = utils.get_location(),
        severity: DiagnosticSeverity = ERROR,
        code: str = "E100",
        source: str = "RaESL compiler",
        related_information: List[DiagnosticRelatedInformation] = None,
    ):
        self.location = location
        range = None if location is None else location.range
        super().__init__(message, range, severity, code, source, related_information)

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
            + f" at {style(self.location)}\n  {self.message}"
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


class DiagnosticStore:
    """Storage of found diagnostics.

    Attributes:
        diagnostics: Stored diagnostics.
        severity: What diagnostics to log.
        exit: Exit on error.
    """

    def __init__(self, severity: DiagnosticSeverity = ERROR, exit: bool = False):
        self.diagnostics: List[EslDiagnostic] = []
        self.severity = severity
        self.exit = exit

    def add(self, diagnostic: EslDiagnostic):
        """Add a diagnostic. Report directly if below severity threshold."""
        self.diagnostics.append(diagnostic)
        if diagnostic.severity <= self.severity:
            self.report(diagnostic)

    def report(self, diagnostic: EslDiagnostic):
        """Report a single diagnostic."""
        message = str(diagnostic)  # Human readable (e.g, 1-based instead of 0-based)

        if diagnostic.severity <= ERROR:
            logger.error(message)
            if self.exit:
                sys.exit(1)
        elif diagnostic.severity <= WARN:
            logger.warning(message)
        else:
            logger.info(message)

    def dump(self, test: bool = False, stream: Optional[IO[str]] = None):
        """Dump all stored diagnostics to the given stream.

        Arguments:
            test: Whether to output in test mode (otherwise: user-friendly).
            stream: Output stream to use. Defaults to stdout.
        """
        stream = click.get_text_stream("stdout") if stream is None else stream

        if not test and not self.diagnostics:
            stream.write("No diagnostics to report.")

        for d in self.diagnostics:
            stream.write(str(d))
            stream.write("\n")

    def has_severe(self) -> bool:
        """Whether there are severe diagnostics stored."""
        return any(d.severity not in _NON_SEVERE for d in self.diagnostics)


def E100(location: Location = utils.get_location()) -> EslDiagnostic:
    """Unexpected end of the specification."""
    return EslDiagnostic(
        "Unexpected end of the specification.",
        location=location,
        severity=ERROR,
        code="E100",
        source="ESL parser",
    )


def E101(acceptors: Iterable[str], location: Location = utils.get_location()) -> EslDiagnostic:
    """Best line match is ambiguous. Found multiple acceptors: {ambi_acceptors}. This
    is an internal error.
    """
    enum = "', '".join(acceptors)
    return EslDiagnostic(
        (
            f"Best line match is ambiguous. Found multiple acceptors: '{enum}'. "
            + "This is most likely an internal error."
        ),
        location=location,
        severity=ERROR,
        code="E101",
        source="ESL parser",
    )


def E102(location: Location = utils.get_location()) -> EslDiagnostic:
    """Syntax error."""
    return EslDiagnostic(
        "Syntax error.",
        location=location,
        severity=ERROR,
        code="E102",
        source="ESL parser",
    )


def E200(
    name: str,
    kind: str,
    location: Location = utils.get_location(),
    dupes: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Multiple {kind} named '{name}'."""
    dupes = [] if dupes is None else dupes
    return EslDiagnostic(
        f"Multiple {kind}s named '{name}'.",
        location=location,
        severity=ERROR,
        code="E200",
        source="ESL typechecker",
        related_information=[EslRelated(dupe, f"Duplicate {kind} '{name}'.") for dupe in dupes],
    )


def E201(section: str, context: str, location: Location = utils.get_location()) -> EslDiagnostic:
    """This '{section}' section is not allowed in the '{context}' context."""
    return EslDiagnostic(
        f"This '{section}' section is not allowed in the '{context}' context.",
        location=location,
        severity=ERROR,
        code="E201",
        source="ESL typechecker",
    )


def E202(
    kind: str,
    name: Optional[str] = None,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """Missing {kind} for '{name}'."""
    if name is None:
        msg = f"Missing {kind}."
    else:
        msg = f"Missing {kind} for '{name}'."
    return EslDiagnostic(
        msg,
        location=location,
        severity=ERROR,
        code="E202",
        source="ESL typechecker",
    )


def E203(
    kind: str, name: Optional[str] = None, location: Location = utils.get_location()
) -> EslDiagnostic:
    """Unknown {kind} named '{name}'."""
    if name is None:
        msg = f"Unknown {kind}."
    else:
        msg = f"Unknown {kind} named '{name}'."
    return EslDiagnostic(
        msg,
        location=location,
        severity=ERROR,
        code="E203",
        source="ESL typechecker",
    )


def E204(
    name: str,
    kind: str,
    location: Location = utils.get_location(),
    cycle: Optional[List[Location]] = None,
):
    """Cyclically dependent {kind} named '{name}'."""
    cycle = [] if cycle is None else cycle
    length = len(cycle)
    return EslDiagnostic(
        f"Cyclically dependent {kind} named '{name}'.",
        location=location,
        severity=ERROR,
        code="E204",
        source="ESL typechecker",
        related_information=[
            EslRelated(entry, f"Cycle {i+1}/{length}.") for i, entry in enumerate(cycle)
        ],
    )


def E205(name: str, context: str, location: Location = utils.get_location()) -> EslDiagnostic:
    """Cannot find {name} in {context}."""
    return EslDiagnostic(
        f"Cannot find {name} in {context}.",
        location=location,
        severity=ERROR,
        code="E205",
        source="ESL typechecker",
    )


def E206(
    name: str,
    kind: str,
    location: Location = utils.get_location(),
    blocks: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Found {kind} block(s), but the relation definition {name} has no such
    parameters.
    """
    blocks = [] if blocks is None else blocks
    return EslDiagnostic(
        (
            f"Found {kind} block(s), "
            + f"but the relation definition {name} has no such parameters."
        ),
        location=location,
        severity=ERROR,
        code="E206",
        source="ESL typechecker",
        related_information=[EslRelated(block, f"Relation {kind} block") for block in blocks],
    )


def E207(
    name: str,
    kind: str,
    location: Location = utils.get_location(),
    definition: Location = utils.get_location(),
) -> EslDiagnostic:
    """Relation instance '{name}' is missing a '{kind}' parameters section."""
    return EslDiagnostic(
        f"Relation instance '{name}' is missing a '{kind}' parameters section.",
        location=location,
        severity=ERROR,
        code="E207",
        source="ESL typechecker",
        related_information=[EslRelated(definition, "Corresponding relation definition.")],
    )


def E208(
    name: str,
    kind: str,
    num: int,
    location: Location = utils.get_location(),
    definition: Location = utils.get_location(),
) -> EslDiagnostic:
    """Relation instance '{name}' is missing at least {num} '{kind}' parameters."""
    return EslDiagnostic(
        f"Relation instance '{name}' is missing at least {num} '{kind}' parameters.",
        location=location,
        severity=ERROR,
        code="E208",
        source="ESL typechecker",
        related_information=[EslRelated(definition, "Corresponding relation definition.")],
    )


def E209(
    name: str,
    kind: str,
    other_kind: str,
    location: Location = utils.get_location(),
    others: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """'{name}' is both a {kind} and a {other_kind}."""
    others = [] if others is None else others
    return EslDiagnostic(
        f"'{name}' is both a {kind} and a {other_kind}.",
        location=location,
        severity=ERROR,
        code="E209",
        source="ESL typechecker",
        related_information=[EslRelated(other, f"{other_kind} location.") for other in others],
    )


def E210(lhs: Location, rhs: Location, reason: str = "are not compatible") -> EslDiagnostic:
    """Values cannot be compared, they {reason}."""
    return EslDiagnostic(
        f"Values cannot be compared, they {reason}.",
        location=lhs,
        severity=ERROR,
        code="E210",
        source="ESL typechecker",
        related_information=[EslRelated(rhs, "Other value location.")],
    )


def E211(
    verb: str,
    preposition: str,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """Unsupported verb-preposition combination '{verb} {preposition}'."""
    return EslDiagnostic(
        f"Unsupported verb-preposition combination '{verb} {preposition}'.",
        location=location,
        severity=ERROR,
        code="E211",
        source="ESL typechecker",
    )


def E212(
    kind: str,
    value: str,
    allowed: str,
    name: Optional[str] = None,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """{kind.capitalize()} '{name}' uses '{value}', but should use {allowed}."""
    if name is None:
        msg = f"{kind.capitalize()} uses '{value}', but should use {allowed}."
    else:
        msg = f"{kind.capitalize()} '{name}' uses '{value}', but should use {allowed}."
    return EslDiagnostic(
        msg,
        location=location,
        severity=ERROR,
        code="E212",
        source="ESL typechecker",
    )


def E213(
    kind: str,
    num: int,
    allowed: str,
    location: Location = utils.get_location(),
    occurrences: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Found {num} {kind}(s), but there should be {allowed}."""
    occurrences = [] if occurrences is None else occurrences
    return EslDiagnostic(
        f"Found {num} {kind}(s), but there should be {allowed}.",
        location=location,
        severity=ERROR,
        code="E213",
        source="ESL typechecker",
        related_information=[EslRelated(occ, f"{kind.capitalize()}") for occ in occurrences],
    )


def E214(
    name: str,
    location: Location = utils.get_location(),
    def_location: Optional[Location] = None,
) -> EslDiagnostic:
    """Definition of type '{name}' failed with an error."""
    def_locs = [] if def_location is None else [def_location]
    return EslDiagnostic(
        f"Definition of type '{name}' failed with an error.",
        location=location,
        severity=ERROR,
        code="E214",
        source="ESL typechecker",
        related_information=[EslRelated(loc, "Related type definition.") for loc in def_locs],
    )


def E215(
    name: str,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """Type name '{name}' must be the name of an elementary type."""
    return EslDiagnostic(
        f"Type name '{name}' must be the name of an elementary type.",
        location=location,
        severity=ERROR,
        code="E215",
        source="ESL typechecker",
    )


def E216(
    name: str,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """Unit '{name}' should not have square brackets around it's name."""
    return EslDiagnostic(
        f"Unit '{name}' should not have square brackets around it's name.",
        location=location,
        severity=ERROR,
        code="E216",
        source="ESL typechecker",
    )


def E217(
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """The dimensionless unit '-' is not allowed to be specified explicitly."""
    return EslDiagnostic(
        "The dimensionless unit '-' is not allowed to be specified explicitly.",
        location=location,
        severity=ERROR,
        code="E217",
        source="ESL typechecker",
    )


def E218(name: str, location: Location = utils.get_location()) -> EslDiagnostic:
    """Standard type '{name}' cannot be overridden."""
    return EslDiagnostic(
        f"Standard type '{name}' cannot be overridden.",
        location=location,
        severity=ERROR,
        code="E218",
        source="ESL typechecker",
    )


def E219(name: str, location: Location = utils.get_location()) -> EslDiagnostic:
    """Unit '{name}' is not allowed here."""
    return EslDiagnostic(
        f"Unit '{name}' is not allowed here.",
        location=location,
        severity=ERROR,
        code="E219",
        source="ESL typechecker",
    )


def E220(name: str, kind: str, location: Location = utils.get_location()) -> EslDiagnostic:
    """Element '{name}' does not match with a {kind}."""
    return EslDiagnostic(
        f"Element '{name}' does not match with a {kind}.",
        location=location,
        severity=ERROR,
        code="E220",
        source="ESL typechecker",
    )


def E221(
    kind: str,
    num: int,
    expected: int,
    location: Location = utils.get_location(),
    references: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Number of {kind}s does not match. Found {num}, expected {expected}."""
    references = [] if references is None else references
    return EslDiagnostic(
        f"Number of {kind}s does not match. Found {num}, expected {expected}.",
        location=location,
        severity=ERROR,
        code="E221",
        source="ESL typechecker",
        related_information=[
            EslRelated(ref, f"Reference with {expected} {kind}(s).") for ref in references
        ],
    )


def E222(
    name: str,
    other: str,
    location: Location = utils.get_location(),
    other_loc: Location = utils.get_location(),
) -> EslDiagnostic:
    """Value '{name}' has additional value restrictions relative to '{other}'."""
    return EslDiagnostic(
        f"Value '{name}' has additional value restrictions relative to '{other}'.",
        location=location,
        severity=ERROR,
        code="E222",
        source="ESL typechecker",
        related_information=[EslRelated(other_loc, f"Other value '{other}'.")],
    )


def E223(
    name: str,
    other: str,
    kind: str,
    location: Location = utils.get_location(),
    other_loc: Optional[Location] = None,
) -> EslDiagnostic:
    """'{name}' is not a {kind} of {other}."""
    related = [] if other_loc is None else [EslRelated(other_loc, f"{other}")]
    return EslDiagnostic(
        f"'{name}' is not a {kind} of {other}.",
        location=location,
        severity=ERROR,
        code="E223",
        source="ESL typechecker",
        related_information=related,
    )


def E224(
    kind: str,
    unsupported: str,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """{kind.capitalize()}s do not support {unsupported}."""
    return EslDiagnostic(
        f"{kind.capitalize()}s do not support {unsupported}.",
        location=location,
        severity=ERROR,
        code="E224",
        source="ESL typechecker",
    )


def E225(
    part: str,
    first_part: str,
    kind: str,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """Cannot resolve '.{part}' part of the '{first_part}' {kind}."""
    return EslDiagnostic(
        f"Cannot resolve '.{part}' part of the '{first_part}' {kind}.",
        location=location,
        severity=ERROR,
        code="E225",
        source="ESL typechecker",
    )


def E226(
    name: str,
    location: Location = utils.get_location(),
) -> EslDiagnostic:
    """Need '{name}' is not allowed to reference a bundle."""
    return EslDiagnostic(
        f"Need '{name}' is not allowed to reference a bundle.",
        location=location,
        severity=ERROR,
        code="E226",
        source="ESL typechecker",
        related_information=[EslRelated(location, "Only elementary variables, try its fields.")],
    )


def E227(
    name: str,
    scope: str,
    location: Location = utils.get_location(),
    dupes: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Multiple identifier '{name}' within '{cdef_name}'."""
    dupes = [] if dupes is None else dupes
    return EslDiagnostic(
        f"Duplicate identifier '{name}' within the scope of '{scope}'.",
        location=location,
        severity=ERROR,
        code="E200",
        source="ESL typechecker",
        related_information=[EslRelated(dupe, f"Duplicate identifier '{name}'.") for dupe in dupes],
    )


def E228(lhs: Location, rhs: Location, reason: str = "are not compatible") -> EslDiagnostic:
    """Values cannot be compared, design rule {reason}."""
    return EslDiagnostic(
        f"Values cannot be compared, design rule {reason}.",
        location=lhs,
        severity=ERROR,
        code="E228",
        source="ESL typechecker",
    )


def E400(
    name: str,
    location: Location = utils.get_location(),
    owners: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Elementary variable value '{name}' has more than one property owner."""
    owners = [] if owners is None else owners
    return EslDiagnostic(
        f"Elementary variable value '{name}' has more than one property owner.",
        location=location,
        severity=ERROR,
        code="E400",
        source="ESL instantiating",
        related_information=[EslRelated(owner, "Duplicate owner.") for owner in owners],
    )


def W200(
    name: str,
    kind: str,
    location: Location = utils.get_location(),
    dupes: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """{kind.capitalize()} '{name}' has been specified multiple times."""
    dupes = [] if dupes is None else dupes
    return EslDiagnostic(
        f"{kind.capitalize()} '{name}' has been specified multiple times.",
        location=location,
        severity=WARN,
        code="W200",
        source="ESL typechecker",
        related_information=[EslRelated(dupe, f"Duplicate {kind}.") for dupe in dupes],
    )


def W300(
    element: Optional[str] = None,
    location: Location = utils.get_location(),
    comments: Optional[List[Location]] = None,
) -> EslDiagnostic:
    """Documentation comment(s) could not be assigned to '{element}'."""
    element = "a specification element" if element is None else f"'{element}'"
    comments = [] if comments is None else comments
    return EslDiagnostic(
        f"Documentation comment(s) could not be assigned to {element}.",
        location=location,
        severity=WARN,
        code="W300",
        source="ESL AST builder",
        related_information=[
            EslRelated(doc, "Unassigned documentation comment.") for doc in comments
        ],
    )
