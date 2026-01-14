# Excel generation

```python
drive_mechanism_excel = "./pump-drive-mechanism.xlsx"
```

RaESL enables you to convert an ESL specification into an Excel workbook.From a Python script, you
can call the conversion using the following snippet:

```python
import raesl.excel

excel_path = generated / "pump.xlsx"
wb = raesl.excel.convert(pump_esl, output=excel_path)  # e.g. "pump.esl"
```

Which results in [this Excel file](../generated/pump.xlsx). You can supply any number of
(positional) ESL file and directory paths just like you can with the ESL compiler.

## Customizing the generated workbook

There are several ways to further customize the Excel workbook. Lets review a fully fledged example:

```python
import raesl.excel

drive_mechanism_excel = generated / "pump-drive-mechanism.xlsx"
wb = raesl.excel.convert(
    pump_esl,  # e.g. "pump.esl"
    output=drive_mechanism_excel,
    scopes={"world.drive-mechanism": 1},
)
```

which results in [this Excel file](../generated/pump-drive-mechanism.xlsx).

### Providing scopes

Note that in this case, we _scoped_ the output document to the `drive-mechanism` instead of the
complete component tree. This means that in this case, only the `drive-mechanism` and components
with a relative depth of 1 with respect to the drive-mechanism are included in the generated output
(e.g. its direct children).

You can supply any number of (overlapping) scopes and receive an Excel workbook for those scopes
specifically. Supplying a scope with `None` as the depth value results in the inclusion of the
complete sub-tree starting at that component instance.

## Command-Line Interface

RaESL Excel generation is also available under the Command-Line Interface (CLI) as `raesl excel`.
Type `raesl excel --help` in your terminal to see the available arguments and usage. Most notable
change with respect to usage from a Python script is that you have to supply a value of `-1` instead
of `None` when specifying output scopes.
