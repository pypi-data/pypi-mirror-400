#
#   Imandra Inc.
#
#   cmd_models.py
#

import time
from logging import getLogger
from typing import Annotated

import typer
from rich import print as printr
from rich.live import Live

from ..strategy.model import Model, ModelList
from .utils import CLServerClient

log = getLogger(__name__)
app = typer.Typer()


# fmt: off
@app.command('list')
def run_model_list(
    live: Annotated[bool, typer.Option(help='If used, then will run the command in a loop.')] = False,
    addr: Annotated[str, typer.Option(help='CL Server address')] = 'http://127.0.0.1:8000',
):
    # fmt: on
    """
    List info about all models in the current strategy
    """

    cl_client = CLServerClient(addr)
    resp = cl_client.get('metamodel/list')
    model_list = ModelList.model_validate_json(resp.json())

    if live:
        with Live(model_list, refresh_per_second=4) as l:
            while True:
                resp = cl_client.get('metamodel/list')
                l.update(ModelList.model_validate_json(resp.json()))
                time.sleep(1)

    else:
        printr(model_list)


# fmt: off
@app.command('view')
def run_model_view(
    index: Annotated[int, typer.Argument(help='Index of the model to view')],
    live: Annotated[bool, typer.Option(help='If used, then will run the command in a loop.')] = False,
    addr: Annotated[str, typer.Option(help='CL Server address')] = 'http://127.0.0.1:8000',
):
    # fmt: on
    """
    View model specified by index
    """

    cl_client = CLServerClient(addr)
    resp = cl_client.get(f'model/byindex/{index}')
    model = Model.model_validate_json(resp.json())

    if live:
        with Live(model, refresh_per_second=1) as l:
            resp = cl_client.get(f'model/byindex/{index}')
            l.update(Model.model_validate_json(resp.json()))
            time.sleep(1)
    else:
        printr(model)


# fmt: off
@app.command('freeze')
def run_model_cmd_freeze(
    index: Annotated[int, typer.Argument(help='Freezes the IML code b/c of user changes.')],
    addr: Annotated[str, typer.Option(help='CL Server address')] = 'http://127.0.0.1:8000',
):
    # fmt: on
    cl_client = CLServerClient(addr)
    resp = cl_client.post(f'model/cmd/freeze/{index}')
    printr(resp.json())


@app.command('unfreeze')
def run_model_cmd_unfreeze(
    index: Annotated[
        int,
        typer.Argument(
            help='Unfreezes the model if frozen. User-specified IML code will be overriden if needed.'
        ),
    ],
    addr: Annotated[str, typer.Option(help='CL Server address')] = 'http://127.0.0.1:8000',
):
    cl_client = CLServerClient(addr)
    resp = cl_client.post(f'model/cmd/unfreeze/{index}')
    printr(resp.json())
