# Ratio ESL

Ratio support for the Elephant Specification Language (ESL) in Python.

## Quickstart

### Installation

RaESL can be installed using `pip install raesl[all]` for any Python version >=3.11.
For managed projects you can use:

- uv: `uv add raesl[all]`
- Poetry: `poetry add raesl -E all`

For RaESL's different subcommands and functionality, the wheel provides extras which you could
provide instead of the `all` used above:

- `doc`: documentation generation using pandoc, Markdown and optionally LaTeX.
- `jupyter`: a Jupyter ESL kernel.
- `pygments`: an ESL syntax highlighter for pygments.
- `rich`: Rich doc output in the form of Plotly images.
- `server`: A language server to parse documents.

The default `raesl compile` command is always available.

Please refer to the [usage documentation](https://raesl.ratio-case.nl) for more info on how to use
RaESL.

## Development installation

This project is packaged using [uv](https://docs.astral.sh/uv/) as the environment manager and build
frontend. Packaging information as well as dependencies are stored in
[pyproject.toml](./pyproject.toml).

For ease of use, this project uses the [just](https://github.com/casey/just) command runner to
simplify common tasks. Installing the project and its development dependencies can be done by
running `just install` in the cloned repository directory or manually by running `uv sync --all-extras`.

Please consult the [justfile](./justfile) for the underlying commands or run `just` to display a
list of all available commands.

### Tests

Tests can be run using `just test` and subsequent arguments will be passed to pytest.

### Linting

Linting the project can be done using `just lint`, automatic fixes can be applied using `just fix`.
Linting config is included in [pyproject.toml](./pyproject.toml) for Ruff.

### Documentation

Documentation can be built using `just docs` or served continuously using `just serve-docs` with
the help of [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Contributions and license

To get contributing, feel free to fork, pick up an issue or file your own and get going for your
first merge! We'll be more than happy to help.

For contribution instructions, head over to [CONTRIBUTING.md](./CONTRIBUTING.md).

RaPlan is licensed following a dual licensing model. In short, we want to provide anyone that
wishes to use our published software under the GNU GPLv3 to do so freely and without any further
limitation. The GNU GPLv3 is a strong copyleft license that promotes the distribution of free,
open-source software. In that spirit, it requires dependent pieces of software to follow the same
route. This might be too restrictive for some. To accommodate users with specific requirements
regarding licenses, we offer a proprietary license. The terms can be discussed by reaching out to
Ratio.
