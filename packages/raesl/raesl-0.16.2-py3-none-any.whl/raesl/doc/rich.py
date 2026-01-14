"""Rich document content."""
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union

from ragraph.graph import Graph

import raesl.plot
from raesl import logger
from raesl.doc.locales import _

IMG_DIR = Path("./images")

DEFAULT_NODE_KINDS = ["component", "function_spec"]
DEFAULT_EDGE_KINDS = ["functional_dependency", "mapping_dependency"]
DEFAULT_PIE_MODE = "relative"


def mdm(
    graph: Graph,
    depth: int,
    rich: str = "tex",
    rich_opts: Dict[str, Any] = {},
    img_dir: Optional[Union[Path, str]] = None,
) -> Generator[str, None, None]:
    """Generate an Multi-Domain Matrix.


    Yields:
        Rich output lines.
    """
    logger.debug("Generating MDM for depth {}...".format(depth))

    img_dir = Path(img_dir if img_dir is not None else rich_opts.get("img_dir", IMG_DIR))
    img_dir.mkdir(parents=True, exist_ok=True)

    level = depth + 1

    style = raesl.plot.Style(
        ragraph=dict(
            piemap={
                "display": "labels",
                "mode": rich_opts.get("pie_mode", DEFAULT_PIE_MODE),
            }
        )
    )

    fig = raesl.plot.mdm(
        graph,
        node_kinds=rich_opts.get("node_kinds", DEFAULT_NODE_KINDS),
        edge_kinds=rich_opts.get("edge_kinds", DEFAULT_EDGE_KINDS),
        depth=level,
        style=style,
    )

    # Width of a pixel in mm on A4 paper with 96 dpi print quality.
    pix_in_mm = 0.26458
    # Width of a line on A4 paper with 20 mm side margins
    line_width = 170

    if fig.layout.width * pix_in_mm < line_width:
        fig_size = "width={:.3f}\\linewidth".format(fig.layout.width * pix_in_mm / line_width)
        angle = 0
    else:
        fig_size = "height={:.3f}\\linewidth".format(
            min(1.0, fig.layout.height * pix_in_mm / line_width)
        )
        angle = 90

    caption = _("{} dependency matrix of decomposition level {}.").format(
        " -- ".join(rich_opts.get("node_kinds", DEFAULT_NODE_KINDS)), level
    )

    img_path = str(img_dir / "level-{}".format(level))
    if not img_dir.is_absolute():
        img_path == "./" + img_path

    logger.debug("Generating image using Plotly's Kaleido...")
    try:
        import platform

        machine = platform.machine()
        if "arm" in machine or "aarch" in machine:
            import plotly.io as pio

            if "--single-process" not in pio.kaleido.scope.chromium_args:
                pio.kaleido.scope.chromium_args += ("--single-process",)

        if rich == "tex":
            img_path = f"{img_path}.pdf"
            fig.write_image(img_path)
            latex_path = img_path.replace("\\", "/").replace("_", "-underscore-")
            yield "\\begin{figure}[!htbp]"
            yield "\\centering"
            yield "\\includegraphics[{}, angle={}]{{{}}}".format(fig_size, angle, latex_path)
            yield "\\caption{{{}}}\\label{{{}}}".format(caption, "fig:mdmlevel" + str(level))
            yield "\\end{figure}"
            logger.debug("Included image as {}.".format(rich))

        elif rich == "md":
            img_path = f"{img_path}.svg"
            fig.write_image(img_path)
            yield "![{}\\label{{{}}}]({})".format(
                caption,
                "fig:mdmlevel" + str(level),
                img_path.replace("\\", "/").replace("_", "-underscore-"),
            )
            yield "\n"
            logger.debug("Included image as {}.".format(rich))
    except Exception as e:
        logger.error(
            "Something went wrong when generating images using Plotly's Kaleido. "
            + "Kaleido might not be available. "
            + "You can also disable rich output generation for now. "
        )
        raise e
