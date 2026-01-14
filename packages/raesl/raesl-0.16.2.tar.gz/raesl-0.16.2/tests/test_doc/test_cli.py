import pytest

from raesl.doc.cli import doc


def test_doc_cli(tmpdir, datadir):
    datadir = datadir.absolute()
    with tmpdir.as_cwd():
        esl_paths = str(datadir / "specs/pump_example.esl")
        with pytest.raises(SystemExit) as e:
            doc([esl_paths, "--dry"])
        assert e.value.code == 0
