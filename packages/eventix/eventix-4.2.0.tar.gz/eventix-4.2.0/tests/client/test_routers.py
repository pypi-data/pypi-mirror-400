import pytest
from fastapi import FastAPI
from lsrestclient import LsRestClientTestClient
from starlette.testclient import TestClient

from eventix.client.fastapi.router.eventix import fastapi_eventix_router_wrapper
from eventix.exceptions import NoTaskFoundForUniqueKey
from eventix.functions.task import task_post
from eventix.pydantic.task import TEventixTask
from tests.fixtures.backend import all_clients, cleanup


@all_clients()
def test_route_event_post(client, set_env):
    with cleanup(client):
        with set_env(**{"EVENTIX_NAMESPACE": "default"}):
            unique_key = "555"
            task_post(TEventixTask(unique_key=unique_key, task="demotask", priority=1))
            app = FastAPI()
            fastapi_eventix_router_wrapper(app)
            app_client = LsRestClientTestClient(TestClient(app))
            r = app_client.get(f"/task/by_unique_key/{unique_key}")
            print(r)
            with pytest.raises(NoTaskFoundForUniqueKey):
                r = app_client.get("/task/by_unique_key/git_et_net")
            print(r)
