"""Document module."""

import logging
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional, Set, Union

import raesl.doc.lines as lns
import raesl.doc.rich as rich
import raesl.doc.sections as secs
from raesl import logger
from raesl.doc.locales import register_locale

# Compile module is excluded during docs generation.
try:
    from raesl.compile import cli
except ImportError:
    pass

TEMPLATES = Path(__file__).parent / "templates"


class Doc:
    """Output document.

    Arguments:
        paths: ESL input files.
        language: Output language.
        prologue: Markdown document to include as a prologue.
        epilogue: Markdown document to include as a conclusion.
        goal_section: Goal section toggle.
        transformation_section: Transformation section toggle.
        behavior_section: Behavior section toggle.
        design_section: Design section toggle.
        need_section: Need section toggle.
        relation_section: Need section toggle.
        var_table: Var table toggle.
        rich: Format to create rich output content in, defaults to 'tex'.
        rich_opts: Rich output generation options.

    Keyword Arguments: Document metadata. See pandoc documentation.
    """

    # Format used when exporting to a Markdown file.
    markdown_file_format = "markdown+table_captions+multiline_tables+pipe_tables"

    # Format used in Doc generation.
    markdown_generated = "markdown+table_captions+multiline_tables+pipe_tables+grid_tables"

    def __init__(
        self,
        *paths: Union[str, Path],
        language: str = "en",
        prologue: Optional[Path] = None,
        epilogue: Optional[Path] = None,
        goal_section: bool = True,
        transformation_section: bool = True,
        behavior_section: bool = True,
        design_section: bool = True,
        need_section: bool = True,
        relation_section: bool = True,
        var_table: bool = True,
        rich: Optional[str] = "tex",
        rich_opts: Optional[Dict[str, Any]] = None,
        esl_paths: Optional[Union[List[str], List[Path]]] = None,
        **metadata,
    ):
        if esl_paths is not None:
            msg = " ".join(
                (
                    "The 'esl_paths' keyword argument will be deprecated.",
                    "Please use your file and directory paths as (any number of)",
                    "positional arguments to this function.",
                )
            )
            logger.warning(msg)
            paths = tuple(esl_paths)

        self.language = language
        register_locale(language)

        self.prologue = Path(prologue).read_text(encoding="utf-8") if prologue else None
        self.epilogue = Path(epilogue).read_text(encoding="utf-8") if epilogue else None

        self.goal_section = goal_section
        self.transformation_section = transformation_section
        self.behavior_section = behavior_section
        self.design_section = design_section
        self.need_section = need_section
        self.relation_section = relation_section
        self.var_table = var_table

        self.rich = rich
        self.rich_opts = rich_opts or dict()

        logger.debug("Parsing metadata {}...".format(metadata))
        self.metadata = {
            "book": True,
            "documentclass": "scrbook",
            "geometry": "margin=2.5cm",
            "graphics": True,
            "papersize": "a4",
            "titlepage": True,
            "titlepage-color": "1c3b6c",
            "titlepage-text-color": "ffffff",
            "titlepage-rule-color": "ffffff",
            "titlepage-background": (TEMPLATES / "background.pdf").as_posix(),
            "toc-own-page": True,
            "top-level-division": "chapter",
            "first-chapter": 1,
        }

        if metadata:
            self.metadata.update(metadata)

        self.metadata["lang"] = self.language

        logger.debug("Parsing ESL files...")

        self.diag_store, _, self.graph = cli.run(*paths)

        if self.diag_store.diagnostics:
            self.diag_store.dump()

        logger.debug("Parsing graph to a document...")
        self.pars: List[Par] = []
        self.parse_esl()

    def parse_esl(self):
        """Parse an ESL output Graph"""
        if self.prologue:
            self.pars = [Par([self.prologue])]

        g = self.graph

        comps = g["world"].children
        comps = sorted(comps, key=lambda x: x.name)
        depth = 0
        h = 1

        while comps:
            # Add chapter introduction.
            logger.debug("Processing nodes at level {}...".format(depth))
            self.pars.append(
                Par(
                    secs.node_decomp_level(
                        depth, comps, h=h, rich=self.rich, rich_opts=self.rich_opts
                    )
                )
            )
            # Add MDM figure in rich mode.
            if self.rich:
                logger.debug("Adding MDM image at level {}...".format(depth))
                self.pars.append(
                    Par(
                        rich.mdm(
                            graph=self.graph,
                            depth=depth,
                            rich=self.rich,
                            rich_opts=self.rich_opts,
                        )
                    )
                )

            # Add bundle information
            self.set_var_bundle_roots()

            for comp in comps:
                logger.debug("Adding sections for node {}...".format(comp.name))
                self.pars.append(Par(lns.lines(comp, h=h + 1)))
                self.pars.append(Par(secs.comp_node_props(comp, g, h + 2)))
                if self.goal_section:
                    self.pars.append(Par(secs.comp_node_goal_reqs(comp, g, h + 2)))
                    self.pars.append(Par(secs.comp_node_goal_cons(comp, g, h + 2)))

                if self.transformation_section:
                    self.pars.append(Par(secs.comp_node_transformation_reqs(comp, g, h + 2)))
                    self.pars.append(Par(secs.comp_node_transformation_cons(comp, g, h + 2)))

                if self.behavior_section:
                    self.pars.append(Par(secs.comp_node_behavior_reqs(comp, g, h + 2)))
                    self.pars.append(Par(secs.comp_node_behavior_cons(comp, g, h + 2)))

                if self.design_section:
                    self.pars.append(Par(secs.comp_node_design_reqs(comp, g, h + 2)))
                    self.pars.append(Par(secs.comp_node_design_cons(comp, g, h + 2)))

                if self.need_section:
                    self.pars.append(Par(secs.comp_node_needs(comp, g, h + 2)))

                if self.relation_section:
                    self.pars.append(Par(secs.comp_node_relations(comp, g, h + 2)))

                self.pars.append(Par(secs.comp_node_subcomps(comp, h + 2)))

            children = []
            for comp in comps:
                children.extend(comp.children)
            comps = children
            depth += 1

        # Check for any miscellaneous needs and design specifications that haven't
        # been printed yet.
        gn = [line for line in secs.global_needs(g, h + 1) if self.need_section]
        gdr = [line for line in secs.global_design_reqs(g, h + 1) if self.design_section]
        gdc = [line for line in secs.global_design_cons(g, h + 1) if self.design_section]
        if len(gn) > 0 or len(gdr) > 0 or len(gdc) > 0:
            self.pars.append(Par(secs.global_needs_and_designs(h)))
            self.pars.append(Par(gn))
            self.pars.append(Par(gdr))
            self.pars.append(Par(gdc))

        if self.epilogue:
            logger.debug("Adding epilogue...")
            self.pars.append(Par([self.epilogue]))

        # Appendices
        if self.var_table:
            logger.debug("Adding appendices...")
            self.pars.append(Par(["\\appendix{}", "\\appendixpage{}"]))
            self.pars.append(Par(secs.var_node_table(g, h=1)))

    @property
    def as_markdown(self) -> str:
        """Markdown representation of this document."""
        return "\n".join(self.yield_markdown())

    def yield_markdown(self) -> Generator[str, None, None]:
        """Yield markdown lines."""
        yield from self.yield_metadata()
        yield from self.yield_pars()

    def yield_metadata(self) -> Generator[str, None, None]:
        """Yield metadata lines."""
        yield "---"
        for key, value in self.metadata.items():
            yield "{}: {}".format(key, value)
        yield "---"

    def yield_pars(self) -> Generator[str, None, None]:
        """Yield all paragraph texts."""
        for par in self.pars:
            yield par.md

    def save(
        self,
        path: Union[Path, str],
        to: Optional[str] = None,
        pandoc_args: List[str] = [
            "--standalone",
            "--number-sections",
            "--toc",
            "--listings",
            "--self-contained",
        ],
        filters: List[str] = ["pandoc-fignos"],
    ):
        """Save document as a file.

        Arguments:
            path: Path to save to.
            to: Optional format to save to. Normally derived from path.
            pandoc_args: Additional arguments for pandoc conversion tool.
            filters: Pandoc filters to use.
        """
        import pypandoc

        path = Path(path)
        if to is None:
            to = path.suffix.lstrip(".")
            if to == "html":
                to == "html5"
        pandoc_args = pandoc_args.copy()
        filters = filters.copy()

        # Fix LaTeX incompatibilities.
        if (to == "tex" or to == "pdf") and self.rich == "md":
            self.rich = "tex"
            self.parse_esl()

        if logger.level <= logging.DEBUG and to != "md":
            logger.debug("Saving Markdown file for debugging purposes...")
            try:
                pypandoc.convert_text(
                    self.as_markdown,
                    self.markdown_file_format,
                    format=self.markdown_generated,
                    outputfile=str(path.with_suffix(".md")),
                    encoding="utf-8",
                    extra_args=pandoc_args,
                    filters=filters,
                )
            except RuntimeError as exc:
                logger.error(str(exc))

        if to == "pdf" or to == "latex":
            template = (TEMPLATES / "eisvogel.latex").resolve()
            pandoc_args.extend(["--template", str(template)])

        if logger.level <= logging.DEBUG and to != "latex":
            try:
                logger.debug("Saving LaTeX file for debugging purposes...")
                pypandoc.convert_text(
                    self.as_markdown,
                    "latex",
                    format=self.markdown_generated,
                    outputfile=str(path.with_suffix(".tex")),
                    encoding="utf-8",
                    extra_args=pandoc_args,
                    filters=filters,
                )
            except RuntimeError as exc:
                logger.error(str(exc))

        logger.debug("Converting to {}...".format(to.upper()))

        # Convert and save.
        try:
            pypandoc.convert_text(
                self.as_markdown,
                to,
                format=self.markdown_generated,
                outputfile=str(path),
                encoding="utf-8",
                extra_args=pandoc_args,
                filters=filters,
            )
        except RuntimeError as exc:
            logger.error(str(exc))
            raise exc

    def get_bundle_name_parts(self) -> Set[str]:
        """Get set of all name parts of bundles used within the spec

        Returns:
            Set of all name parts of bundles.
        """
        vnames = [n.name for n in self.graph.get_nodes_by_kind("variable")]
        cnames = [n.name for n in self.graph.get_nodes_by_kind("component")]

        cname_parts = set()
        for name in cnames:
            cname_parts.update(set(name.split(".")))

        vname_parts = set()
        for name in vnames:
            vname_parts.update(set(name.split(".")[:-1]))

        return vname_parts - cname_parts

    def set_var_bundle_roots(self):
        """Set the bundle root of variables if they originate from a bundle."""
        bnps = self.get_bundle_name_parts()
        for v in self.graph.get_nodes_by_kind("variable"):
            v.annotations.esl_info["bundle_root_name"] = get_bundle_root(
                vname=v.name, bundle_name_parts=bnps
            )


class Par:
    """Paragraph.

    Arguments:
        lines: Lines of this paragraph.
        obj: Object of this paragraph.

    Attributes:
        md: Markdown representation.
    """

    def __init__(self, lines: Iterable[str], obj: Optional[Any] = None):
        self.md = "\n".join(lines) + "\n"
        self.md = self.md.replace("_", " ").replace(" ->", " &rarr;")
        self.md = self.md.replace("-underscore-", "_")
        self.obj = obj


def get_bundle_root(vname: str, bundle_name_parts: Set) -> Union[None, str]:
    """Check if variable originates from a bundle and return the name
    of the root of the bundle.

    Arguments:
        vname: Name of the variable to check.
        bundle_name_parts: Set of strings the comprise bundle names.

    Returns:
       None or Name of the root of the bundle from which the variable originates.
    """
    bundle_root = None
    name_parts = vname.split(".")

    if name_parts[-2] not in bundle_name_parts:
        # Variable did not originate from a bundle:
        return bundle_root

    for idx in range(2, len(name_parts) + 1):
        if name_parts[-idx] in bundle_name_parts:
            bundle_root = name_parts[-idx]
        else:
            # Location part of varaible name has been entered
            break

    return bundle_root
