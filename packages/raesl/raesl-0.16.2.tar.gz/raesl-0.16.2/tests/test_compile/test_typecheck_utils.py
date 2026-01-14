"""Tests for the typechecking utils module."""
from raesl.compile.typechecking import utils


def test_nomultiple():
    arguments = [0, 1, 2, 3, 4, 5]
    result = utils.split_arguments(len(arguments), None, arguments)
    assert result == [[a] for a in arguments]


def test_multiple1():
    arguments = [0, 1, 2, 3, 4, 5]
    params_length = 5

    result = utils.split_arguments(params_length, 0, arguments)
    assert result == [[0, 1], [2], [3], [4], [5]]

    result = utils.split_arguments(params_length, 1, arguments)
    assert result == [[0], [1, 2], [3], [4], [5]]

    result = utils.split_arguments(params_length, 2, arguments)
    assert result == [[0], [1], [2, 3], [4], [5]]

    result = utils.split_arguments(params_length, 3, arguments)
    assert result == [[0], [1], [2], [3, 4], [5]]

    result = utils.split_arguments(params_length, 4, arguments)
    assert result == [[0], [1], [2], [3], [4, 5]]


def test_multiple2():
    arguments = [0, 1, 2, 3, 4]
    params_length = 5

    # 'multiple' is 1 argument
    result = utils.split_arguments(params_length, 0, arguments)
    assert result == [[a] for a in arguments]

    result = utils.split_arguments(params_length, 1, arguments)
    assert result == [[a] for a in arguments]

    result = utils.split_arguments(params_length, 2, arguments)
    assert result == [[a] for a in arguments]

    result = utils.split_arguments(params_length, 3, arguments)
    assert result == [[a] for a in arguments]

    result = utils.split_arguments(params_length, 4, arguments)
    assert result == [[a] for a in arguments]


def test_multiple3():
    arguments = ["a", "b", "c"]
    params_length = 1

    # 1 multi-value parameter.
    result = utils.split_arguments(params_length, 0, arguments)
    assert result == [arguments]
