# Document generation usage

RaESL enables you to convert an ESL specification into a display document such as PDF, Markdown or
even Word. It uses Pandoc under the hood, or in some cases LaTeX, too. Since these documents are
generated from your spec, they are guaranteed to be up-to-date and consistent with your content.

From a Python script, you can call the conversion using the following snippet:

```python
import raesl.doc

pdf_path = generated / "pump.pdf"
raesl.doc.convert(pump_esl, output=pdf_path, title="Pump example", force=True)  # e.g. "pump.esl"
```

Which results in [this PDF](../generated/pump.pdf). You can supply any number of (positional)
ESL file and directory paths just like you can with the ESL compiler.

## Customizing the generated document

There are several ways to further customize the display document. Lets review a fully fledged
example:

```python
import raesl.doc

html_path = generated / "pump.html"
raesl.doc.convert(
    pump_esl,  # e.g. "pump.esl" ...
    output=html_path,  # e.g. "pump.html"
    language="en",  # "en" or "nl"
    title="Pump example",
    prologue=pump_prologue,  # e.g. "prologue.md"
    epilogue=pump_epilogue,  # e.g. "epilogue.md"
    rich="md",  # "md", "tex", or "off"
    force=True,
    dry=False,
)
```

which results in [this HTML file](../generated/pump.html).

### Document file formats

Internally your specification is converted to Markdown. A lightweight typesetting language often
rendered to HTML pages. Changing the output path to something with the `.pdf` extension changes the
format to PDF. Similarly, the `.md` extension changes the format to Markdown or `.html` to HTML.

We recommend generating PDF files for the pretties results, as well as using the `rich="tex"` option
for pretty LaTeX figures.

### Including a prologue or epilogue

You can provide your own `prologue` or `epilogue` as files in a Pandoc Markdown format which will be
rendered before and after the main content, respectively. The prologue is put after the frontmatter
and the epilogue is placed before the automatically generated appendices.

### Document language

You can change the generated document's language by changing the `language` argument. Currently,
Dutch (`nl`) and English (`en`) are supported.

!!! note

    Please keep in mind that all your variable and component names will not be translated during this
    conversion.

!!! note

    You can make the output a little less verbatim by adding articles (Dutch: lidwoorden) before
    component names separated by an underscore `_`. All underscores are replaced by spaces in the
    generated output text.

## Command-Line Interface

RaESL document generation is also available under the Command-Line Interface (CLI) as `raesl doc`.
Type `raesl doc --help` in your terminal to see the available arguments.
