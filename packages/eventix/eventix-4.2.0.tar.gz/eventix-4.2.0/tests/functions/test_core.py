import datetime
import logging
from pprint import pprint
from typing import Dict, List, Tuple

import pytest
from pydantic import BaseModel
from pydantic_db_backend.contexts.pagination_parameter import (
    pagination_parameter_provider,
)
from pydantic_db_backend_common.pydantic import PaginationParameterModel

from eventix.contexts import delay_tasks, namespace_provider, worker_id_context, worker_id_provider
from eventix.functions.core import namespace_context, task
from eventix.functions.task_worker import TaskWorker
from eventix.pydantic.task import EventixTaskStatusEnum, TEventixTask
from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_tasks import (
    OperatorContextIsEmpty,
    default_operator,
    demo_parent_task,
    demotask,
    demotask_consuming_operator_context,
)

log = logging.getLogger(__name__)


@task(store_result=True)
def gammel(a: int):
    log.info(f"gammel: {a}")
    return a


def render_product_unique_uid(sku: int, org_id: str, render_class: str, version: int, *args, **kwargs):
    return f"{sku}_{org_id}_{render_class}_{version}"


@task(unique_key_generator=render_product_unique_uid)
def render_product(sku: int, org_id: str, render_class: str, version: int):
    log.info(f"rendering {sku} {render_class} for {org_id}")
    return dict(sku=sku, org_id=org_id, render_class=render_class, version=version)


@all_clients()
def test_task(client):
    with cleanup(client):
        pprint(gammel.run(1))
        gammel.delay(1, _priority=99)


@all_clients()
def test_task_operator_context(client, register_tasks, set_env):
    op = "horst"
    with set_env(**{"APP_NAME": default_operator}):
        with cleanup(client):
            demotask_consuming_operator_context.delay()
            with pagination_parameter_provider(PaginationParameterModel(limit=1)):
                existing_task = next(iter(client.get_instances(TEventixTask).data), None)
                assert default_operator in existing_task.operator
        with cleanup(client):
            demotask_consuming_operator_context.delay(_operator=op)
            with pagination_parameter_provider(PaginationParameterModel(limit=1)):
                existing_task = next(iter(client.get_instances(TEventixTask).data), None)
                assert existing_task.operator == op

        with cleanup(client):
            with pytest.raises(OperatorContextIsEmpty):
                demotask_consuming_operator_context.run()
            demotask_consuming_operator_context.run(_operator=op)

        with cleanup(client):
            with delay_tasks(False):
                demotask_consuming_operator_context.run(_operator=op)
                with pytest.raises(OperatorContextIsEmpty):
                    demotask_consuming_operator_context.delay()


@all_clients()
def test_multiple_tasks(client):
    with cleanup(client):
        for i in range(100):
            gammel.delay(i)


@all_clients()
def test_schedule_double(client):
    with cleanup(client):
        params = dict(sku=137097, org_id="ESO-1", render_class="erp", version=1, _priority=99)
        for i in range(5):
            params["_priority"] = i
            render_product.delay(**params)


@pytest.mark.parametrize("ns, exp", [("gammel", "gammel"), (None, "default")])
def test_namespace_provider(ns, exp):
    with namespace_provider(ns):
        with namespace_context() as namespace:
            assert namespace == exp


@pytest.mark.parametrize("ns, exp", [("gammel", "gammel"), (None, "default")])
def test_worker_id_provider(ns, exp):
    with worker_id_provider(ns):
        with worker_id_context() as worker_id:
            assert worker_id == exp


class Person(BaseModel):
    name: str
    age: int


def test_restore_pydantic_instances():
    class GammelSpec(BaseModel):
        name: str
        gammel_factor: int
        gammel_listen: list[Person]

    @task()
    def demo_pydantic_task(a: int, b: int, c: GammelSpec, root_gammel_listen: list[Person]) -> dict:
        assert isinstance(c, GammelSpec)

        for entry in c.gammel_listen:
            assert isinstance(entry, Person)

        for entry in root_gammel_listen:
            assert isinstance(entry, Person)
        return {"a": a, "b": b, "c": c}

    r = demo_pydantic_task.run(
        a=2,
        b=4,
        c=GammelSpec(name="gammler", gammel_factor=99, gammel_listen=[Person(name="gammler", age=99)]),
        root_gammel_listen=[Person(name="gammler", age=99)],
    )
    print(r)
    r = demo_pydantic_task.run(
        2,
        4,
        dict(name="gammler", gammel_factor=99, gammel_listen=[dict(name="gammler", age=99)]),
        [dict(name="gammler", age=99)],
    )
    print(r)
    r = demo_pydantic_task.run(
        a=2,
        b=4,
        c=dict(name="gammler", gammel_factor=99, gammel_listen=[dict(name="gammler", age=99)]),
        root_gammel_listen=[dict(name="gammler", age=99)],
    )
    print(r)


