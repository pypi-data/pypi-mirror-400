# Changelog

## [0.16.2] - 2025-12-19

### Fixed

- Re-add and fix missing sections in component chapters for the new renderer approach.

## [0.16.1] - 2025-12-18

### Fixed

- Use new multi-export utility for figures by RaGraph which fixes faulty image sizing when flushing figures (inside the new renderer).

## [0.16.0] - 2025-12-12

### Added

- Added new [`raesl.render`][raesl.render] and [`raesl.l10n`][raesl.l10n] modules which are to replace the `raesl.doc` and `raesl.doc.locales` modules as the new implementation matures. It supports exporting specifications to Typst, PDF (through Typst), HTML and Markdown.

### Fixed

- Tinies of fixups in `pygments.py` and some typing in the Canopy export.
- Some test code maintenance.

## [0.15.0] - 2025-12-09

### Changed

- Major dependencies update. Only important or major versions shown or initial minor versions like `0.minor.patch`:
  - `graphviz` from `0.20.3` to `0.21.0`
  - `ipykernel` from `6.29.5` to `7.1.0`
  - `ipython` from `8.32.0` to `9.4.0`
- Moved plot functionality into main dependencies and install kaleido as plotly's extra `plotly[kaleido]` instead of as a separate dependency and updated from `6.0.0` to `6.5.0`.
- Reserved dependencies for the upcoming `render` module as an extra.
- Removed version identifiers from development dependency groups. We just assume the latest (compatible) dependencies are good enough.

## [0.14.6] - 2025-12-08

### Changed

- Updated the ordering of the internals of `esl_info` annotations in the different outputs to be `sorted(x)` lists instead of arbitrarily ordered collection types.

### Fixed

- Some internal formatting using ruff's import sorting.

## [0.14.5] - 2025-03-10

### Fixed

- Reinstated the `raesl[all]` extra to install all extras at once.

## [0.14.4] - 2025-02-14

### Fixed

- Fixed documentation errors throughout function documentation.

### Changed

- Changed documentation at https://raesl.ratio-case.nl to be built using MkDocs.

## [0.14.3] - 2025-02-04

### Changed

- Removed unused direct dependency on `numpy`.

## [0.14.2] - 2024-02-21

### Changed

- [`raesl.excel.component_overview`][raesl.excel.component_overview] has been updated to account for goal spec
  migration and goal specs that have no subclauses.

## [0.14.1] - 2024-02-06

### Changed

- [`raesl.canopy.add_canopy_annotations`][raesl.canopy.add_canopy_annotations] has been
  updated for better rendering within the Canopy app.

## [0.14.0] - 2024-02-01

### Added

- Generation of Excel with all active goal-requirements of a selected component.

## [0.13.2] - 2023-12-06

### Fixed

- Docs generation for cases with "minimized" and "maximized" in design rules.

## [0.13.1] - 2023-12-06

### Fixed

- Usage of bundles within a design rule results in a clear error (E228).

## [0.13.0] - 2023-12-06

### Added

- To canopy annotations for showing all specifications interactively within the canopy app.

## [0.12.5] - 2023-11-21

### Changed

- Updated dependencies.

## [0.12.4] - 2023-08-08

### Added

- Pygments entrypoint for syntax highlighting.

## [0.12.3] - 2023-07-04

### Fixed

- Solved the `DeprecationWarning` of `typing.io.IO` and changed to `typing.IO`.

## [0.12.2] - 2023-06-06

### Changed

- Updated Eisvogel Latex template.

## [0.12.1] - 2023-02-06

### Fixed

- Field filtering for `raeasl.plot.mdm`.

## [0.12.0] - 2022-10-26

### Added

- Added migration of design dependencies. That is, if a descendant of an ancestor _i_ has a design
  dependency with a descendant of an ancestor _j_, then ancestors _i_ and _j_ have a design
  dependency as well. This rule has been implemented.

