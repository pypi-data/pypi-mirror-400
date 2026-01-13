import os

import pytest
from pyrelukko.testcontainers import RelukkoContainer, RelukkoDbContainer
from testcontainers.core.network import Network

from Relukko import Relukko


@pytest.fixture(scope="session")
def relukko_backend():
    if os.environ.get("CI_HAS_RELUKKO"):
        # Gitlab does not allow DinD networks, so Relukko runs as a service
        # in the background of the job.
        relukko = Relukko(
            base_url=os.environ['CI_RELUKKO_BASE_URL'],
            api_key=os.environ['CI_RELUKKO_API_KEY']
        )
        yield relukko, None
        # clean up all locks from DB!
        locks = relukko.get_all_relukkos()
        for lock in locks:
            relukko.client.delete_relukko(lock['id'])
    else:
        with Network() as rl_net:
            with RelukkoDbContainer(net=rl_net,
                image="postgres:17", hostname="relukkodb") as _db:
                db_url = "postgresql://relukko:relukko@relukkodb/relukko"
                with RelukkoContainer(rl_net, db_url=db_url) as backend:
                    relukko = Relukko(
                        base_url=backend.get_api_url(), api_key="somekey")
                    yield relukko, backend


@pytest.fixture(scope="function")
def mock_env_relukko_skip(monkeypatch):
    monkeypatch.setenv("RELUKKO_TRUST_ME_IT_IS_LOCKED", "yes")
    yield
    monkeypatch.delenv("RELUKKO_TRUST_ME_IT_IS_LOCKED", raising=True)

