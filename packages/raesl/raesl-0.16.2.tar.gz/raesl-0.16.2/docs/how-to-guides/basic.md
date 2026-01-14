# Basic usage

Welcome to the RaESL usage documentation! This page covers the rudiments of how to compile an ESL
specification and convert it into an [`Graph`][ragraph.graph.Graph] object for further processing.

Usage of the [`raesl.plot`][raesl.plot] module for generating graphical views from ESL
specifications and the [`raesl.doc`][raesl.doc] module for converting ESL specifications into PDF
documents is discussed in the following documentation sections:

- [Plotting and visualization](./plot.md)
- [Document generation](./doc.md)
- [Excel workbook generation](./excel.md)

## Command-Line Interface

Most RaESL functionality is included in it's command line interface (CLI), which is available in
your terminal after installation. Suppose you have an ESL specification in a file named
`specification.esl`. You would then be able to compile it using:

```sh
raesl compile specification.esl
```

Simple as that! If the compiler doesn't find any errors, it will stay silent. For usage from a
Python script, please refer to the sections below.

For more info on the (sub-)commands supplied by RaESL, you can type `raesl --help` in your terminal.
You can use it for any of the following:

- `raesl compile`: Compiling ESL specification files or directories (optionally generating Graph
  output).
- `raesl doc`: Converting ESL specification files or directories into a PDF or formatted document.
- `raesl excel`: Converting ESL specification files or directories into an Excel workbook.
- `raesl jupyter`: Managing the RaESL Jupyter kernel.
- `raesl serve`: Starting the RaESL language server to support editors.
- `raesl version`: Display the installed RaESL version.

Command specific help is also available, which results in:

```sh
raesl compile --help
```

## Compiling ESL specifications

Compiling an ESL specification from a Python script can be done in one of two ways. If it is the
dependency [`Graph`][ragraph.graph.Graph] you're after, the best way to obtain it is using
**RaGraph**'s I/O module:

```python
from ragraph.io.esl import from_esl

graph = from_esl(path_to_esl_file)  # (e.g. "specification.esl")
```

which used the [`ragraph.io.esl.from_esl`][ragraph.io.esl.from_esl] method.

The second method is a little more elaborate and provides you with additional objects to explore
from the **RaESL** compile module itself:

```python
from raesl.compile.cli import run

diag_store, spec, graph = run(path_to_esl_file)  # (e.g. "specification.esl")
```

which returns three variables: `diag_store` which is an
[`DiagnosticStore`][raesl.compile.diagnostics.DiagnosticStore] object that contains all diagnostics
information such as warnings and errors; `spec` which is an
[`Specification`][raesl.compile.ast.specification.Specification] object that contains the specified
type, verb, relation and component definitions; and `graph` which is an
[`ragraph.graph.Graph`][ragraph.graph.Graph] object that contains all nodes and edges that have been
derived from the compiled specification.

### Multi-file input

As your specification grows, it might be beneficial to split it into multiple files. The compiler
can handle this without any problem! The ESL compiler will walk through the (component)
instantiation tree starting at the `world` definition and collect and instantiate the required
definitions from your provided ESL files. Hence, the list of provided ESL files should only contain
a single `world` definition.

Suppose your ESL files are all in one directory, you would then be able to obtain the
[`Graph`][ragraph.graph.Graph] like so:

```python
from ragraph.io.esl import from_esl

graph = from_esl(path_to_esl_dir)  # (e.g. "./specification")
```

You can also supply any number of file and directory path arguments to the
[`ragraph.io.esl.from_esl`][ragraph.io.esl.from_esl] and
[`raesl.compile.cli.run`][raesl.compile.cli.run] methods and they will be used to discover all
available ESL files:

```python
from ragraph.io.esl import from_esl

graph = from_esl(
    path_to_esl_dir, path_to_extra_esl_file
)  # (e.g. "specification/", "extra-file.esl")
```

!!! note

    As a rule of thumb we advice to create a separate ESL file for each component definition. This
    limits the size of individual ESL files which benefits clarity.

### Multiple use-cases / scenarios

At some point, you might want to investigate multiple use-cases or scenarios that have quite some
definitions in common. As an example, you could organize your files like this:

```tree
project
├── scenarios
│   ├── scenario1.esl
│   └── scenario2.esl
└── definitions
    ├── types.esl
    ├── user.esl
    ├── component1.esl
    ├── component2.esl
    └── component3.esl
```

Where you organize your `scenarios` (i.e. world definitions) into a separate folder. You can then
compile this specification by specifying the scenario **file** and definitions **directory**. Lets
assume that in `scenario1`, we supply something to a `user` component using a system comprised of
`component1` and in `scenario2` we do this using `component2` and `component3`. If we didn't make
any syntax errors, the compiler will then be able to compile both scenarios without any problems
using:

```sh
raesl compile ./definitions ./scenarios/scenario1.esl
```

or from Python:

```python { skip="True" }
from ragraph.io.esl import from_esl

graph = from_esl("./definitions", "./scenarios/scenario1.esl")
```

This way, you don't need to duplicate anything that is present in both scenarios! Types, relations,
common components: they are all (re-)used automatically.
