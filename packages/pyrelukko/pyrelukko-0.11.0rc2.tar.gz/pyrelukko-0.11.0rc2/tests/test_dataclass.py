
import logging

from requests_mock import ANY

from pyrelukko import RelukkoClient, RelukkoDTO
from pyrelukko.decorators import SKIP_RELUKKO

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


RELUKKO_DATA_FIELDS = [
    "id",
    "lock_name",
    "creator",
    "ip",
    "expires_at",
    "created_at",
    "updated_at",
]


def test_lock_dataclass(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=200,
        reason="OK",
        json=SKIP_RELUKKO.to_dict()
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key", disable_websocket=True,
    )

    lock = relukko.get_lock("GetLock")

    assert isinstance(lock, RelukkoDTO)
    assert isinstance(lock.to_dict(), dict)


def test_lock_dict_like(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=200,
        reason="OK",
        json=SKIP_RELUKKO.to_dict()
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key", disable_websocket=True,
    )

    lock = relukko.get_lock("GetLock")

    for field in RELUKKO_DATA_FIELDS:
        assert SKIP_RELUKKO[field] == lock[field]


def test_lock_get_field(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=200,
        reason="OK",
        json=SKIP_RELUKKO.to_dict()
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key", disable_websocket=True,
    )

    lock = relukko.get_lock("GetLock")

    for field in RELUKKO_DATA_FIELDS:
        assert SKIP_RELUKKO.get(field) == lock.get(field)
