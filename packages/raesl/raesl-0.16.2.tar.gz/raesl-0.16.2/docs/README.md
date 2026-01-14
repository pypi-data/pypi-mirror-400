# Ratio ESL

Ratio support for the Elephant Specification Language (ESL) in Python.

1. [How-to guides](./how-to-guides/README.md) for a more use-case centric approach, the package's,
1. [Reference](./reference/README.md) including source code,
1. The [Changelog](./CHANGELOG.md) outlining all changes following the
   [https://keepachangelog.com](https://keepachangelog.com) conventions.

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

## Where to next?

The [How-to guides](./how-to-guides/README.md) are a great place to start and get your bearings!

## License and contributions

For contribution instructions, head over to the [open-source GitLab
repository](https://gitlab.com/ratio-case-os/python/raesl)!

All code snippets in of this documentation are free to use.

If you find any documentation worthwhile citing, please do so with a proper reference to our
documentation!

RaESL is licensed following a dual licensing model. In short, we want to provide anyone that
wishes to use our published software under the GNU GPLv3 to do so freely and without any further
limitation. The GNU GPLv3 is a strong copyleft license that promotes the distribution of free,
open-source software. In that spirit, it requires dependent pieces of software to follow the same
route. This might be too restrictive for some. To accommodate users with specific requirements
regarding licenses, we offer a proprietary license. The terms can be discussed by reaching out to
Ratio.
