import contextlib
import os
from typing import List

import pytest
from pydantic_db_backend.backend import has_backend_features
from pydantic_db_backend.backends.mongodb import MongoDbBackend
from pytest_lazyfixture import lazy_fixture

from eventix.pydantic.task import TEventixTask


@pytest.fixture
def client_mongodb():
    os.environ["MONGODB_URI"] = "mongodb://localhost:32001/pdb_pytest"
    client = MongoDbBackend(alias="default")
    return client


@pytest.fixture(scope="session")
def client_mongodb_session():
    os.environ["MONGODB_URI"] = "mongodb://localhost:32001/pdb_pytest"
    client = MongoDbBackend(alias="default")
    return client


@contextlib.contextmanager
def cleanup(client):
    client.delete_collection(TEventixTask)
    yield


available_client_fixtures = [("client_mongodb", MongoDbBackend)]


def all_clients(features: List[str] | None = None):
    client_fixtures = [
        (lazy_fixture(name)) for name, backend in available_client_fixtures if has_backend_features(backend, features)
    ]

    def inner(func):
        return pytest.mark.parametrize("client", client_fixtures)(func)

    return inner


def couchdb_client_only(func):
    return pytest.mark.parametrize(
        "client",
        [(lazy_fixture("client_couchdb"))],
    )(func)


def mongodb_client_only(func):
    return pytest.mark.parametrize(
        "client",
        [(lazy_fixture("client_mongodb"))],
    )(func)
