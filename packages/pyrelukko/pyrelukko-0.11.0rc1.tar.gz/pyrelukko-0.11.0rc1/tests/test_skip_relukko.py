import logging
from datetime import datetime

from pyrelukko import RelukkoClient
from pyrelukko.decorators import SKIP_RELUKKO

logger = logging.getLogger(__name__)
exp_expires_at = datetime.fromisoformat(SKIP_RELUKKO["expires_at"])


def test_skip_life_cycle(mock_env_relukko_skip):
    assert mock_env_relukko_skip is None
    relukko = RelukkoClient(base_url="http://relukko", api_key="abc")

    skipped = relukko.acquire_relukko(
        "SKIP_THIS", creator="skipper", max_run_time=5)
    assert skipped == SKIP_RELUKKO

    lock = relukko.get_lock(
        "00000000-0000-0000-0000-000000000000")
    assert lock == SKIP_RELUKKO

    locks = relukko.get_locks()
    assert locks == [ SKIP_RELUKKO ]

    lock = relukko.update_relukko(
        "00000000-0000-0000-0000-000000000000", creator="Skipper")
    assert lock == SKIP_RELUKKO

    lock = relukko.delete_relukko(
        "00000000-0000-0000-0000-000000000000")
    assert lock == SKIP_RELUKKO

    lock = relukko.keep_relukko_alive(
        "00000000-0000-0000-0000-000000000000")
    assert lock == SKIP_RELUKKO

    lock = relukko.keep_relukko_alive_put(
        "00000000-0000-0000-0000-000000000000", 5)
    assert lock == SKIP_RELUKKO

    lock = relukko.add_to_expires_at_time(
        "00000000-0000-0000-0000-000000000000")
    assert lock == SKIP_RELUKKO

    lock = relukko.add_to_expires_at_time_put(
        "00000000-0000-0000-0000-000000000000", 5)
    assert lock == SKIP_RELUKKO
