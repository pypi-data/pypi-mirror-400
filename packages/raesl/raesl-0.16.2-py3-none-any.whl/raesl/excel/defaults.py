"""Default options for ESL to Excel workbook conversion."""
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.protection import SheetProtection

WRAP = Alignment(wrap_text=True)
MONO = Font(name="Consolas")
SHEETPROTECTION = SheetProtection(
    sheet=True,
    formatColumns=False,
    formatRows=False,
    formatCells=False,
    sort=False,
    autoFilter=False,
)

OPTIONS = {
    # General
    "instance path": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=True)),
        width=30,
    ),
    "component path": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=True)),
        width=40,
    ),
    "instance name": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=True)),
        width=20,
    ),
    "parent component": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=False)),
        width=30,
    ),
    "component definition": dict(
        styles=dict(alignment=Alignment(horizontal="left", vertical="top", wrap_text=True)),
        width=30,
    ),
    "kind": dict(styles=dict(alignment=Alignment(horizontal="center", vertical="top")), width=20),
    "form": dict(styles=dict(alignment=Alignment(horizontal="center", vertical="top")), width=15),
    # Helper words
    "auxiliary": dict(
        styles=dict(alignment=Alignment(horizontal="center", vertical="top", wrap_text=True)),
        width=12,
    ),
    "comparison": dict(
        styles=dict(alignment=Alignment(horizontal="center", vertical="top", wrap_text=True)),
        width=20,
    ),
    "comments": dict(
        styles=dict(alignment=Alignment(horizontal="left", vertical="top", wrap_text=True)),
        width=60,
    ),
    # Overview
    "specification text": dict(
        styles=dict(alignment=Alignment(horizontal="left", vertical="top", wrap_text=True)),
        width=60,
    ),
    # Need
    "subject": dict(
        styles=dict(alignment=Alignment(horizontal="left", vertical="top", wrap_text=True)),
        width=30,
    ),
    # Goal/transform specific
    "source component": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=True)),
        width=40,
    ),
    "target component": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=True)),
        width=40,
    ),
    "verb": dict(
        styles=dict(alignment=Alignment(horizontal="center", vertical="top", wrap_text=True)),
        width=15,
    ),
    "preposition": dict(
        styles=dict(alignment=Alignment(horizontal="center", vertical="top", wrap_text=True)),
        width=10,
    ),
    "variables": dict(
        styles=dict(alignment=Alignment(horizontal="left", vertical="top", wrap_text=True)),
        width=30,
    ),
    # Design requirements
    "bound": dict(
        styles=dict(alignment=Alignment(horizontal="right", vertical="top", wrap_text=True)),
        width=20,
    ),
    "subclauses": dict(
        styles=dict(alignment=Alignment(horizontal="left", vertical="top")), width=60
    ),
}

OUTPUT = "./esl.xlsx"
SCOPES = dict(world=None)
