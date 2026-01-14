from pathlib import Path
from shutil import rmtree

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples
from ragraph.graph import Graph

DOCS_DIR = Path(__file__).parent.parent / "docs"
DOCS_FILES = DOCS_DIR.glob("**/*.md")


@pytest.mark.parametrize("example", find_examples(*DOCS_FILES), ids=str)
def test_docs(
    example: CodeExample,
    eval_example: EvalExample,
    datadir: Path,
    pump_example_graph: Graph,
    tmpdir,
):
    """Test the package's documentation."""

    if example.prefix_settings().get("skip"):
        return

    docs_gendir = DOCS_DIR / "generated"
    docs_gendir.mkdir(exist_ok=True)

    pump_esl = datadir / "specs" / "pump_example.esl"
    globals = dict(
        pump_esl=pump_esl,
        path_to_esl_file=pump_esl,
        path_to_esl_dir=datadir / "esl",
        path_to_extra_esl_file=datadir / "esl" / "noodstopketen" / "level_0" / "preamble.esl",
        pump_prologue=datadir / "doc" / "md" / "prologue.md",
        pump_epilogue=datadir / "doc" / "md" / "epilogue.md",
        generated=docs_gendir,
        pump_example_graph=pump_example_graph,
        graph=pump_example_graph,
        cfv_path=docs_gendir / "cfv_mdm.svg",
        hierarchy_path=docs_gendir / "hierarchy_diagram",
        functional_dependency_path=docs_gendir / "functional_dependency_diagram",
        functional_context_path=docs_gendir / "functional_context_diagram",
        function_chain_path=docs_gendir / "function_chain_diagram",
        functional_traceability_path=docs_gendir / "functional_traceability_diagram",
    )

    eval_example.set_config(
        line_length=88,
        target_version="py311",
        ruff_select=["E", "W", "I"],
        ruff_ignore=["F821"],
    )
    if eval_example.update_examples:
        eval_example.format_ruff(example)
        eval_example.run_print_update(example, module_globals=globals)
    else:
        eval_example.lint_ruff(example)
        eval_example.run_print_check(example, module_globals=globals)

    # Temporary file cleanup because of rich document generation.
    rmtree(Path(__file__).parent.parent / "images", ignore_errors=True)
