import os

import pytest
from lsrestclient import LsRestClientTestClient
from pydantic_db_backend.backends.mongodb import MongoDbBackend
from pytest_lazyfixture import lazy_fixture
from starlette.testclient import TestClient


@pytest.fixture(scope="session")
def app_client():
    os.environ["APP_CLIENT"] = "true"
    from main import app

    return LsRestClientTestClient(TestClient(app))


@pytest.fixture(scope="session")
def cli_app_client(client_mongodb_session):
    os.environ["APP_CLIENT"] = "true"
    from main import app

    client = MongoDbBackend()
    LsRestClientTestClient(TestClient(app), name="eventix")
    return client


def cli_client(func):
    return pytest.mark.parametrize(
        "client",
        [(lazy_fixture("cli_app_client"))],
    )(func)
