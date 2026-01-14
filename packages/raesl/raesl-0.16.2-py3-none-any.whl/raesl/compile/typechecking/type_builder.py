"""Class for constructing types."""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from raesl.compile import diagnostics, scanner
from raesl.compile.ast import exprs, types
from raesl.compile.ast.specification import Specification
from raesl.compile.typechecking.orderer import Orderer

if TYPE_CHECKING:
    from raesl.compile.scanner import Token
    from raesl.compile.typechecking.ast_builder import AstBuilder
    from raesl.compile.typechecking.orderer import OrdererEntry
    from raesl.types import Location

STANDARD_TYPE_NAMES = ("real", "integer", "string", "boolean")


class TempTypeDef:
    """Temporary storage of a type definition."""

    def __init__(
        self,
        type_name: "Token",
        parent_name: Optional["Token"],
        enum_spec: Optional[List[exprs.Value]],
        unit_spec: Optional[List["Token"]],
        ival_spec: Optional[List[Tuple[Optional[exprs.Value], Optional[exprs.Value]]]],
        cons_spec: Optional[exprs.Value],
    ):
        self.type_name = type_name
        self.parent_name = parent_name
        self.enum_spec = enum_spec
        self.unit_spec = unit_spec
        self.ival_spec = ival_spec
        self.cons_spec = cons_spec


class TempFieldDef:
    """Temporary storage of a field in a bundle."""

    def __init__(
        self,
        field_name: "Token",
        type_name: Optional["Token"],
    ):
        self.field_name = field_name
        self.type_name = type_name


class TempBundleDef:
    """Temporary storage of a bundle definition."""

    def __init__(self, bundle_name: "Token"):
        self.bundle_name = bundle_name
        self.bundle_fields: List[TempFieldDef] = []


