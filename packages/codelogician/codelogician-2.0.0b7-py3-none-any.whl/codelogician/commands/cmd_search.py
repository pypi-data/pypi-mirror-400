#
#   Imandra Inc.
#
#   cmd_search.py
#
from logging import getLogger

from rich import print as rprint

from .utils import CLServerClient

log = getLogger(__name__)


def run_search(query: str, addr: str):
    """
    Run search command
    """
    cl_client = CLServerClient(addr)
    response = cl_client.get('search', {'query': query})

    if len(response.json()) == 0:
        print('No results found!')
    else:
        for res in response.json():
            rprint(res)
