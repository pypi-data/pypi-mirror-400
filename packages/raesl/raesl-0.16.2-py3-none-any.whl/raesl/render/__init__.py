"""RaESL output rendering module

Renders ESL specifications to output formats such as HTML, Typst, and Typst compiled to PDF.
"""

from typing import Literal

Format = Literal["typst", "pdf", "html", "markdown"]
