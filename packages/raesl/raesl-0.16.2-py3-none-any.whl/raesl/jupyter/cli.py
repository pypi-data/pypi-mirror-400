"""ESL Jupyter kernel Command Line Interface."""

import os
import sys
from typing import Optional

import click

kernel_json = {
    "argv": [
        sys.executable,
        "-m",
        "raesl.jupyter.cli",
        "run",
        "-f",
        "{connection_file}",
    ],
    "display_name": "ESL",
    "language": "esl",
    "mimetype": "text/x-esl",
    "file_extension": ".esl",
    "pygments_lexer": "esl",
    "codemirror_mode": "esl",
}


def install_my_kernel_spec(user=True, prefix=None):
    import json

    from IPython.utils.tempdir import TemporaryDirectory
    from jupyter_client.kernelspec import KernelSpecManager

    with TemporaryDirectory() as td:
        print("Installing Jupyter kernel spec...")
        os.chmod(td, 0o755)  # Starts off as 700, not user readable

        with open(os.path.join(td, "kernel.json"), "w") as f:
            json.dump(kernel_json, f, sort_keys=True)

        # assets = pathlib.Path(__file__).parent / "assets"
        # for asset in assets.iterdir():
        #     shutil.copy2(assets / asset, td)

        KernelSpecManager().install_kernel_spec(td, "esl", user=user, prefix=prefix)
        KernelSpecManager().get_kernel_spec("esl")
        print("Done.")


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


@click.group("jupyter")
def jupyter():
    """Manage the Jupyter ESL kernel."""
    pass


@jupyter.command("install")
@click.option(
    "--user",
    is_flag=True,
    default=False,
    help="Install to the per-user kernels registry. Default if not root.",
)
@click.option(
    "--sys-prefix",
    is_flag=True,
    default=False,
    help="Install to sys.prefix (e.g. a virtualenv or conda env)",
)
@click.option(
    "--prefix",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Install to the given prefix. "
    "Kernelspec will be installed to {prefix}/share/jupyter/kernels/",
)
def install(user: bool, sys_prefix: bool, prefix: Optional[str] = None) -> None:
    """Install the ESL Jupyter kernel spec."""
    prefix = sys.prefix if sys_prefix else prefix

    if not prefix and not _is_root():
        user = True

    install_my_kernel_spec(user=user, prefix=prefix)


@jupyter.command("run")
@click.option(
    "-f",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Kernel connection file.",
)
def run(f: str):
    """Run the ESL Jupyter kernel."""
    from ipykernel.kernelapp import IPKernelApp

    from raesl.jupyter.kernel import EslKernel

    IPKernelApp.launch_instance(kernel_class=EslKernel)


if __name__ == "__main__":
    jupyter()
