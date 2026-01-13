import datetime
import logging
from contextlib import nullcontext
from types import NoneType

import pytest
from freezegun import freeze_time
from pydantic_db_backend_common.pydantic import PaginationParameterModel
from pydantic_db_backend_common.utils import utcnow
from webexception.webexception import WebException

from eventix.exceptions import NoTaskFoundForUniqueKey, TaskUniqueKeyNotUnique, WrongTaskStatus
from eventix.functions.core import task
from eventix.functions.task import (
    task_by_unique_key,
    task_clean_expired_workers,
    task_next_scheduled,
    task_post,
    task_reschedule,
    tasks_by_status,
    tasks_by_task,
    tasks_dump,
)
from eventix.pydantic.task import EventixTaskStatusEnum, TEventixTask
from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_tasks import demotask

log = logging.getLogger(__name__)


@all_clients()
@pytest.mark.parametrize("amount, ret_type", [(0, NoneType), (4, TEventixTask)])
def test_task_next_scheduled(client, amount, ret_type, register_tasks):
    with freeze_time("2022-01-01"):
        with cleanup(client):
            for i in range(amount):
                demotask.delay(
                    value=i,
                    _priority=i,
                    _eta=datetime.datetime(year=2009, month=11, day=1),
                )

            worker_id = "worker123"
            t = task_next_scheduled(worker_id=worker_id, namespace="pytest")
            assert isinstance(t, ret_type)

            if ret_type == TEventixTask:
                # check task specific things
                assert t.worker_id == worker_id
                assert t.status == "processing"

                with freeze_time("2022-01-01 00:05:00"):
                    assert t.worker_expires == utcnow()


@all_clients()
@pytest.mark.parametrize("amount, ret_type", [(4, TEventixTask)])
def test_task_next_scheduled_concurency(client, amount, ret_type):
    worker_id1 = "worker123"
    with freeze_time("2022-01-01"):
        with cleanup(client):
            t1 = TEventixTask(
                task="demo",
                args=(1,),
                namespace="pytest",
                worker_id=None,
                worker_expires=None,
                # worker_id=worker_id1,
                # worker_expires=utcnow()+datetime.timedelta(days=1)
            )
            client.put_instance(t1)

            # demotask.delay(value=i, _priority=i)

            st1 = task_next_scheduled(worker_id=worker_id1, namespace="pytest")
            if st1 is not None:
                log.debug("got " + st1.uid)
            # t2 = task_next_scheduled(worker_id=worker_id2, namespace="pytest")
            # log.debug(t2.uid)


@all_clients()
def test_task_clean_expired_workers(client):
    worker_id = "worker123"
    amount = 3
    namespace = "pytest"

    with cleanup(client):
        with freeze_time("2022-01-01"):
            for i in range(amount):
                demotask.delay(value=i, _priority=i)
                task_next_scheduled(worker_id=worker_id, namespace=namespace)

            assert task_next_scheduled(worker_id=worker_id, namespace=namespace) is None

        with freeze_time("2022-01-01 00:10:00"):
            task_clean_expired_workers()


class DemoException(WebException):
    pass


@all_clients()
def test_tasks_by_status(client, generate_many_tasks):
    tests = [
        ("scheduled", None, 0, 10, None, dict(length=10, max_results=20)),
        # ("scheduled", None, 0, 0, [], dict(length=200)),
        # ("done", None, 0, 0, [], dict(length=100)),
        # ("done", None, 0, 20, [], dict(length=20, max_results=100)),
        # ("done", None, 95, 20, [], dict(length=5)),
    ]

    with cleanup(client):
        generate_many_tasks(
            client,
            {
                "scheduled": 20,
                # "scheduled": 200,
                # "processing": 2,
                # "done": 100,
                # "retry": 50,
                # "error": 30
            },
        )

        for i, (status, namespace, skip, limit, sort, exp) in enumerate(tests):
            log.info(f"test {i}: {[status, namespace, skip, limit, sort, exp]}")

            # noinspection PyTypeChecker
            tasks = tasks_by_status(
                status=status,
                namespace=namespace,
                pagination_parameter=PaginationParameterModel(skip=skip, limit=limit, sort=sort),
            )

            if "length" in exp:
                assert len(tasks.data) == exp["length"]

            if "max_results" in exp:
                assert tasks.max_results == exp["max_results"]