class TypeBuilder:
    """Builder to construct types of the specification.

    Arguments:
        ast_builder: AST builder instance.

    Attributes:
        diag_store: Storage for found diagnostics.
        type_defs: Found type definitions in the specification, temporarily stored until
            all type information is available.
        bundle_defs: Found bundle definitions in the specification, temporarily stored
            until all type information is available.
        current_bundle: If not None, reference to the last opened bundle definition
            for adding additional fields to it.
    """

    def __init__(self, ast_builder: "AstBuilder"):
        # Make the builder problem store available locally.
        self.diag_store = ast_builder.diag_store

        # Setup type data storage.
        self.type_defs: List[TempTypeDef] = []
        self.bundle_defs: List[TempBundleDef] = []
        self.current_bundle: Optional[TempBundleDef] = None
        self.types_with_error: Optional[Dict[str, Token]] = (
            None  # typedefs that were not added setup during type construction.
        )

        ast_builder.register_new_section(self)

    def notify_new_section(self, _new_top_section: bool):
        """Notification that type additions have finished."""
        self.current_bundle = None

    @staticmethod
    def get_entry_location(entry: "OrdererEntry") -> "Location":
        """Retrieve position information from a type entry.

        Arguments:
            entry: Entry to use.

        Returns:
            Position information of the entry.
        """
        if isinstance(entry.data, TempTypeDef):
            return entry.data.type_name.get_location()
        else:
            assert isinstance(entry.data, TempBundleDef)
            return entry.data.bundle_name.get_location()

    @staticmethod
    def add_standard_types(resolved_types: Dict[str, types.TypeDef]):
        """Add all standard types to the resolved types."""
        for name in STANDARD_TYPE_NAMES:
            name_tok = scanner.Token("NAME", name, "ESL-compiler", 0, 0, 0)
            standard_type = types.ElementaryType(None, [], None)
            typedef = types.TypeDef(name_tok, standard_type)

            assert name not in resolved_types
            resolved_types[name] = typedef

    def finish(self, spec: Specification):
        """Check the collected types and bundles, report any errors, and add them
        to the specification.

        Arguments:
            spec: Specification to extend with the found types.
        """
        self.current_bundle = None  # Likely not needed, but it's safe.

        orderer = Orderer()

        # Add type definitions.
        for tdef in self.type_defs:
            if tdef.parent_name is None:
                needs = []
            else:
                needs = [tdef.parent_name.tok_text]

            # Check for duplicate use of the name as a type.
            entry = orderer.find_entry(tdef.type_name.tok_text)
            if entry is not None:
                locs = [
                    tdef.type_name.get_location(),
                    TypeBuilder.get_entry_location(entry),
                ]
                self.diag_store.add(
                    diagnostics.E200(
                        tdef.type_name.tok_text,
                        "type definition",
                        location=locs[0],
                        dupes=locs,
                    )
                )
                continue

            orderer.add_dependency(tdef.type_name.tok_text, needs, tdef)

        # Add bundle definitions
        for bdef in self.bundle_defs:
            needs = set()
            field_names = {}
            for bfield in bdef.bundle_fields:
                # Verify unique field names.
                field_name = bfield.field_name.tok_text
                if field_name in field_names:
                    locs = [
                        field_names[field_name].get_location(),
                        bfield.field_name.get_location(),
                    ]
                    self.diag_store.add(
                        diagnostics.E200(
                            field_name,
                            "Bundle field name",
                            location=locs[0],
                            dupes=locs,
                        )
                    )
                    # Continue anyway

                if bfield.type_name is not None:
                    needs.add(bfield.type_name.tok_text)

            # Check for duplicate use of the name as a type.
            entry = orderer.find_entry(bdef.bundle_name.tok_text)
            if entry is not None:
                locs = [
                    bdef.bundle_name.get_location(),
                    TypeBuilder.get_entry_location(entry),
                ]
                # Type name is used for more than one type
                self.diag_store.add(
                    diagnostics.E200(
                        bdef.bundle_name.tok_text, "type", location=locs[0], dupes=locs
                    )
                )
                continue

            orderer.add_dependency(bdef.bundle_name.tok_text, list(needs), bdef)

        # Let the orderer decide on an order of processing, and process the result.
        resolved, cycle = orderer.resolve()

        self.types_with_error = {}
        """(str -> Token) Types that are defined in the spec but something was wrong."""

        resolved_types = {}
        """Dict of name-string to types.TypeDef."""

        # Make standard types generally available for the entire specification.
        TypeBuilder.add_standard_types(resolved_types)

        for entry in resolved:
            if entry.data is None:
                # Entry was created by the orderer, we should run into it again and fail
                # to find it.
                continue

            if isinstance(entry.data, TempTypeDef):
                self._make_typedef(entry.data, resolved_types)
            else:
                assert isinstance(entry.data, TempBundleDef)
                self._make_bundledef(entry.data, resolved_types)

        self.types_with_error = None

        if cycle:
            locs = [TypeBuilder.get_entry_location(entry) for entry in cycle]
            name = cycle[0].name
            self.diag_store.add(
                diagnostics.E204(name, "type definition", location=locs[0], cycle=locs)
            )

        # Store output
        spec.types = resolved_types

    def _construct_type(
        self,
        parent_name: Optional["Token"],
        enum_spec: Optional[List[exprs.Value]],
        unit_spec: Optional[List["Token"]],
        ival_spec: Optional[List[Tuple[Optional[exprs.Value], Optional[exprs.Value]]]],
        cons_spec: Optional[exprs.Value],
        prefer_parent: bool,
        resolved_types: Dict[str, types.TypeDef],
    ) -> Optional[types.BaseType]:
        """Construct a new type from the given parameters.

        Arguments:
            prefer_parent: If possible, don't make a new type.

        Returns:
            The parent type if nothing changed, the constructed ElementaryType if
                something was extended, or None if construction failed.
        """
        # Find parent type, and verify we can extend it if needed.
        parent_type: Optional[types.BaseType]
        if parent_name is None:
            parent_type = None
        else:
            # Type should be available.
            parent_typedef = resolved_types.get(parent_name.tok_text)
            if parent_typedef is None:
                # Not available, perhaps an error happened with that type?
                assert self.types_with_error is not None
                parent_def_tok = self.types_with_error.get(parent_name.tok_text)

                if parent_def_tok:
                    # Parent was defined but failed with an error.
                    self.diag_store.add(
                        diagnostics.E214(
                            parent_name.tok_text,
                            location=parent_name.get_location(),
                            def_location=parent_def_tok.get_location(),
                        )
                    )
                else:
                    # Parent was never defined at all.
                    self.diag_store.add(
                        diagnostics.E203(
                            "type",
                            name=parent_name.tok_text,
                            location=parent_name.get_location(),
                        )
                    )
                return None

            parent_type = parent_typedef.type
            is_extended = (
                (enum_spec is not None)
                or (unit_spec is not None)
                or (ival_spec is not None)
                or (cons_spec is not None)
            )

            if not isinstance(parent_type, types.ElementaryType):
                # Parent is a compound, type cannot be extended.
                if is_extended:
                    self.diag_store.add(
                        diagnostics.E215(parent_name.tok_text, location=parent_name.get_location())
                    )
                    return None

                return parent_type

            # Parent is an elementary type.
            if not is_extended and prefer_parent:
                # No extension and a parent type is preferred.
                return parent_type

        # Check the data of the new type.
        #
        # Process units.
        available_units: Dict[str, "Token"] = {}
        if parent_type:
            available_units = dict((tok.tok_text, tok) for tok in parent_type.units)
        else:
            available_units = {}

        type_units = []
        if unit_spec:
            for unit in unit_spec:
                unit_text: str = unit.tok_text
                # Check for not having '[xyz]' or '-'.
                if unit_text.startswith("[") and unit_text.endswith("]"):
                    self.diag_store.add(
                        diagnostics.E216(unit.tok_text, location=unit.get_location())
                    )
                    return None
                if unit_text == "-":
                    self.diag_store.add(diagnostics.E217(location=unit.get_location()))
                    return None

                if unit_text in available_units:
                    self.diag_store.add(
                        diagnostics.W200(unit.tok_text, "unit", location=unit.get_location())
                    )
                    continue  # Silently discard duplicates.

                type_units.append(unit)
                available_units[unit_text] = unit

        # Build intervals
        type_intervals: Optional[List[Tuple[Optional[exprs.Value], Optional[exprs.Value]]]]
        type_intervals = None

        if ival_spec:
            type_intervals = ival_spec

        if enum_spec:
            assert not type_intervals
            type_intervals = [(val, val) for val in enum_spec]

        if cons_spec:
            assert not type_intervals
            type_intervals = [(cons_spec, cons_spec)]

        if not type_intervals:
            type_intervals = []

        if parent_type and prefer_parent and not type_units and not type_intervals:
            # An extension was specified but nothing changed, keep the parent if
            # preferred.
            return parent_type

        # Verify units of the type limits.
        for low_val, high_val in type_intervals:
            self.check_unit(low_val, available_units)
            self.check_unit(high_val, available_units)

        assert type_intervals is not None
        return types.ElementaryType(parent_type, type_units, type_intervals)

    def _check_override_standard_type(self, type_name: "Token") -> bool:
        """Check whether the new type tries to override a standard type. Give an error
        if it does.

        Returns:
            True if the new type is a standard type, else False.
        """
        if type_name.tok_text in STANDARD_TYPE_NAMES:
            self.diag_store.add(
                diagnostics.E218(type_name.tok_text, location=type_name.get_location)
            )
            return True
        return False

    def _make_typedef(self, tdef: TempTypeDef, resolved_types: Dict[str, types.TypeDef]):
        """Add the type definition to the resolved collection. It is assumed the
        dependencies are already available (as ensured by the Orderer).
        """
        if self._check_override_standard_type(tdef.type_name):
            return  # Something failed and was reported.

        new_type = self._construct_type(
            tdef.parent_name,
            tdef.enum_spec,
            tdef.unit_spec,
            tdef.ival_spec,
            tdef.cons_spec,
            False,
            resolved_types,
        )
        if new_type is None:
            assert self.types_with_error is not None
            self.types_with_error[tdef.type_name.tok_text] = tdef.type_name
            return  # Something failed and was reported.

        typedef = types.TypeDef(tdef.type_name, new_type)
        assert typedef.name.tok_text not in resolved_types
        resolved_types[typedef.name.tok_text] = typedef

    def _make_bundledef(self, bdef: TempBundleDef, resolved_types: Dict[str, types.TypeDef]):
        """Add the bundle definition to the resolved collection. It is assumed the
        dependencies are already available (as ensured by the Orderer).
        """
        if self._check_override_standard_type(bdef.bundle_name):
            return

        fields = []
        field_names: Dict[str, "Token"] = {}  # For duplicate field name detection.
        failed = False
        for field in bdef.bundle_fields:
            new_type = self._construct_type(
                field.type_name,
                None,
                None,
                None,
                None,
                True,
                resolved_types,
            )
            if not new_type:
                assert self.types_with_error is not None
                self.types_with_error[bdef.bundle_name.tok_text] = bdef.bundle_name
                failed = True
                continue  # But continue looking for more errors.

            if field.field_name.tok_text in field_names:
                # Duplicate field, discard. Above it was already reported.
                continue

            field_names[field.field_name.tok_text] = field.field_name
            fields.append(types.CompoundField(field.field_name, new_type))

        if failed:
            # Some error was detected, bail out.
            return

        new_bundle = types.Compound(fields)
        typedef = types.TypeDef(bdef.bundle_name, new_bundle)
        assert typedef.name.tok_text not in resolved_types
        resolved_types[typedef.name.tok_text] = typedef

    def add_typedef(
        self,
        type_name: "Token",
        parent_name: Optional["Token"],
        enum_spec: Optional[List[exprs.Value]],
        unit_spec: Optional[List["Token"]],
        ival_spec: Optional[List[Tuple[Optional[exprs.Value], Optional[exprs.Value]]]],
        cons_spec: Optional[exprs.Value],
    ):
        """The parser found a new type definition entry, store it."""
        temp_tdef = TempTypeDef(type_name, parent_name, enum_spec, unit_spec, ival_spec, cons_spec)
        self.type_defs.append(temp_tdef)
        self.current_bundle = None

    def new_bundle_type(self, bundle_name: "Token"):
        """The parser found a new bundle in the source code, create it."""
        temp_bdef = TempBundleDef(bundle_name)
        self.bundle_defs.append(temp_bdef)
        self.current_bundle = temp_bdef

    def add_bundle_field(
        self,
        field_name: "Token",
        type_name: Optional["Token"],
    ):
        """A new field in the current bundle has been found by the parser, add it."""
        temp_fdef = TempFieldDef(field_name, type_name)
        assert self.current_bundle, "Trying to add a bundle field outside a type section."
        self.current_bundle.bundle_fields.append(temp_fdef)

    def check_unit(self, value: Optional[exprs.Value], available_units: Dict[str, "Token"]) -> None:
        """Check whether the unit possibly specified in 'value' is available for use.
        Report an error if it is not available.
        """
        if value is None or value.unit is None:
            return

        units = value.get_units()
        if units is None:
            return

        if units.intersection(available_units):
            return  # Value uses a known unit.

        unit_text = value.unit.tok_text
        if unit_text.startswith("[") and unit_text.endswith("]"):
            unit_text = unit_text[1:-1]
        self.diag_store.add(diagnostics.E219(unit_text, location=value.unit.get_location()))
