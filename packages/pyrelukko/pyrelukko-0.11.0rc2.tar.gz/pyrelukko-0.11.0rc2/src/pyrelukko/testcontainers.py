# pylint: skip-file
"""
Testcontainers to be used in PyTests, for an real life fixture see
``tests/conftest.py`` (relukko_backend):

Example::

    @pytest.fixture(scope="session")
    def relukko_backend():
        with Network() as rl_net:
            with RelukkoDbContainer(net=rl_net,
                image="postgres:16", hostname="relukkodb") as _db:
                db_url = "postgresql://relukko:relukko@relukkodb/relukko"
                with RelukkoContainer(rl_net, db_url=db_url) as backend:
                    relukko = RelukkoClient(
                        base_url=backend.get_api_url(), api_key="somekey")
                    yield relukko, backend

"""
import os
import socket
import time

from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import WaitStrategy
from testcontainers.generic import ServerContainer
from testcontainers.postgres import PostgresContainer


class RelukkoContainer(ServerContainer):
    def __init__(self, net: Network,
                 db_url: str,
                 image="registry.gitlab.com/relukko/relukko:latest"):
        """Starts a "Relukko" container for testing.

        Ensures the "Relukko" container is up, running and ready to use.

        :param net: The ``testcontainers`` Network in which also the required
                    PostgreSQL database is reachable.
        :type net: Network
        :param db_url: The URL where the PostgreSQL is reachable, defaults to None.
        :type db_url: str,
        :param image: The Relukko container image to start, defaults to
                      "registry.gitlab.com/relukko/relukko:latest".
                      The value in the env var ``CI_RELUKKO_CONTAINER_IMAGE``
                      takes precedence over the value given as argument.
        :type image: str, optional
        """
        container_image = os.environ.get('CI_RELUKKO_CONTAINER_IMAGE') or image
        self.db_url = db_url
        self.net = net
        super(RelukkoContainer, self).__init__(image=container_image, port=3000)

    def _configure(self):
        self.with_env("DATABASE_URL", self.db_url)
        self.with_env("RELUKKO_API_KEY", "somekey")
        self.with_env("RELUKKO_USER", "relukko")
        self.with_env("RELUKKO_PASSWORD", "relukko")
        self.with_env("RELUKKO_BIND_ADDR", "0.0.0.0")
        self.with_network(self.net)

    def get_api_url(self) -> str:
        """Return the URL where the Relukko API server can be reached.

        :return: API Url
        :rtype: str
        """
        return f"http://localhost:{self.get_exposed_port(3000)}"

    def _create_connection_url(self) -> str:
        return f"{self.get_api_url()}/healthchecker"


class PgWaitStrategy(WaitStrategy):
    def wait_until_ready(self, container):
        start_time = time.time()
        packet = bytes([
                    0x00, 0x00, 0x00, 0x52, 0x00, 0x03, 0x00, 0x00,
                    0x75, 0x73, 0x65, 0x72, 0x00, 0x72, 0x65, 0x6c,
                    0x75, 0x6b, 0x6b, 0x6f, 0x00, 0x64, 0x61, 0x74,
                    0x61, 0x62, 0x61, 0x73, 0x65, 0x00, 0x72, 0x65,
                    0x6c, 0x75, 0x6b, 0x6b, 0x6f, 0x00, 0x61, 0x70,
                    0x70, 0x6c, 0x69, 0x63, 0x61, 0x74, 0x69, 0x6f,
                    0x6e, 0x5f, 0x6e, 0x61, 0x6d, 0x65, 0x00, 0x70,
                    0x73, 0x71, 0x6c, 0x00, 0x63, 0x6c, 0x69, 0x65,
                    0x6e, 0x74, 0x5f, 0x65, 0x6e, 0x63, 0x6f, 0x64,
                    0x69, 0x6e, 0x67, 0x00, 0x55, 0x54, 0x46, 0x38,
                    0x00, 0x00
                ])

        while True:
            if time.time() - start_time > self._startup_timeout:
                raise TimeoutError(
                    f"PostgreSQL not ready within {self._startup_timeout} seconds."
                )

            port = container.get_exposed_port(container.port)
            try:
                with socket.create_connection(("localhost", port)) as sock:
                    sock.send(packet)
                    buf = sock.recv(40)
                    if len(buf) != 0 and b"SCRAM-SHA" in buf:
                        return
            except (
                ConnectionError,
                ConnectionAbortedError,
                ConnectionRefusedError,
                ConnectionResetError,
                ):
                pass
            finally:
                time.sleep(self._poll_interval)


class RelukkoDbContainer(PostgresContainer):
    def __init__(
            self, net: Network,
            image: str = "postgres:latest",
            port: int = 5432,
            username: str | None = None,
            password: str | None = None,
            dbname: str | None = None,
            driver: str | None = "psycopg2",
            **kwargs) -> None:
        """Starts a PostgreSQL container for the Relukko API server.

        Ensures the PostgreSQL container is up, running and ready to use.

        :param net: The ``testcontainers`` Network in which also the Relukko
                    API container will run.
        :type net: Network
        :param image: The PostgreSQL container image to start, defaults to
                      "postgres:latest".
        :type image: str, optional
        :param port: The listening port of the PostgreSQL db, defaults to 5432.
        :type port: int, optional
        :param username: The username of the PostgreSQL db main user, defaults
                         to None.
        :type username: str | None, optional
        :param password: The password of the PostgreSQL db main user, defaults
                         to None.
        :type password: str | None, optional
        :param dbname: The database name of the PostgreSQL db main database,
                       defaults to None.
        :type dbname: str | None, optional
        :param driver: The name of the driver to append to the connection
                       string returned by ``get_connection_url()``, defaults
                       to "psycopg2".
        :type driver: str | None, optional
        """
        self.net = net
        super().__init__(image, port, username, password, dbname, driver, **kwargs)

    def _configure(self) -> None:
        self.with_env("POSTGRES_USER", "relukko")
        self.with_env("POSTGRES_PASSWORD", "relukko")
        self.with_env("POSTGRES_DB", "relukko")
        self.with_network(self.net)

    def _connect(self) -> None:
        strategy = PgWaitStrategy()
        strategy.wait_until_ready(self)