def test_restore_pydantic_instances_part_2():
    @task()
    def demo_pydantic_task_p2(a: List, b: Dict, c: int) -> dict:
        assert isinstance(a, list)
        assert isinstance(b, dict)
        return {"a": a, "b": b, "c": c}

    demo_pydantic_task_p2.run([1, 2, 3], {"test": 1}, 5)
    demo_pydantic_task_p2.run(a=[1, 2, 3], b={"test": 1}, c=5)


def test_restore_alias_types_1():
    # check if c is of type GammelSpec
    class GammelSpec(BaseModel):
        name: str
        gammel_factor: int

    @task()
    def demo_pydantic_task(a: GammelSpec) -> dict:
        assert isinstance(a, GammelSpec)
        return {"a": a}

    demo_pydantic_task.run(a=dict(name="gammler", gammel_factor=99))


def test_restore_alias_types_2():
    # check if dictionaries works fine
    @task()
    def task_alias_types(products: Dict[int, int], gammel: int | float, gammel_2: Tuple[int, str, float]):
        log.info(f"products: {products}")
        return dict(
            products=products,
            gammel=gammel,
            gammel_2=gammel_2,
        )

    task_alias_types.run(products={5: 6}, gammel=10.0, gammel_2=(1, "a", 5.0))


def test_restore_alias_types_3():
    # check if datetimes works fine
    @task()
    def task_alias_types(a: datetime.datetime):
        assert isinstance(a, datetime.datetime)
        return dict(
            a=a,
        )

    task_alias_types.run(a=datetime.datetime.utcnow())


@all_clients()
def test_data_types_from_tasks_from_db(register_tasks, client):
    # test written because of string/datetime problem
    # make sure that task parameters from type datetime cumming as strings from db.
    # they should be casted later
    with cleanup(client):
        t = demotask.delay(value=1, _priority=1, test_date_time=datetime.datetime.utcnow())
        with pagination_parameter_provider(PaginationParameterModel(limit=1)):
            existing_task = next(iter(client.get_instances(TEventixTask).data), None)
        assert isinstance(existing_task.kwargs["test_date_time"], str)
        TaskWorker.execute_task(t)

        with pagination_parameter_provider(PaginationParameterModel(limit=1)):
            assert_task = next(iter(client.get_instances(TEventixTask).data), None)
        assert assert_task.status == "done"


@all_clients()
def test_task_priority_context(client, register_tasks):
    with cleanup(client):
        t = demo_parent_task.delay(_priority=99)
        TaskWorker.execute_task(t)
        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=2)
        ):
            existing_task = next(iter(client.get_instances(TEventixTask).data), None)
        assert existing_task.priority == 99


@all_clients()
def test_task_with_eta(client, register_tasks):
    @task()
    def task_eta_(test_value: str):
        return dict(test_value=test_value)

    with cleanup(client):
        eta = datetime.datetime(year=2050, month=1, day=1).replace(tzinfo=datetime.timezone.utc)
        task_eta_.delay(test_value="wuhu", _eta=eta)
        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=2)
        ):
            existing_task = next(iter(client.get_instances(TEventixTask).data), None)

        assert existing_task.eta == eta


@all_clients()
def test_task_with_error_eta_max(client):
    error_eta_max = 1800

    @task(error_eta_max=error_eta_max)
    def task_eta_(test_value: str):
        return dict(test_value=test_value)

    with cleanup(client):
        task_eta_.delay(test_value="wuhu")
        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=2)
        ):
            existing_task = next(iter(client.get_instances(TEventixTask).data), None)

        assert existing_task.error_eta_max == error_eta_max


@all_clients()
def test_task_with_error_eta_inc(client):
    error_eta_inc = 35

    @task(error_eta_inc=error_eta_inc)
    def task_eta_(test_value: str):
        return dict(test_value=test_value)

    with cleanup(client):
        task_eta_.delay(test_value="wuhu")
        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=2)
        ):
            existing_task = next(iter(client.get_instances(TEventixTask).data), None)

        assert existing_task.error_eta_inc == error_eta_inc
