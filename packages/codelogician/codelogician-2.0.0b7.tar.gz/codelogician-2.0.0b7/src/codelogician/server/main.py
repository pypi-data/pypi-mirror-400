#
#   CodeLogician Server
#
#   main.py
#

import logging
import os
import sys
from pathlib import Path
from typing import Annotated

import dotenv
import typer
import uvicorn

from ..util import maybe_or_call
from .cl_server import CLServer
from .config import ServerConfig
from .endpoints import register_endpoints
from .state import ServerState
from .utils import do_intro

dotenv.load_dotenv('.env')
if 'IMANDRA_UNI_KEY' not in os.environ:
    print("CodeLogician requires 'IMANDRA_UNI_KEY' to be set!")
    sys.exit(0)

log = logging.getLogger(__name__)

# ch = logging.StreamHandler(sys.stdout)
# ch.setLevel(logging.INFO) # Only show INFO and above
# ch.setFormatter(logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"))
# log.addHandler(ch)


def log_and_raise(msg):
    log.error(msg)
    raise Exception(msg)


def run_server(
    dir: str,
    state: str | None = None,
    clean: bool = False,
    config: Annotated[
        str, typer.Option('--config', help='Server configuration YAML file')
    ] = 'config/server_config.yaml',
    addr: Annotated[
        str, typer.Option(help='Server address, host/port')
    ] = 'http://127.0.0.1:8000',
):
    """
    Run the server
    - dir - target directory
    - state_path - state file to use
    - clean - should we discard any existing changes
    - config - server configuration
    - addr - address we should use instead of the one provided in the config
    """

    do_intro()

    try:
        servConfig = ServerConfig.fromYAML(config)
    except Exception as e:
        log.warning(f'Failed to load in server config: {str(e)}. Using defaults.')
        servConfig = ServerConfig()

    def load_state(state_path):
        # We need to use the existing state
        abs_path = str(Path(state_path).resolve())

        if not os.path.exists(abs_path):
            log.warning(
                f"Specified path for server config doesn't exist: [{abs_path}]. Using defaults."
            )
            return ServerState(abs_path=abs_path)
        else:
            try:
                return ServerState.fromFile(abs_path)
            except Exception as e:
                log_and_raise(
                    f'Failed to read server state from `{abs_path}` ({str(e)})'
                )

    def new_state():
        server_state_abs_path = os.path.join(os.getcwd(), '.cl_server')

        state = ServerState(
            abs_path=server_state_abs_path, strategy_paths=[], config=servConfig
        )

        if dir:
            # We need to add a strategy directory to the state
            abs_path = str(Path(dir).resolve())  # TODO: is os.path.abspath better?
            if not (os.path.exists(abs_path) and os.path.isdir(abs_path)):
                log_and_raise(
                    f'Specified path must exist and be a directory: {abs_path}'
                )

            state.strategy_paths.append(abs_path)
            if clean:
                log.info(
                    'Starting clean, so will attempt to remove any existing caches!'
                )
                cache_path = os.path.join(abs_path, '.cl_cache')
                if os.path.exists(cache_path):
                    try:
                        os.remove(cache_path)
                        log.info(f'Removed: {cache_path}')
                    except Exception:
                        log_and_raise(f'Failed to remove {cache_path}!')
        return state

    def run_state(state):
        server = CLServer(state)
        register_endpoints(server)

        uvicorn.run(
            server,
            host=state.config.host,
            port=state.config.port,
            # reload=state.config.debug,
            log_level='info',
        )

    run_state(maybe_or_call(new_state, load_state, state))
