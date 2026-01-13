import os
import socket
import ssl
import threading
from pathlib import Path
from typing import List

import pytest
from testcontainers.core.network import Network

from pyrelukko import RelukkoClient
from pyrelukko.testcontainers import RelukkoContainer, RelukkoDbContainer

SCRIPT_DIR = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def relukko_backend():
    if os.environ.get("CI_HAS_RELUKKO"):
        # Gitlab does not allow DinD networks, so Relukko runs as a service
        # in the background of the job.
        relukko = RelukkoClient(
            base_url=os.environ['CI_RELUKKO_BASE_URL'],
            api_key=os.environ['CI_RELUKKO_API_KEY']
        )
        yield relukko, None
    else:
        with Network() as rl_net:
            with RelukkoDbContainer(net=rl_net,
                image="postgres:17", hostname="relukkodb") as _db:
                db_url = "postgresql://relukko:relukko@relukkodb/relukko"
                with RelukkoContainer(rl_net, db_url=db_url) as backend:
                    relukko = RelukkoClient(
                        base_url=backend.get_api_url(), api_key="somekey")
                    yield relukko, backend

@pytest.fixture(scope="function")
def tls_listener():

    certfile = SCRIPT_DIR / "cert" / "relukko.crt"
    keyfile = SCRIPT_DIR / "cert" / "relukko.key"

    def run_server(port_info: List, keep_running: threading.Event):
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen(5)  # Listen for incoming connections

            _, assigned_port = sock.getsockname()
            port_info.append(assigned_port)

            # Wrap the socket with TLS
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            with context.wrap_socket(sock, server_side=True) as ssock:

                ssock.settimeout(1)

                while keep_running.is_set():
                    try:
                        client_socket, _ = ssock.accept()
                        client_socket.sendall(b"Hello, TLS Client!")
                        client_socket.close()
                    except Exception as _:
                        continue

    port_info = []
    keep_running = threading.Event()
    keep_running.set()
    thread = threading.Thread(target=run_server, args=(port_info, keep_running))
    thread.start()

    while not port_info:
        pass

    yield thread, port_info[0]

    keep_running.clear()
    thread.join()

@pytest.fixture(scope="function")
def mock_env_relukko_skip(monkeypatch):
    monkeypatch.setenv("RELUKKO_TRUST_ME_IT_IS_LOCKED", "yes")
    yield
    monkeypatch.delenv("RELUKKO_TRUST_ME_IT_IS_LOCKED", raising=True)
