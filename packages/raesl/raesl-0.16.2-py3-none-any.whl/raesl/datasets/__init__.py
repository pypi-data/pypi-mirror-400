"""Datasets module. Contains various ESL datasets (see :obj:`enum()`, :obj:`get()`,
and :obj:`info`).
"""

import importlib
import shutil
from pathlib import Path
from typing import List

HERE = Path(__file__).parent


def enum() -> List[str]:
    """Enumerate all available datasets."""
    return sorted(
        [
            d.name
            for d in HERE.iterdir()
            if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("_")
        ]
    )


def check(name: str):
    """Check whether a dataset exists."""
    available = enum()
    if name not in available:
        raise ValueError(
            "Dataset {} cannot be found. Please pick one of {}.".format(name, available)
        )


def info(name: str) -> str:
    """Get information about a dataset."""
    check(name)
    mod = importlib.import_module(f"raesl.datasets.{name}")
    doc = mod.__doc__
    return str(doc)


def copy(name: str, output_path: str, as_file: bool = False) -> None:
    """Copy a dataset into a directory or file."""
    check(name)
    p = Path(output_path)
    p.parent.mkdir(exist_ok=True, parents=True)

    loc = HERE / name
    files = [f for f in (HERE / name).glob("**/*.esl")]

    if as_file:
        p.write_text("\n\n".join(f.read_text() for f in files))
    else:
        if p.exists() and any(p.iterdir()):
            raise ValueError(f"Directory {p} already exists and is not empty.")

        for f in files:
            dest = p / f.relative_to(loc)
            dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(f, dest)


def get(name: str):
    """Get a dataset.

    Arguments:
        name: Name of the dataset to get (see `ragraph.datasets.enum()`).
    """
    from ragraph.io.esl import from_esl

    check(name)

    graph = from_esl(HERE / name)
    graph.kind = name

    return graph