## [0.11.1] - 2022-10-27

### Added

- A convenient 'all' extra to install all extras at once.

## [0.11.0] - 2022-07-16

### Changed

- Changed RaESL to be published on PyPI!
- New tasks, pipeline, tools, but no significant changes.

## 0.10.8

- Bug fix in Excel output generation.
- Added variable sheet to Excel output generation.

## 0.10.7

- Bug fix regarding the selection of component goals when generating PDF output.

## 0.10.6

- Bug fix regarding the directionality of design dependencies between variables derived from
  relations.

## 0.10.5

- Refactored dependency `ragraph.plot.colors` into [`ragraph.colors`][ragraph.colors].

## 0.10.4

- Fix for ARM architectures. Set Chromium flags to Kaleido image export in docs generation.

## 0.10.3

- Attempt to fix Kaleido versioning issues.

## 0.10.2

- Guard the command-line a little better against missing dependencies.
- Update to latest pygls for `raesl server`.

## 0.10.1

- Dependency updates.

## 0.10.0

- Added Excel generation functionality in the [`raesl.excel`][raesl.excel] subpackage. Usage is
  described in [Excel](./how-to-guides/excel.md).

## 0.9.0

- Documentation tags as proposed in [LEP0008]() have been implemented.

## 0.8.6

- Bug fix. Doc comments attached to variables are no longer duplicated in output.

## 0.8.5

- Bug fix regarding the handling of "minimum" and "maximum" in design specifications.

## 0.8.4

- Bug fix in [`raesl.plot`][raesl.plot] related to the displayed node sequence after clustering of
  non-lead node kinds.

## 0.8.3

- Several changes to [`raesl.doc`][raesl.doc] to improve readability of the generated outputs.
- Added section toggle arguments to [`reasl.doc.convert`][raesl.doc.convert] to allow a user to
  exclude specific sections from the generated document. By default all sections are included.

## 0.8.2

- Minor fixups.

## 0.8.1

- Improved the handling of bundles when generating a PDF document. Bundles are unfolded below the
  main specification text rather than within the main specification text.
- Added separate chapters for behavior specifications, needs, and design specifications that are not
  (in)directly related to components.
- Added `**metadata**` kwargs to [`reasl.doc.convert`][raesl.doc.convert] such that one can add a
  subtitle, date, author and logo to the title page of the generated PDF document.

## 0.8.0

- Added a convenient method to access `raesl doc`'s functionality from a Python script over at
  [`reasl.doc.convert`][raesl.doc.convert].
- Several further fixups to the [`raesl.doc`][raesl.doc] module.

## 0.7.3

- Add some backwards compatibility to the paths resolver so it handles lists as arguments, too.
  However, the recommended method is supplying multiple path arguments in an `*args` fashion.

## 0.7.2

- Bug fix regarding PDF document generation. Needs and design requirements that do not (indirectly)
  relate to components did not end up within the output document. Now they do.

## 0.7.1

- Modified the behavioral dependency derivation rules to detect logical dependencies between
  components and between function specifications. Path dependencies resulting from decomposing
  complex behavioral specifications into multiple smaller behavior specifications are now accounted
  for.

## 0.7.0

- Added a plotting module to generate figures tailored to the inspection of ESL specifications:
  - Matrix figures are made using Plotly and build on the foundations of
    [`ragraph.plot.mdm`][ragraph.plot.mdm]. For now, the only matrix figure is the
    [`raesl.plot.mdm`][raesl.plot.mdm], which is a Multi-Domain Matrix figure of (part of) an ESL
    spec.
  - Diagram figures are made using Graphviz and have some filtering in place to aid in inspecting
    the hierarchy, or reviewing the functional dependency network in various ways.
  - See [plotting usage](./how-to-guides/plot.md) for more information and examples.

## 0.6.0

