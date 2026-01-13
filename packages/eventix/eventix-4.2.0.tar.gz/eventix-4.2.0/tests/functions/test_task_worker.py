from types import NoneType
from typing import Any, Dict

import pytest
from freezegun import freeze_time
from pydantic_db_backend.contexts.pagination_parameter import (
    pagination_parameter_provider,
)
from pydantic_db_backend_common.pydantic import PaginationParameterModel
from pydantic_db_backend_common.utils import utcnow

from eventix.functions.task_scheduler import TaskScheduler
from eventix.functions.task_worker import TaskWorker
from eventix.pydantic.task import TEventixTask
from tests.conftest import check_time_or_none, time_or_none
from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_tasks import default_operator, demotask, demotask_consuming_task_context, demotask_unregistered
from tests.functions.test_task import DemoException


@all_clients()
def test_task_next_scheduled(client):
    with cleanup(client):
        t = TaskWorker.task_next_scheduled()
        assert t is None
        t = demotask.delay(value=1, _priority=1)
        t2 = TaskWorker.task_next_scheduled()
        assert t.uid == t2.uid


def test_register_tasks():
    TaskWorker.register_tasks(["tests.fixtures.demo_task"])


@all_clients()
def test_listen(client):
    amount = 1
    with cleanup(client):
        with freeze_time("2022-01-01"):
            for i in range(amount):
                demotask.delay(value=i, _priority=i)

        TaskWorker.listen(endless=False)


@all_clients()
def test_execute_task(client):
    with cleanup(client):
        t = demotask.delay(value=1, _priority=1)
        TaskWorker.execute_task(t)

        t = demotask_unregistered.delay(value=1, _priority=1)
        TaskWorker.execute_task(t)


@all_clients()
def test_execute_task_operator(client, register_tasks, set_env):
    with set_env(APP_NAME=default_operator):
        with cleanup(client):
            t = demotask.delay(value=1)
            TaskWorker.execute_task(t)
            assert t.operator is not None
            assert default_operator in t.operator
            op = "horst"
            t = demotask_consuming_task_context.delay(_operator=op)
            TaskWorker.execute_task(t)
            assert t.operator is not None
            assert t.operator == op


@all_clients()
# @couchdb_client_only
# @mongodb_client_only
@pytest.mark.parametrize(
    "params, checks, error",
    [
        (dict(expires=None), dict(route_put=1, return_type=TEventixTask), False),
        (dict(expires=0), dict(route_delete=1, return_type=NoneType), False),
        (dict(expires=10), dict(route_put=1, return_type=TEventixTask), False),
        (dict(expires=10), dict(route_put=1, return_typ=NoneType), True),
    ],
)
def test_task_write_back(params, checks, error, mocker, client):
    print(id(params))
    expires = params.get("expires", None)
    expires = time_or_none(expires)
    expire_params = {} if expires is None else {"expires": expires}
    t = TEventixTask(task="demotask", **params | expire_params)

    # route_delete = mocker.patch("pydantic_db_backend.backend.Backend.delete_uid")
    route_delete = mocker.patch.object(client, "delete_uid")

    if error:
        mock_params = dict(side_effect=Exception("mocked error"))
    else:
        mock_params = dict(return_value=t)
    # route_put = mocker.patch("pydantic_db_backend.backend.Backend.put_instance", **mock_params)
    route_put = mocker.patch.object(client, "put_instance", **mock_params)

    with cleanup(client):
        t = TaskScheduler.schedule(t)
        r = TaskWorker.task_write_back(t)

    if "route_delete" in checks:
        assert route_delete.call_count == checks["route_delete"]

    if "route_put" in checks:
        assert route_put.call_count == checks["route_put"]

    if "return_type" in checks:
        assert isinstance(r, checks["return_type"])


