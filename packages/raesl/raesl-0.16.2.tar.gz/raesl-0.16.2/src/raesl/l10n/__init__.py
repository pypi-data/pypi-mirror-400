"""Localization module to support localized text generation."""

from pathlib import Path
from typing import Literal

from raesl.l10n.abc import LocaleAbc
from raesl.l10n.en_us import EnUs
from raesl.l10n.nl_nl import NlNl

HERE = Path(__file__).parent

LocaleId = Literal["en-US", "nl-NL"]
"""Supported locale IDs."""

SHORTHANDS: dict[str, str] = {"nl": "nl-NL", "en": "en-US"}


def get_locale(id: LocaleId = "en-US") -> LocaleAbc:
    """Get the locale given for a given Locale ID."""
    match SHORTHANDS.get(id, id).lower():
        case "en-us":
            return EnUs()
        case "nl-nl":
            return NlNl()
        case _:
            raise ValueError(f"Unknown locale. Supported locales: {LocaleId}")
