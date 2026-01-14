"""ESL Jupyter Kernel implementation."""

import json
import pathlib
import tempfile
import urllib
from typing import Optional

from ipykernel import get_connection_file
from ipykernel.kernelbase import Kernel
from jupyter_server import serverapp

from raesl import __version__

# Compile module is excluded during docs generation.
try:
    from raesl.compile.cli import run
except ImportError:
    pass


class EslKernel(Kernel):
    implementation = "raesl.compile"
    implementation_version = __version__
    language = "esl"
    language_version = "2.0"
    language_info = {
        "name": "Elephant Specification Language",
        "mimetype": "text/x-esl",
        "file_extension": ".esl",
    }
    banner = "ESL Kernel - Support for the Elephant Specification Language."

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        stdout = []
        stderr = []

        with tempfile.TemporaryDirectory() as tmpdir:
            esl = pathlib.Path(tmpdir) / "notebook.esl"
            esl.write_text(code, encoding="utf-8")
            try:
                run(esl)
                stdout.append("Compiler ran succesfully.")
                try:
                    # notebook = self.get_notebook_path()
                    # if not notebook:
                    #     notebook = pathlib.Path("./notebook.esl")
                    esl_doc = pathlib.Path("./notebook.esl")
                    esl_doc.write_text(code)
                    stdout.append("ESL file saved as {}.".format(esl_doc.name))
                except Exception as exc:
                    stderr.append(str(exc))
            except Exception as exc:
                stderr.append(str(exc))

        if not silent:
            stdout_content = {"name": "stdout", "text": "\n".join(stdout)}
            self.send_response(self.iopub_socket, "stream", stdout_content)

        if stderr:
            stderr_content = {"name": "stderr", "text": "\n".join(stderr)}
            self.send_response(self.iopub_socket, "stream", stderr_content)

        return {
            "status": "ok",
            # The base class increments the execution count
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

    def get_notebook_path(self) -> Optional[pathlib.Path]:
        connection_file = get_connection_file()
        kernel_id = connection_file.split("-", 1)[1].split(".")[0]

        for srv in serverapp.list_running_servers():
            try:
                if srv["token"] == "" and not srv["password"]:
                    req = urllib.request.urlopen(srv["url"] + "api/sessions")
                else:
                    req = urllib.request.urlopen(srv["url"] + "api/sessions?token=" + srv["token"])
                sessions = json.load(req)
                for sess in sessions:
                    if sess["kernel"]["id"] == kernel_id:
                        return pathlib.Path(srv["notebook_dir"], sess["notebook"]["path"])
            except Exception:
                return None
