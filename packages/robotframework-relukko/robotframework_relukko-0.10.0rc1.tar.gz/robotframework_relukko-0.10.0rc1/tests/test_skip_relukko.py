import logging
from datetime import datetime

from Relukko import Relukko
from pyrelukko.decorators import SKIP_RELUKKO

logger = logging.getLogger(__name__)
exp_expires_at = SKIP_RELUKKO.expires_at
exp_created_at = SKIP_RELUKKO.created_at


def test_skip_life_cycle(mock_env_relukko_skip):
    relukko = Relukko(base_url="http://relukko", api_key="abcd")
    skipped = relukko.acquire_relukko("SKIP_THIS", max_wait_time="5s")
    assert skipped == SKIP_RELUKKO

    lock = relukko.keep_relukko_alive_for_the_next_5_min()
    assert lock == SKIP_RELUKKO

    lock = relukko.keep_relukko_alive_for_x_seconds(5)
    assert lock == SKIP_RELUKKO

    lock = relukko.keep_relukko_alive_for_the_next("5s")
    assert lock == SKIP_RELUKKO

    lock = relukko.add_to_current_relukko_expire_at_time_5_min()
    assert lock == SKIP_RELUKKO

    lock = relukko.add_to_current_relukko_expire_time_x_seconds(5)
    assert lock == SKIP_RELUKKO

    lock = relukko.add_to_current_relukko_expire_at_time("5s")
    assert lock == SKIP_RELUKKO

    lock = relukko.update_relukko(creator="Skipper")
    assert lock == SKIP_RELUKKO

    lock = relukko.get_current_relukko(refresh=False)
    assert lock == SKIP_RELUKKO

    lock = relukko.get_current_relukko(refresh=True)
    assert lock == SKIP_RELUKKO

    expires_at = relukko.get_relukko_expires_at_time(refresh=False)
    assert expires_at == exp_expires_at

    expires_at = relukko.get_relukko_expires_at_time(refresh=True)
    assert expires_at == exp_expires_at

    expires_at = relukko.get_relukko_created_at_time(refresh=False)
    assert expires_at == exp_expires_at

    expires_at = relukko.get_relukko_created_at_time(refresh=True)
    assert expires_at == exp_expires_at

    lock = relukko.delete_relukko()
    assert lock == SKIP_RELUKKO
