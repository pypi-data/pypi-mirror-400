"""Jupyter server integration for doweb."""

import asyncio
import os
import socket

# import requests
import uvicorn

from doweb.default import app

# Global variables for server state
jupyter_server = None
host = None
port = None


# TODO: Don't start a server if there is one running and the version
# is similar or higher


def is_port_in_use(
    port: int,
    host: str = "localhost",
) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def _run() -> None:
    global jupyter_server, host, port  # noqa: PLW0603

    _port = os.getenv("DOWEB_PORT")
    port = 8081 if _port is None else int(_port)
    host = os.getenv("DOWEB_HOST")
    if host is None:
        host = "localhost"
    # if is_port_in_use(host=host, port=port):
    #     req = requests.request("get", f"http://{host}:{port}/status")

    config = uvicorn.Config(app)
    config.port = port
    config.host = host

    jupyter_server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    server_task = loop.create_task(jupyter_server.serve())
    # Store task reference to avoid it being garbage collected
    server_task.add_done_callback(lambda _: None)


def _server_is_running() -> bool:
    global jupyter_server  # noqa: PLW0602
    return False if jupyter_server is None else jupyter_server.started


def start() -> None:
    """Start a jupyter_server if it's nor already started."""
    if not _server_is_running():
        _run()
