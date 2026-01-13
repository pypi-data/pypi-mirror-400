import freezegun
import pytest
from pydantic_db_backend.contexts.pagination_parameter import (
    pagination_parameter_provider,
)
from pydantic_db_backend_common.pydantic import PaginationParameterModel

from eventix.functions.relay import RelayManager
from eventix.functions.task import task_post
from eventix.functions.tools import uid
from eventix.pydantic.relay import RelayModel
from eventix.pydantic.task import TEventixTask
from tests.fixtures.backend import all_clients, cleanup


@all_clients()
def test_task_post_uniqueness(client):
    with cleanup(client):
        tm1 = TEventixTask(unique_key="uni", task="demotask", priority=1)
        tm1_ret = task_post(tm1)
        print(tm1)
        print()
        print(tm1_ret)
        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == 1

        tm2 = tm1.model_copy()
        tm2.uid = uid()

        tm2_ret = task_post(tm2)

        assert tm2_ret.uid == tm1.uid  # gets the uid of the first, since this one gets overwritten
        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == 1
        assert tm1.uid == instances.data[0].uid

        # now check if retry gets overwritten as well

        # tune existing record to have a retry status
        tm3 = tm2_ret.model_copy()
        tm3.status = "retry"
        client.put_instance(tm3)

        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == 1
        assert tm3.uid == instances.data[0].uid
        assert "retry" == instances.data[0].status

        # now overwrite with scheduled

        tm4 = tm1.model_copy()
        tm4.uid = uid()

        task_post(tm4)

        assert tm2_ret.uid == tm1.uid  # gets the uid of the first, since this one gets overwritten

        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == 1
        assert tm1.uid == instances.data[0].uid
        assert "scheduled" == instances.data[0].status


@all_clients()
@freezegun.freeze_time("2023-01-01T10:00:00")
def test_router_task_post(app_client, client):
    amount = 10
    with cleanup(client):
        for i in range(amount):
            tm = TEventixTask(task="demotask", priority=1)
            json = tm.model_dump()
            app_client.post("/task", body=json)

        with pagination_parameter_provider(PaginationParameterModel(limit=amount + 1)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == amount


@pytest.mark.skip(reason="external dependency")
@all_clients()
@freezegun.freeze_time("2023-01-01T10:00:00")
def test_router_task_post_relay(app_client, client):
    RelayManager.relays = {}
    RelayManager.add_relay(RelayModel(url="http://k12-test.lsoft.online:30010", namespace="gammel"))
    amount = 1
    with cleanup(client):
        for i in range(amount):
            tm = TEventixTask(task="demotask", namespace="gammel", priority=1)
            json = tm.model_dump()
            app_client.post("/task", body=json)

        # with pagination_parameter_provider(PaginationParameterModel(limit=amount + 1)):
        #     instances = client.get_instances(TaskModel)
        # assert len(instances.data) == amount


@all_clients()
@freezegun.freeze_time("2023-01-01T10:00:00")
def test_router_task_post_pokemon(client, app_client):
    amount = 10
    with cleanup(client):
        for i in range(amount):
            tm = TEventixTask(task="demotask", priority=1, kwargs={"data": "Pokémon"})
            json = tm.model_dump_json()
            app_client.post("/task", data=json)
        with pagination_parameter_provider(PaginationParameterModel(limit=amount + 1)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == amount


@all_clients()
def test_route_task_get(app_client, client):
    with cleanup(client):
        tm = TEventixTask(task="demotask", priority=1)
        app_client.post("/task", data=tm.json())

        r = app_client.get(f"/task/{tm.uid}")
        assert r.status_code == 200
        assert r.json()["uid"] == tm.uid


@all_clients()
def test_route_task_delete(app_client, client):
    with cleanup(client):
        tm = TEventixTask(task="demotask", priority=1)
        app_client.post("/task", data=tm.model_dump_json())

        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == 1

        app_client.delete(f"/task/{tm.uid}")

        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            instances = client.get_instances(TEventixTask)
        assert len(instances.data) == 0


@all_clients()
def test_route_task_update(app_client, client):
    with cleanup(client):
        tm = TEventixTask(task="demotask", priority=1)
        r = app_client.post("/task", data=tm.json())
        tm2 = TEventixTask.parse_raw(r.content)

        tm2.kwargs = dict(a=1)

        r = app_client.put(f"/task/{tm.uid}", data=tm2.json())
        assert r.status_code == 200
        tm3 = TEventixTask.parse_raw(r.content)

        r = app_client.put(f"/task/{tm.uid}", data=tm2.json())
        assert r.status_code == 409

        tm3.kwargs = dict(b=2)
        r = app_client.put(f"/task/{tm.uid}", data=tm3.json())
        assert r.status_code == 200
