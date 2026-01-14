#
#   Imandra Inc.
#
#   cmd_sketches.py
#

from logging import getLogger
from typing import Annotated

import typer
from rich import print as rprint

from .utils import CLServerClient

log = getLogger(__name__)
app = typer.Typer()


@app.command('list')
def run_sketches_list(
    addr: Annotated[
        str, typer.Option(help='CL Server address')
    ] = 'http://127.0.0.1:8000',
):
    """
    Run search command
    """

    cl_client = CLServerClient(addr)
    response = cl_client.get('sketches/list')

    if len(response.json()) == 0:
        print('No results found!')
    else:
        for res in response.json():
            rprint(res)


# fmt: off
@app.command('create')
def run_sketches_create(
    rel_path: Annotated[str, typer.Argument(help='Relative path of the model to use as the anchor')],
    addr: Annotated[str, typer.Option(help='CL Server address')] = 'http://127.0.0.1:8000',
):
    # fmt: on
    """
    Create a new sketch
    """
    typer.echo("I'm in run_sketches_create")


# fmt: off
@app.command('delete')
def run_sketches_delete(
    sketch_id: Annotated[str, typer.Argument(help='Sketch ID of the sketch to be deleted')],
    addr: Annotated[str, typer.Option(help='CL Server address')] = 'http://127.0.0.1:8000',
):
    # fmt: on
    """
    Delete a sketch
    """
    typer.echo("I'm in run_sketches_delete")
