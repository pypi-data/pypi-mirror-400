"""ESL Language Server Command Line interface."""

from typing import Optional

import click

from raesl import logger


@click.command("serve")
@click.option(
    "--port",
    "-p",
    default=None,
    type=click.INT,
    help="An optional TCP port to run on, useful for debugging.",
)
def serve(port: Optional[int] = None):
    """Start the ESL Language Server."""
    try:
        from raesl.server.server import ls
    except ImportError:
        logger.error("Missing dependencies. Make sure the 'server' extras are installed.")
        return

    if port is None:
        logger.info("Starting ESL Language Server on STDIO...")
        ls.start_io()
    else:
        logger.info(f"Starting ESL Language Server on port {port}...")
        ls.start_tcp("localhost", port)


if __name__ == "__main__":
    serve()
