import datetime
import logging

import pytest
from freezegun import freeze_time
from pydantic_db_backend_common.utils import utcnow

from eventix.contexts import namespace_provider
from eventix.functions.eventix_client import EventixClient

pytest_plugins = [
    "tests.fixtures.docker_compose",
    "tests.fixtures.app_client",
    "tests.fixtures.backend",
    "tests.fixtures.demo_tasks",
    "tests.fixtures.worker",
]


@pytest.fixture(autouse=True)
def setup_logging():
    # turn off logging for httpx in pytest ( access log of flask )
    logging.getLogger("httpx").setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def eventix_client(app_client):
    EventixClient.interface = app_client
    EventixClient.namespace = "pytest"
    EventixClient.set_base_url("")
    # EventflowClient.set_base_url("http://localhost:8000")


@pytest.fixture(autouse=True)
def namespace():
    with namespace_provider("pytest"):
        yield


def time_or_none(seconds: int | None):
    return None if seconds is None else utcnow() + datetime.timedelta(seconds=seconds)


def check_time_or_none(t: datetime.datetime, seconds: int | None):
    if seconds is None:
        assert t is None
    else:
        assert t == utcnow() + datetime.timedelta(seconds=seconds)


def dt(dt_str: str) -> datetime.datetime:
    with freeze_time(dt_str):
        return utcnow()
