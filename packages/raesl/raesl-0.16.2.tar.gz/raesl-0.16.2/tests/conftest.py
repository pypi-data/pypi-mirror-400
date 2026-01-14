import difflib
import json
import shutil
import uuid
from pathlib import Path

import pytest

from raesl.render.context import Context

TESTS = Path(__file__).parent
UPDATE_PATH = TESTS / ".update"
UPDATE = UPDATE_PATH.exists()
INSPECT_PATH = TESTS / ".inspect"
INSPECT = INSPECT_PATH.exists()
SPECS_PATH = TESTS / "data" / "specs"


# Fix UUID generation during tests:
def generate_int_uuids():
    index = 0
    while True:
        yield uuid.UUID(int=index)
        index += 1


@pytest.fixture(autouse=True, scope="function")
def reset_uuids():
    int_uuid = generate_int_uuids()
    uuid.uuid4 = lambda: next(int_uuid)


@pytest.fixture
def update():
    return UPDATE


@pytest.fixture
def inspect():
    return INSPECT


@pytest.fixture
def datadir():
    return (TESTS / "data").relative_to(Path.cwd())


@pytest.fixture
def gendir():
    path = TESTS / "generated"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture(params=SPECS_PATH.glob("*.esl"))
def spec(request) -> Path:
    return request.param.relative_to(Path.cwd())


@pytest.fixture(params=(TESTS / "data" / "good_examples").glob("*.esl"))
def good_example(request):
    return request.param.relative_to(Path.cwd())


@pytest.fixture(params=(TESTS / "data" / "bad_examples").glob("*.esl"))
def bad_example(request):
    return request.param.relative_to(Path.cwd())


@pytest.fixture
def pump_example_graph(datadir: Path):
    from raesl.compile import to_graph

    fpath = datadir / "specs" / "pump_example.esl"
    graph = to_graph(fpath)
    return graph


@pytest.fixture
def verify_content():
    def verify(content: str, reference: Path, start=0, stop=None):
        if UPDATE:
            reference.write_text(content)

        try:
            assert (
                content.splitlines()[start:stop] == reference.read_text().splitlines()[start:stop]
            ), "Content lines should match."
        except AssertionError as e:
            if reference.suffix == ".yaml" and "*id" in e.args[0]:
                pass  # Pass on finicky YAML ID errors.
            else:
                raise e

    return verify


@pytest.fixture
def check_diff():
    """Check whether there is a diff w.r.t. to the reference path."""

    def _check_diff(path: Path, ref_path: Path, sort: bool = False):
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        ref_text = ref_path.read_text(encoding="utf-8") if path.exists() else ""

        lines = text.splitlines(False)
        ref_lines = ref_text.splitlines(False)
        if sort:
            lines, ref_lines = sorted(lines), sorted(ref_lines)

        diff = difflib.unified_diff(
            ref_lines,
            lines,
            fromfile=str(ref_path),
            tofile=str(path),
            lineterm="",
        )
        diffstr = "\n".join(diff)

        if diffstr and UPDATE:
            if not ref_path.parent.exists():
                ref_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, ref_path)
        else:
            assert not diffstr, diffstr

    return _check_diff


@pytest.fixture
def check_digraph(tmpdir, datadir, check_diff):
    """Digraph output check function."""
    import graphviz

    def _check_digraph(digraph: graphviz.Digraph, fname: Path):
        digraph.comment = "TEST"
        dot_path = Path(digraph.save(directory=tmpdir, filename=fname))
        ref_path = Path(datadir / "dot" / fname)
        check_diff(dot_path, ref_path, sort=True)

    return _check_digraph


@pytest.fixture
def check_plotly(tmpdir, datadir, check_diff, inspect):
    """Plotly output check function."""
    from plotly.graph_objs import Figure

    def _check_plotly(fig: Figure, fname: str):
        """Checking if the figure data and shapes are equal to the data and shapes
        stored in the reference file.

        Arguments:
            fig: The figure to be tested.
            file_path: The relative path to the reference file.
            update: Whether to update the reference file.
        """
        if inspect:
            fig.show()

        plotly_json = fig.to_plotly_json()

        plotly_json["layout"]["shapes"] = sorted(
            plotly_json["layout"]["shapes"], key=lambda x: str(x)
        )

        for idx, data in enumerate(plotly_json["data"]):
            for key in ["x", "y", "text"]:
                if plotly_json["data"][idx].get("text", None) is None:
                    # Text data is not always present at every plot element.
                    continue
                plotly_json["data"][idx][key] = sorted(data[key], key=lambda x: x)

        (tmpdir / fname).write_text(
            json.dumps(plotly_json, sort_keys=True, indent=2), encoding="utf-8"
        )

        check_diff(tmpdir / fname, datadir / "plotly" / fname, sort=True)

    return _check_plotly


@pytest.fixture
def context() -> Context:
    return Context()


@pytest.fixture
def temp_context(tmp_path: Path) -> Context:
    return Context(output_dir=tmp_path)