@all_clients(features=["find_extend_pipeline"])
def test_tasks_by_task(client, generate_many_random_tasks):
    with cleanup(client):
        generate_many_random_tasks(
            client,
            {
                "done": 20,
                "error": 3,
                "scheduled": 10,
                "retry": 5,
                "processing": 2,
            },
        )
        page_size = 10
        pages = 4

        for i in range(10):
            for page in range(pages):
                tasks = tasks_by_task(
                    task=f"demotask{i}",
                    namespace="default",
                    pagination_parameter=PaginationParameterModel(skip=page * page_size, limit=page_size),
                )
                for d in tasks.data:
                    assert i == int(d.task[-1])
                    print(f"[{d.status:>10s}] {d.uid} {d.scheduled} {d.task}")


@all_clients()
def test_task_by_unique_key(client):
    @task(unique_key_generator=lambda identifier: f"test_unique_id_{identifier}")
    def demo_task() -> dict:
        log.debug("test_unique_id")
        return {}

    with cleanup(client):
        demo_task.delay(identifier=1)
        demo_task.delay(identifier=2)
        demo_task.delay(identifier=3)
        demo_task.delay(identifier=4)
        demo_task.delay(identifier=5)

        for i in (3, 5, 4, 1, 2):
            search_unique_id = f"test_unique_id_{i}"
            assert_value = task_by_unique_key(unique_key=search_unique_id)

            assert assert_value.unique_key == search_unique_id

        git_et_nit_value = "git_et_nit_5"
        with pytest.raises(NoTaskFoundForUniqueKey) as e:
            task_by_unique_key(unique_key=git_et_nit_value)

        assert e.value.unique_id == git_et_nit_value


@all_clients()
def test_task_by_unique_key_namespace(client):
    with cleanup(client):
        unique_key = "1"
        task_post(TEventixTask(unique_key=unique_key, task="demotask", priority=1))
        task_post(TEventixTask(unique_key=unique_key, task="demotask", priority=1, namespace="gammel"))

        with pytest.raises(TaskUniqueKeyNotUnique):
            task_by_unique_key(unique_key=unique_key)

        r = task_by_unique_key(unique_key=unique_key, namespace="gammel")
        assert r.unique_key == unique_key


jan2025 = datetime.datetime(year=2025, month=1, day=1).replace(tzinfo=datetime.timezone.utc)


@all_clients()
@pytest.mark.parametrize(
    "status, eta, ctx",
    [
        (EventixTaskStatusEnum.error, None, nullcontext()),
        (EventixTaskStatusEnum.error, jan2025, nullcontext()),
        (EventixTaskStatusEnum.processing, None, pytest.raises(WrongTaskStatus)),
    ],
)
def test_task_reschedule(client, status, eta, ctx):
    with cleanup(client):
        with ctx:
            t = client.put_instance(TEventixTask(task="demotask", status=status))
            t2 = task_reschedule(t.uid, eta)
            assert t2.status == "scheduled"
            if eta is not None:
                assert t2.eta == eta


@all_clients(features=["find_extend_pipeline"])
def test_tasks_dump(client, generate_many_tasks):
    with cleanup(client):
        generate_many_tasks(
            client,
            {
                "done": 20,
                "error": 3,
                "scheduled": 10,
                "retry": 5,
                "processing": 2,
            },
        )
        tasks = tasks_dump(PaginationParameterModel(skip=0, limit=10))
        assert len(tasks.data) == 10
        assert tasks.max_results == 40
