from pathlib import Path

from raesl.doc.doc import Doc
from raesl.utils import get_esl_paths

LOCAL_DEBUG = False


def test_esls_en(tmpdir, datadir, gendir, inspect):
    datadir = datadir.absolute()
    gendir = gendir.absolute()

    with tmpdir.as_cwd():
        d = Doc(
            datadir / "doc" / "esl" / "pump.esl",
            prologue=datadir / "doc" / "md" / "prologue.md",
            epilogue=datadir / "doc" / "md" / "epilogue.md",
            rich="tex",
            language="en",
            title="Pump",
        )
        if inspect:
            out_file = Path(gendir) / "pump_en.pdf"
        else:
            out_file = "pump_en.pdf"
        d.save(out_file)


def test_esls_nl(tmpdir, datadir, gendir, inspect):
    datadir = datadir.absolute()
    gendir = gendir.absolute()

    for esl_paths, name in zip(
        [
            [datadir / "doc" / "esl" / "basisspecificatie.esl"],
            get_esl_paths(datadir / "doc" / "esl" / "noodstopketen"),
        ],
        ["Basisspecificatie", "Noodstopketen"],
    ):
        with tmpdir.as_cwd():
            d = Doc(
                *esl_paths,
                prologue=datadir / "doc" / "md" / "prologue.md",
                epilogue=datadir / "doc" / "md" / "epilogue.md",
                rich="tex",
                language="nl",
                title=name,
            )
            if inspect:
                out_file = Path(gendir) / f"{name}.pdf"
            else:
                out_file = f"{name}.pdf"
            d.save(out_file)


def test_pump_md(tmpdir, datadir, gendir, inspect):
    datadir = datadir.absolute()
    gendir = gendir.absolute()

    with tmpdir.as_cwd():
        d = Doc(
            datadir / "doc" / "esl" / "pump.esl",
            prologue=datadir / "doc" / "md" / "prologue.md",
            epilogue=datadir / "doc" / "md" / "epilogue.md",
            rich="md",
            language="en",
            title="Pump",
        )
        if inspect:
            out_file = Path(gendir) / "pump_en.pdf"
        else:
            out_file = "pump_en.pdf"
        d.save(out_file)


def test_pump_set_mdm(tmpdir, datadir, gendir, inspect):
    datadir = datadir.absolute()
    gendir = gendir.absolute()

    with tmpdir.as_cwd():
        d = Doc(
            datadir / "doc" / "esl" / "pump.esl",
            prologue=datadir / "doc" / "md" / "prologue.md",
            epilogue=datadir / "doc" / "md" / "epilogue.md",
            rich="tex",
            rich_opts={
                "node_kinds": ["component"],
                "edge_kinds": ["functional_dependency"],
                "pie_mode": "relative",
            },
            language="en",
            title="Pump",
        )
        if inspect:
            out_file = Path(gendir) / "pump_set_mdm.pdf"
        else:
            out_file = "pump_set_mdm.pdf"
        d.save(out_file)


def test_bundle_handling(tmpdir, datadir, gendir, inspect):
    datadir = datadir.absolute()
    gendir = gendir.absolute()

    with tmpdir.as_cwd():
        d = Doc(
            datadir / "doc/esl/bundle_handling.esl",
            rich="tex",
            language="en",
            title="Bundle handling",
        )
        if inspect:
            out_file = Path(gendir) / "bundle_handling.pdf"
        else:
            out_file = "bundle_handling.pdf"
        d.save(out_file)


def test_bundle_handling_nl(tmpdir, datadir, gendir, inspect):
    datadir = datadir.absolute()
    gendir = gendir.absolute()

    with tmpdir.as_cwd():
        d = Doc(
            datadir / "doc/esl/bundle_handling.esl",
            rich="tex",
            language="nl",
            title="Bundle handling",
        )
        if inspect:
            out_file = Path(gendir) / "bundle_handling_nl.pdf"
        else:
            out_file = "bundle_handling_nl.pdf"
        d.save(out_file)
