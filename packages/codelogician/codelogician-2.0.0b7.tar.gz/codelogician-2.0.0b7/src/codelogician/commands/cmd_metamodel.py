#
#   Imandra Inc.
#
#   cmd_models.py
#

from logging import getLogger
from typing import Annotated

import typer
from rich import print as rprint

from .utils import CLServerClient

log = getLogger(__name__)

app = typer.Typer()


@app.command('cmd')
def run_metamodel_cmd(
    cmd: Annotated[str, typer.Option(help='Command to execute')] = '',
    addr: Annotated[str, typer.Option(help='Server address')] = 'http://127.0.0.1:8000',
):
    """
    Run search command
    """

    cl_client = CLServerClient(addr)

    response = cl_client.get('search', {'query': cmd})

    if len(response.json()) == 0:
        print('No results found!')
    else:
        for res in response.json():
            rprint(res)
