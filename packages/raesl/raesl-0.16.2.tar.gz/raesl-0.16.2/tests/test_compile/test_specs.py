"""Test compiler output for specifications in data/specs"""

import difflib
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional

from ragraph.io.json import from_json, to_json

import raesl.plot
from raesl.compile.ast.specification import dump
from raesl.compile.cli import run

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.diagnostics import DiagnosticStore


def compare_texts(exp_path: Path, real_path: Path, update) -> Optional[Iterable[str]]:
    """Compare expected output with real output, and display differences.

    Returns:
        Diff lines or None.
    """
    real_text = real_path.read_text() if real_path.exists() else ""
    if update:
        if real_text == "":
            if exp_path.exists():
                exp_path.unlink()
        else:
            exp_path.write_text(real_text)
        return None
    exp_text = exp_path.read_text() if exp_path.exists() else ""

    if exp_text == real_text:
        return None

    exp_lines = exp_text.split("\n")
    real_lines = real_text.split("\n")
    diff = difflib.unified_diff(
        exp_lines,
        real_lines,
        fromfile=str(exp_path),
        tofile=str(real_path),
        lineterm="",
    )
    return diff


def check_spec(
    specification: Optional["Specification"],
    spec_path: Path,
    tmpdir: Path,
    update: bool,
):
    """Check specification output."""
    exp_path = spec_path.with_suffix(".exp_output")
    real_path = tmpdir / (spec_path.stem + ".output")
    if specification is not None:
        with real_path.open("a") as f:
            dump(specification, f)
    else:
        real_path.write_text("")
    diff = compare_texts(exp_path, real_path, update)
    assert diff is None, "\n".join(diff)


def check_diag(diag_store: "DiagnosticStore", spec_path: Path, tmpdir: Path, update: bool):
    """Check diagnostic output."""
    exp_path = spec_path.with_suffix(".exp_error")
    real_path = tmpdir / (spec_path.stem + ".error")
    with real_path.open("a") as f:
        diag_store.dump(test=True, stream=f)
    diff = compare_texts(exp_path, real_path, update)
    assert diff is None, "\n".join(diff)


def test_doccomment_handling(datadir: Path, update: bool):
    """Test for multi-file doc comment handling"""

    fpath = datadir / "doccomments"

    diag_store, parsed_spec, g = run(fpath)
    assert g is not None

    assert g["world.x"].annotations.esl_info["comments"] == [
        "Oh yeah it works!",
        "Even multi-line!",
    ]
    assert g["world.blib"].annotations.esl_info["comments"] == [
        "Hello",
    ]
    assert g["world.blib.A"].annotations.esl_info["comments"] == [
        "Apple",
    ]
    assert g["world.blib.B"].annotations.esl_info["comments"] == [
        "Pie",
    ]
    assert g["world.blib.g1"].annotations.esl_info["comments"] == [
        "Strawberry",
        "Bonjour",
    ]
    assert g["world.blib.g1"].annotations.esl_info["comments"] == [
        "Strawberry",
        "Bonjour",
    ]
    assert g["world.blib.g2"].annotations.esl_info["comments"] == [
        "Banana's",
        "Au revoir",
    ]
    assert g["world.blub"].annotations.esl_info["comments"] == [
        "Goodby",
    ]
    assert g["world.blub.A"].annotations.esl_info["comments"] == [
        "Apple",
    ]
    assert g["world.blub.B"].annotations.esl_info["comments"] == [
        "Pie",
    ]
    assert g["world.blub.g1"].annotations.esl_info["comments"] == [
        "Strawberry",
        "Bonjour",
    ]
    assert g["world.blub.g1"].annotations.esl_info["comments"] == [
        "Strawberry",
        "Bonjour",
    ]
    assert g["world.blub.g2"].annotations.esl_info["comments"] == [
        "Banana's",
        "Au revoir",
    ]
    assert g["world.g2"].annotations.esl_info["comments"] == ["Peace", "Au revoir"]
    assert g["world.g4"].annotations.esl_info["comments"] == ["Pear", "Bonjour"]


def test_graph_building(datadir: Path, update: bool, inspect: bool):
    fpaths = [
        datadir / "specs" / "pump_example.esl",
        datadir / "specs" / "behavior-requirements_path_dependencies.esl",
        datadir / "specs" / "design_dependency_migration.esl",
    ]

    for fpath in fpaths:
        diag_store, parsed_spec, g = run(fpath)
        assert g is not None

        if diag_store.diagnostics:
            diag_store.dump()

        ref_file = fpath.with_suffix(".json")

        if update:
            to_json(g, ref_file)

        g_ref = from_json(ref_file)

        for n in g.nodes:
            assert g[n.name].annotations.esl_info == g_ref[n.name].annotations.esl_info

        for ni in g.nodes:
            for nj in g.nodes:
                for e, e_ref in zip(g[ni.name, nj.name], g_ref[ni.name, nj.name]):
                    if hasattr(e, "esl_info"):
                        for key, val in e.annotations.esl_info["reason"]:
                            assert val.sort == e_ref.annotations.esl_inf["reason"]["key"].sort()

        if inspect:
            style = raesl.plot.Style(ragraph=dict(piemap={"display": "labels", "mode": "relative"}))
            fig = raesl.plot.mdm(
                graph=g,
                node_kinds=[
                    "component",
                    "function_spec",
                    "behavior_spec",
                    "variable",
                    "design_spec",
                    "relation_spec",
                    "need",
                ],
                edge_kinds=[
                    "functional_dependency",
                    "mapping_dependency",
                    "logical_dependency",
                    "coordination_dependency",
                    "design_dependency",
                ],
                depth=10,
                style=style,
            )
            fig.show()


def test_specs(spec: Path, datadir: Path, tmpdir: Path, update: bool):
    diag_store, compiled_spec, graph = run(spec)
    check_spec(compiled_spec, spec, Path(tmpdir), update)
    check_diag(diag_store, spec, Path(tmpdir), update)


def test_bad_specs(bad_example: Path, datadir: Path, tmpdir: Path, update: bool):
    diag_store, compiled_spec, graph = run(bad_example)
    check_spec(compiled_spec, bad_example, Path(tmpdir), update)
    check_diag(diag_store, bad_example, Path(tmpdir), update)


def test_good_specs(good_example: Path, datadir: Path, tmpdir: Path, update: bool):
    diag_store, compiled_spec, graph = run(good_example)
    check_spec(compiled_spec, good_example, Path(tmpdir), update)
    check_diag(diag_store, good_example, Path(tmpdir), update)
