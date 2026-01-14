"""Tests for the Document class."""

import pytest
from ragraph.graph import Graph

from raesl.render.specification import Document, Info


def test_doc_smoke(temp_context, pump_example_graph: Graph, datadir):
    doc = Document(
        temp_context,
        graph=pump_example_graph,
        info=Info(
            title="Pump specification",
            abstract="This is the test specification of a water pump system.",
        ),
        prologue=datadir / "doc" / "typst" / "prologue.typ",
        epilogue=datadir / "doc" / "typst" / "epilogue.typ",
        var_table=True,
    )

    doc.compile("pump.typ")
    doc.compile("pump.pdf")


@pytest.mark.skip("SmartLight only available on local machine.")
def test_sl2(temp_context):
    from raesl.compile import to_graph

    fpath = "/home/tiemen/assignments/smart-light/specs"
    graph = to_graph(fpath)

    doc = Document(
        temp_context,
        graph=graph,
        info=Info(
            title="SmartLight 2.0",
            abstract="Inverse Compton Scattering X-ray Source.",
        ),
        var_table=True,
    )

    doc.compile("sl2.typ")
    doc.compile("sl2.pdf")
