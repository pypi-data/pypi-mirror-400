"""Tests for scanner module."""
from raesl.compile import scanner


def test_whitespace_pat():
    for text in [
        "|",
        " |",
        " |\n",
        "|a",
        " |a",
        "... |",
        "|.... ",
        " ...\n|",
        "|... text",
        "|... ...",
        "#some thing|",
        "#some thing\r|\n",
        " #|",
        "...#\n |text",
        "...#\n ... \n |text",
    ]:
        exp_len = text.find("|")
        text = text[:exp_len] + text[exp_len + 1 :]

        s = scanner.Lexer(None, text, 0, 0, 1, [])
        s.skip_white()
        assert s.offset == exp_len, "Input: '{}'".format(repr(text))


def test_find():
    s = scanner.Lexer(None, " define types\n", 0, 0, 1, [])

    t = s.find("DEFINE_KW")
    assert t, "should find 'define'"
    assert t.tok_text == "define"

    t = s.find("VERB_KW")
    assert not t, "should not find 'verb'"

    t = s.find("TYPE_KW")
    assert t, "should find 'types'"
    assert t.tok_text == "types"

    t = s.find("NL_TK")
    assert t, "should find newline"


def test_not_find_type_kw1():
    s = scanner.Lexer(None, "typess", 0, 0, 1, [])
    t = s.find("TYPE_KW")
    assert not t


def test_not_find_type_kw2():
    s = scanner.Lexer(None, "types-etc", 0, 0, 1, [])
    t = s.find("TYPE_KW")
    assert not t


def test_find_type_kw():
    s = scanner.Lexer(None, "TyPEs", 0, 0, 1, [])
    t = s.find("TYPE_KW")
    assert t
    assert t.tok_text == "TyPEs"


def test_find_name():
    s = scanner.Lexer(None, "label: defines most needs", 0, 0, 1, [])

    t = s.find("NAME")
    assert t, "Should find 'label'"
    assert t.tok_text == "label"

    t = s.find("COLON_TK")
    assert t, "Should find ':'"
    assert t.tok_text == ":"

    t = s.find("NAME")
    assert t, "Should find 'defines'"
    assert t.tok_text == "defines"

    t = s.find("NAME")
    assert t, "Should find 'most'"
    assert t.tok_text == "most"

    t = s.find("NAME")
    assert t, "Should find 'needs'"
    assert t.tok_text == "needs"


def test_name_syntax1():
    s = scanner.Lexer(None, "abc-def", 0, 0, 1, [])

    t = s.find("NAME")
    assert t, "Should find 'abc-def'"
    assert t.tok_text == "abc-def"


def test_name_syntax2():
    s = scanner.Lexer(None, "-def", 0, 0, 1, [])

    t = s.find("NAME")
    assert not t, "Should not find '-def'"

    t = s.find("NONSPACE")
    assert t, "Should find '-def'"
    assert t.tok_text == "-def"


def test_name_syntax3():
    s = scanner.Lexer(None, "abc-", 0, 0, 1, [])

    t = s.find("NAME")
    assert t, "Should find 'abc'"
    assert t.tok_text == "abc"


def test_find_words():
    s = scanner.Lexer(None, "label: defines most needs", 0, 0, 1, [])

    t = s.find("NONSPACE")
    assert t, "Should find 'label:'"
    assert t.tok_text == "label:"

    t = s.find("DEFINE_KW")
    assert not t, "should not find define keyword"

    t = s.find("NONSPACE")
    assert t, "Should find 'defines'"
    assert t.tok_text == "defines"

    t = s.find("NONSPACE")
    assert t, "Should find 'most'"
    assert t.tok_text == "most"

    t = s.find("NONSPACE")
    assert t, "Should find 'needs'"
    assert t.tok_text == "needs"


def test_find_comma():
    s = scanner.Lexer(None, "x,y x, y,", 0, 0, 1, [])

    t = s.find("NONCOMMA")
    assert t, "Should find 'x,y'"
    assert t.tok_text == "x,y"

    t = s.find("NONSPACE")
    assert t, "Should find 'x,'"
    assert t.tok_text == "x,"

    t = s.find("NONCOMMA")
    assert t, "Should find 'y'"
    assert t.tok_text == "y"
