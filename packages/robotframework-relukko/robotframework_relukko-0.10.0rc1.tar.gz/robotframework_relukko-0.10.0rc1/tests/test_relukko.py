import logging
from datetime import datetime, timezone

import pytest
from pyrelukko import RelukkoClient
from robot.api import SkipExecution
from robot.libraries.BuiltIn import BuiltIn
from urllib3.util import parse_url

from Relukko import Relukko

logger = logging.getLogger(__name__)


def test_init():
    relukko = Relukko(base_url="http://relukko", api_key="abcd")
    assert isinstance(relukko, Relukko)
    assert isinstance(relukko.client, RelukkoClient)
    assert isinstance(relukko.builtin, BuiltIn)
    assert relukko.client.base_url == parse_url("http://relukko")
    assert relukko.client.api_key == "abcd"
    assert relukko.creator == None
    assert relukko.lock == None
    assert relukko.lock_id == None


def test_setup():
    relukko = Relukko(base_url="http://relukko", api_key="abcd")
    assert relukko.creator == None

    relukko.set_up_relukko(creator="PyTest")
    assert relukko.creator == "PyTest"


def test_acquire_relukko(relukko_backend):
    relukko, _ = relukko_backend
    lock = relukko.acquire_relukko("lock001", creator="PyTest")

    assert lock is not None
    assert relukko.lock == lock
    assert lock['lock_name'] == "lock001"
    assert lock['creator'] == "PyTest"
    assert relukko.lock_id == lock['id']
    assert relukko.lock_id == lock['id']

    with pytest.raises(SkipExecution):
        relukko.acquire_relukko(
            "lock001", creator="PyTest", max_wait_time="30s")