@all_clients()
def test_check_scheduled_tasks(client):
    with cleanup(client):
        with freeze_time("2022-01-01"):
            TaskWorker.config_schedule(
                {
                    "schedule": [
                        {
                            "schedule": "*/2 * * * *",
                            "task": "demotask",
                            "args": [],
                            "kwargs": {},
                        },
                        {
                            "schedule": "*/5 * * * *",
                            "task": "demotask_unique",
                            "name": "demotask 5min",
                            # "args": [],
                            # "kwargs": {}
                        },
                    ]
                }
            )

        with freeze_time("2022-01-01 00:02:00"):
            TaskWorker.check_scheduled_tasks()
        with freeze_time("2022-01-01 00:05:00"):
            TaskWorker.check_scheduled_tasks()

        with pagination_parameter_provider(PaginationParameterModel(limit=10)):
            tasks = client.get_instances(model=TEventixTask)

        assert len(tasks.data) == 3


@pytest.mark.parametrize(
    "exc, params, rounds, checks",
    [
        (
            Exception("Broken"),
            dict(store_result=True, retry=False),
            1,
            {"status": "error"},
        ),
        (
            {"error": "Broken"},
            dict(store_result=True, retry=False),
            1,
            {"status": "error"},
        ),
        (
            DemoException("Broken"),
            dict(store_result=True),
            1,
            {"eta": 30, "status": "retry"},
        ),
        (
            DemoException("Broken"),
            dict(store_result=True),
            8,
            {"eta": 300, "status": "retry"},
        ),
        (
            DemoException("Broken"),
            dict(error_expires=86400, max_retries=0),
            1,
            {"expires": 86400, "state": "error"},
        ),
        (
            DemoException("Broken"),
            dict(error_expires=86400, max_retries=1),
            1,
            {"expires": None, "state": "retry"},
        ),
        (
            DemoException("Broken"),
            dict(error_expires=86400, max_retries=1),
            2,
            {"expires": 86400, "state": "error"},
        ),
        (
            {"error": "Broken"},
            dict(retry=True, worker_id="123", worker_expires=utcnow()),
            1,
            {"status": "retry", "worker_id": None, "worker_expires": None},
        ),
        (
            {"error": "Broken"},
            dict(retry=False, worker_id="123"),
            1,
            {"status": "error", "worker_id": "123", "worker_expires": None},
        ),
    ],
)
def test_task_set_error(exc, params, rounds, checks: Dict[str, Any]):
    with freeze_time("2022-01-01"):
        # test error_eta_inc
        t = TEventixTask(task="demotask", **params)

        for i in range(rounds):
            TaskWorker.task_set_error(t, exc)

        if "eta" in checks:
            assert t.error_eta_inc == checks["eta"]

        if "expires" in checks:
            check_time_or_none(t.expires, checks["expires"])

        if "status" in checks:
            assert t.status == checks["status"]

        if "worker_id" in checks:
            assert t.worker_id == checks["worker_id"]

        if "worker_expires" in checks:
            check_time_or_none(t.worker_expires, checks["worker_expires"])


@pytest.mark.parametrize(
    "exc, params, checks",
    [
        ({"r": 1}, dict(store_result=True), {"status": "done", "expires": 604800}),
        (
            {"r": 1},
            dict(store_result=True, result_expires=3600),
            {"status": "done", "expires": 3600},
        ),
        (
            {"r": 1},
            dict(store_result=True, result_expires=None),
            {"status": "done", "expires": None},
        ),
        (
            {"r": 1},
            dict(store_result=False, result_expires=None),
            {"status": "done", "expires": 0},
        ),
    ],
)
def test_task_set_result(exc, params, checks: Dict[str, Any]):
    with freeze_time("2022-01-01"):
        # test error_eta_inc
        t = TEventixTask(task="demotask", **params)

        TaskWorker.task_set_result(t, exc)

        if "expires" in checks:
            check_time_or_none(t.expires, checks["expires"])

        if "status" in checks:
            assert t.status == checks["status"]

        if "worker_expires" in checks:
            check_time_or_none(t.worker_expires, checks["worker_expires"])
