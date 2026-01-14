"""Collect and process relation definition that are found by the parser."""

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional

from raesl.compile import diagnostics
from raesl.compile.ast import relations

if TYPE_CHECKING:
    from raesl.compile.ast.specification import Specification
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder

INPUT = relations.INPUT
OUTPUT = relations.OUTPUT
INPOUT = relations.INPOUT


class RelationDefBuilder:
    """Builder to construct relation definitions.

    Arguments:
        ast_builder: AST builder instance.

    Attributes:
        diag_store: Storage for found diagnostics.
        rel_defs: Created relation definitions while collecting data from parsing.
        current_reldef: Reference to the entry in 'rel_defs' that is being filled.
        last_occurrences: Map of input/output directions to token of last occurrence
            of that direction in the current definition.
        current_direction: Parameter direction to attach to a new parameter.
    """

    def __init__(self, ast_builder: "AstBuilder"):
        self.diag_store = ast_builder.diag_store

        self.rel_defs: Optional[List[relations.RelationDefinition]] = []
        self.current_reldef: Optional[relations.RelationDefinition] = None
        self.last_occurrences: Dict[str, "Token"] = {}
        self.current_direction: Optional[str] = None

        ast_builder.register_new_section(self)

    def notify_new_section(self, _new_top_section: bool):
        """Parser found a new section, drop all 'in-progress' relation definition
        construction.
        """
        self.current_reldef = None
        self.last_occurrences = {}
        self.current_direction = None

    def add_reldef(self, name: "Token"):
        """Add a new relation definition. Parameters will follow.

        Arguments:
            name: Name of the relation definition.
        """
        assert self.rel_defs is not None

        reldef = relations.RelationDefinition(name)
        self.rel_defs.append(reldef)
        self.current_reldef = reldef
        self.last_occurrences = {}
        self.current_direction = None

    def reldef_param_header(self, header_tok: "Token", direction: str):
        """New parameter subsection with a direction. Set the direction for the
        parameters that will follow.

        Arguments:
            header_tok: Token of the direction, for deriving position information if
                needed.
            direction: Direction of the next parameters of the relation definition.
        """
        assert self.current_reldef is not None

        last_occurrence = self.last_occurrences.get(direction)
        if last_occurrence is not None:
            direction_text = {
                INPUT: "require",
                OUTPUT: "returning",
                INPOUT: "relating",
            }[direction]
            locs = [header_tok.get_location(), last_occurrence.get_location()]
            self.diag_store.add(
                diagnostics.E200(direction_text, "parameter section", location=locs[0], dupes=locs)
            )
            # Continue anyway

        self.last_occurrences[direction] = header_tok
        self.current_direction = direction

    def reldef_add_param(self, name: "Token", type_name: "Token", multi: bool):
        """Add a parameter to the current relation definition."""
        assert self.current_direction is not None
        assert self.current_reldef is not None

        rel_param = relations.RelationDefParameter(name, type_name, self.current_direction, multi)
        self.current_reldef.params.append(rel_param)

    def finish(self, spec: "Specification"):
        """Check the relation definitions and add them to the result specification."""
        reldef_texts: Dict[
            str, "Token"
        ] = {}  # Map of defined names for relation definitions to their token.
        assert self.rel_defs is not None
        for rel_def in self.rel_defs:
            # Verify unique name.
            reldef_text = rel_def.name.tok_text
            if reldef_text in reldef_texts:
                locs = [
                    rel_def.name.get_location(),
                    reldef_texts[reldef_text].get_location(),
                ]
                self.diag_store.add(
                    diagnostics.E200(
                        reldef_text, "relation definition", location=locs[0], dupes=locs
                    )
                )
                continue

            reldef_texts[reldef_text] = rel_def.name

            # Verify parameters.
            multi_value_params: Dict[str, List[relations.RelationDefParameter]] = defaultdict(
                list
            )  # Multi-value params in each direction.
            param_texts: Dict[str, "Token"] = {}  # Map of defined parameter names to their token.
            for param in rel_def.params:
                # Register multi-value params.
                if param.multi:
                    multi_value_params[param.direction].append(param)

                # Check unique name.
                param_text = param.name.tok_text
                if param_text in param_texts:
                    locs = [
                        param.name.get_location(),
                        param_texts[param_text].get_location(),
                    ]
                    self.diag_store.add(
                        diagnostics.E200(
                            param_text,
                            "parameter definition",
                            location=locs[0],
                            dupes=locs,
                        )
                    )
                    # Continue anyway

                param_texts[param_text] = param.name

                # check type.
                type_text = param.type_name.tok_text
                typedef = spec.types.get(type_text)
                if typedef is None:
                    loc = param.type_name.get_location()
                    self.diag_store.add(diagnostics.E203("type", name=type_text, location=loc))

                    param.type = None
                else:
                    param.type = typedef.type

            # Verify lack of more than one multi-value parameter in each direction.
            found_fatal = False
            for mv_params in multi_value_params.values():
                if len(mv_params) > 1:
                    locs = [mvp.name.get_location() for mvp in mv_params]
                    direction_text = {
                        INPUT: "requiring",
                        OUTPUT: "returning",
                        INPOUT: "relating",
                    }[mv_params[0].direction]
                    self.diag_store.add(
                        diagnostics.E213(
                            f"'{direction_text}' multi-value parameter",
                            len(mv_params),
                            "at most 1",
                            location=locs[0],
                            occurrences=locs,
                        )
                    )
                    found_fatal = True

            if found_fatal:
                continue  # Fatal error.

        spec.rel_defs = self.rel_defs
        self.rel_defs = None  # Avoid adding more relation definitions.