def test_keep_relukko_alive_for_the_next_5_min(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("keep_me", "10s", "PyTest")

    start_time = datetime.now(timezone.utc)
    keep_lock = relukko.keep_relukko_alive_for_the_next_5_min()
    assert lock['expires_at'] is not keep_lock['expires_at']

    expires_diff = keep_lock.expires_at - start_time
    assert 295 < expires_diff.seconds < 305


def test_keep_relukko_alive_for_x_seconds(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("keep_me_more", "15s", "PyTest")

    start_time = datetime.now(timezone.utc)
    keep_lock = relukko.keep_relukko_alive_for_x_seconds(42)
    assert lock['expires_at'] is not keep_lock['expires_at']

    expires_diff = keep_lock.expires_at - start_time
    assert 38 < expires_diff.seconds < 46


def test_keep_relukko_alive_for_the_next(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("keep_me_even_more", "12s", "PyTest")

    start_time = datetime.now(timezone.utc)
    keep_lock = relukko.keep_relukko_alive_for_the_next("7m43s")
    assert lock['expires_at'] is not keep_lock['expires_at']

    expires_diff = keep_lock.expires_at - start_time
    assert 458 < expires_diff.seconds < 468


def test_add_to_current_relukko_expire_at_time_5_min(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("add_me", "12s", "PyTest")

    add_lock = relukko.add_to_current_relukko_expire_at_time_5_min()
    assert lock['expires_at'] is not add_lock['expires_at']

    expires_diff = add_lock.expires_at - lock.expires_at
    assert 295 < expires_diff.seconds < 305


def test_add_to_current_relukko_expire_time_x_seconds(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("add_me_more", "12s", "PyTest")

    add_lock = relukko.add_to_current_relukko_expire_time_x_seconds(42)
    assert lock['expires_at'] is not add_lock['expires_at']

    expires_diff = add_lock.expires_at - lock.expires_at
    assert 37 < expires_diff.seconds < 47


def test_add_to_current_relukko_expire_at_time(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("add_me_even_more", "12s", "PyTest")

    add_lock = relukko.add_to_current_relukko_expire_at_time("7m42s")
    assert lock['expires_at'] is not add_lock['expires_at']

    expires_diff = add_lock.expires_at - lock.expires_at
    assert 458 < expires_diff.seconds < 468


def test_update_relukko(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("update_my_creator", "12s", "PyTest")
    assert lock['creator'] == "PyTest"

    upd_lock = relukko.update_relukko(creator="TestMe")
    assert upd_lock['creator'] == "TestMe"


def test_update_relukko_expires_at(relukko_backend):
    relukko, _ = relukko_backend

    relukko.acquire_relukko("update_my_expires_at", "12s", "PyTest")

    expires_at = datetime.fromisoformat("2099-12-31T12:34:56.789Z")
    upd_lock = relukko.update_relukko(expires_at=expires_at)
    assert upd_lock['expires_at'] == expires_at

    upd_lock = relukko.update_relukko(expires_at="2099-12-01T23:12:00.123456Z")
    expires_at = datetime.fromisoformat("2099-12-01T23:12:00.123456Z")
    assert upd_lock['expires_at'] == expires_at


def test_delete_relukko(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("delete_me", "12s", "PyTest")
    locks = relukko.get_all_relukkos()
    assert lock in locks
    assert relukko.lock == lock
    assert relukko.lock_id == lock['id']

    relukko.delete_relukko()
    locks = relukko.get_all_relukkos()
    assert lock not in locks
    assert relukko.lock is None
    assert relukko.lock_id is None


def test_get_current_relukko(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("try_to_catch_me", "12s", "PyTest")
    id = lock['id']

    # use pyrelukko client directly, so cache is not updated
    relukko.client.update_relukko(id, creator="TestMe")

    cached = relukko.get_current_relukko(refresh=False)
    assert cached['creator'] == "PyTest"

    refreshed = relukko.get_current_relukko(refresh=True)
    assert refreshed['creator'] == "TestMe"


def test_get_relukko_expires_at_time(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("what_is_my_expire_time", "12s", "PyTest")
    id = lock['id']

    # use pyrelukko client directly, so cache is not updated
    expires_at = datetime.fromisoformat("2099-12-31T12:34:56.789Z")
    relukko.client.update_relukko(id, expires_at=expires_at)

    cached = relukko.get_relukko_expires_at_time(refresh=False)
    assert cached == lock.expires_at

    refreshed = relukko.get_relukko_expires_at_time(refresh=True)
    assert refreshed == expires_at

def test_get_relukko_created_at_time(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("what_is_my_created_time", "12s", "PyTest")

    cached = relukko.get_relukko_created_at_time(refresh=False)
    assert cached == lock.created_at

    refreshed = relukko.get_relukko_created_at_time(refresh=True)
    assert refreshed == lock.created_at

def test_acquire_relukko_for_test_with_test_case_id(
        monkeypatch, relukko_backend):
    relukko, _ = relukko_backend
    with monkeypatch.context() as m:
        def mock_get_var_val(*args, **kwargs):
            return [
                "some tag",
                "an other tag",
                "new",
                "test_case_id:c0359cb9-fa1e-4215-8eff-6a8877e91dd8",
            ]

        m.setattr(BuiltIn, "get_variable_value", mock_get_var_val)
        lock = relukko.acquire_relukko_for_test()
        assert lock['lock_name'] == "c0359cb9-fa1e-4215-8eff-6a8877e91dd8"


def test_acquire_relukko_for_test_without_test_case_id(
        monkeypatch, relukko_backend):
    relukko, _ = relukko_backend
    with monkeypatch.context() as m:
        def mock_get_var_val(self, name, *args, **kwargs):
            match name:
                case "${TEST NAME}":
                    return "Test Name Verify Bar"
                case "${SUITE NAME}":
                    return "Suite Name Foo"
                case "@{TEST TAGS}":
                    return ["new", "foo", "bar"]

        m.setattr(BuiltIn, "get_variable_value", mock_get_var_val)
        lock = relukko.acquire_relukko_for_test()
        assert lock['lock_name'] == "Suite Name Foo:Test Name Verify Bar"


def test_get_locks(relukko_backend):
    relukko, _ = relukko_backend
    lock01 = relukko.acquire_relukko("lock01", "12s", "PyTest")
    lock02 = relukko.acquire_relukko("lock02", "12s", "PyTest")
    lock03 = relukko.acquire_relukko("lock03", "12s", "PyTest")

    locks = relukko.get_all_relukkos()

    assert lock01 in locks
    assert lock02 in locks
    assert lock03 in locks