- Add a convenient method for obtaining the [`Graph`][ragraph.graph.Graph] object from RaESL's compiler:
  `raesl.compile.to_graph`. It takes the exact same arguments as `raesl.compile.cli.run` but offers
  only the [`Graph`][ragraph.graph.Graph] as output for use in Python scripts.

## 0.5.6

- Bugfixes and fixups.

## 0.5.5

- Bug fix. `reasel.compile.instantiating.edge_building.EdgeFactory` is made more efficient.

## 0.5.4

- Bug fix. Set background.pdf path to unix path.

## 0.5.3

- Bug fix. Specification of units, domains and enumerations is no longer allowed in bundle fields.

## 0.5.2

- Update of `raesl.pygements.EslLexer`. Missing keywords are added.

## 0.5.1

- Bug fix. Implemented an identifier uniques check. This check ensures that all identifiers of ESL
  elements within the scope of a component definition are unique.

## 0.5.0

- Removed ESL 1.0 compiler from package.

## 0.4.8

- Bux fix. Dotted names are allowed as subject of needs. Bundles are no longer allowed.
- Bux fix. Breath first path finding method is corrected.

## 0.4.7

- Migration from Orca to Kaleido for static image generation (following Plotly's migration.

## 0.4.6

- Bug fix. The derivation of traceability dependencies between function specifications has been
  fixed.

## 0.4.5

- Update of raesl.doc such that is uses raesl.compile rather than raesl.compiler.

## 0.4.4

- Bug fix regarding asymetric product DSMs when plotting functional dependencies and the
  decomposition three has a depth \>= 3.

## 0.4.3

- Bug fix regarding DocComment handling when parsing multiple ESL files.
- DocComments are no long split in individual words. The are now stored as a list of full lines.

## 0.4.2

- Bug fix regarding the usage of bundles in goal-, transformation-, and relation speficiations.

## 0.4.1

- Update E202 and E203 for missing/unknown specification elements.
  - E202 now covers actually missing elements of a given kind.
  - E203 now covers unknown elements of a given kind.
  - Naming the unknown/missing "thing" is optional.

## 0.4.0

- Added a language server module. The language server can be started using `raesl serve` to start it
  using STDIO (use this in production) or `raesl serve -p <debug_port_number>` (use this when
  debugging). Currently, you can use this by building and installing the VS Code extension.
- Solved some cyclic imports that occurred when compiling the language server executable so we could
  ship it with the VS Code extension.

## 0.3.2

#### Bug fixes

- Fixed type assignment of variables that are part of a bundle.
- The function `utils.get_esl_paths` is modified to ignore folders starting with ".".
- All `yield` lines are removed from `edge_buidling.py` and replaced by `self._add()`\`

## 0.3.1

#### Bug fix

- The compiler no longer yields a syntax error when dotted names are used within goal,
  transformation, design, behavior, and relation specifications. Dotted names are required when one
  wants to use only a sub-element of a bundle.

## 0.3.0

#### Graph output creation

- Using `raesl.compile.cli.run` now returns an `ragraph.graph.Graph` object if a specification is
  compiled successfully. The returned `Graph` contains all specification elements (e.g. components,
  goals, transformations, etc) as `ragraph. node.Node` objects and all derived dependencies between
  them as `ragraph.edge.Edge` objects.

## 0.2.1

- Removed deprecated "problems" module entirely. Locations and positions should now be handled using
  the `raesl.types.Location` type.
- See `raesl.utils.get_location` for a shortcut to get a Location object quickly.

## 0.2.0

#### Revamp problem reporting

- Added some new classes of the Language Server Protocol.
- Usage of Diagnostics and Related Information to replace "Problems".
- Usage of centralized logging module to produce regular output.
- Usage of click to manage verbosity level on CLI.

## 0.1.0

- Add new compiler in parallel to the old one. After a full re-integration we should move to 1.0.0.
- The new compiler is "callable" using `raesl compile`, while the old one is put under
  `raesl compiler` (with r).

## 0.0.1

- Initial version from template.
