"""Tests for the localization module."""

from pytest import mark

from raesl.l10n import get_locale


def test_locale_smoke():
    en_us = get_locale()
    assert en_us.locale_id() == "en-US"

    nl_nl = get_locale("nl")
    assert nl_nl.locale_id() == "nl-NL"


@mark.parametrize(
    "item,count,pluralized,result",
    [
        ("foo", 0, None, "zero foos"),
        ("foo", 1, None, "one foo"),
        ("foo", 2, None, "two foos"),
        ("foo", 10, None, "ten foos"),
        ("foo", 11, None, "11 foos"),
        ("foo", 0, "quux", "zero quux"),
        ("bay", 0, None, "zero bays"),
        ("quantity", 0, None, "zero quantities"),
    ],
)
def test_plural(item: str, count: int, pluralized: str, result: str):
    loc = get_locale()

    assert loc.amount(item=item, count=count, pluralized=pluralized) == result
