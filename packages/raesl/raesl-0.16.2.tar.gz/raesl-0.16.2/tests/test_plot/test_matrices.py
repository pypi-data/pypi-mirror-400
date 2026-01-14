import plotly.io as pio
from ragraph import colors
from ragraph.analysis.heuristics import markov_gamma
from ragraph.graph import Graph
from ragraph.io.esl import from_esl

import raesl.plot


def test_mdm_0(pump_example_graph: Graph, check_plotly):
    """Testing the creating of a multi-domain-matrix plot."""
    g = pump_example_graph

    style = raesl.plot.Style(ragraph=dict(piemap={"display": "labels", "mode": "relative"}))

    for depth in [1, 2]:
        mdm = raesl.plot.mdm(
            g,
            node_kinds=["component", "function_spec", "variable"],
            edge_kinds=["functional_dependency", "mapping_dependency"],
            depth=depth,
            style=style,
        )

        fname = f"pump_mdm_fig_level_{depth}.json"
        check_plotly(mdm, fname)


def test_mdm_1(tmpdir, datadir, check_plotly):
    g = from_esl(datadir / "doc" / "esl" / "noodstopketen")

    col_dict = {
        label: color
        for label, color in zip(g.edge_labels, colors.get_categorical(len(g.edge_labels)))
    }

    # Plot clustered matrix
    markov_gamma(
        g,
        alpha=2,
        beta=4.0,
        mu=3.0,
        gamma=2.0,
        local_buses=True,
        leafs=[n for n in g.leafs if n.kind == "component"],
    )

    markov_gamma(
        g,
        alpha=2,
        beta=3.5,
        mu=3.5,
        gamma=10.0,
        local_buses=True,
        leafs=[n for n in g.leafs if n.kind == "function_spec"],
    )

    style = raesl.plot.Style(
        ragraph=dict(
            piemap={"display": "labels", "mode": "relative"},
            palettes={"fields": col_dict},
            show_legend=True,
        )
    )

    depth = g.max_depth
    mdm = raesl.plot.mdm(
        g,
        node_kinds=["component", "function_spec"],
        edge_kinds=["functional_dependency", "mapping_dependency"],
        depth=depth,
        style=style,
    )

    fname = "noodstopketen_mdm_clustered.json"
    check_plotly(mdm, fname)


def test_mdm_group_export(tmp_path, datadir):
    g = from_esl(datadir / "doc" / "esl" / "noodstopketen")

    col_dict = {
        label: color
        for label, color in zip(g.edge_labels, colors.get_categorical(len(g.edge_labels)))
    }

    # Plot clustered matrix
    markov_gamma(
        g,
        alpha=2,
        beta=4.0,
        mu=3.0,
        gamma=2.0,
        local_buses=True,
        leafs=[n for n in g.leafs if n.kind == "component"],
    )

    markov_gamma(
        g,
        alpha=2,
        beta=3.5,
        mu=3.5,
        gamma=10.0,
        local_buses=True,
        leafs=[n for n in g.leafs if n.kind == "function_spec"],
    )

    style = raesl.plot.Style(
        ragraph=dict(
            piemap={"display": "labels", "mode": "relative"},
            palettes={"fields": col_dict},
            show_legend=True,
        )
    )

    depth = g.max_depth

    figures = [
        raesl.plot.mdm(
            g,
            node_kinds=["component", "function_spec"],
            edge_kinds=["functional_dependency", "mapping_dependency"],
            depth=i,
            style=style,
        )
        for i in range(depth)
    ]
    paths = [tmp_path / f"mdm-{i}.svg" for i in range(depth)]

    pio.write_images(
        fig=figures,
        file=paths,
        width=[fig.layout.width for fig in figures],
        height=[fig.layout.height for fig in figures],
        scale=1.0,
    )
