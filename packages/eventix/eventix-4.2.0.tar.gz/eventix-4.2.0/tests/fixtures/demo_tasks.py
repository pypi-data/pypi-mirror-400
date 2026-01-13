import datetime
import logging
from random import randint

from tests.fixtures import set_env

assert set_env
import pytest
from lsidentity.contexts import LsiAccountId
from pydantic_db_backend.backend import Backend
from pydantic_db_backend_common.utils import utcnow

from eventix.functions.core import task
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)

default_operator = "EVENTIX_UNKNOWN_OPERATOR"


@task()
def demo_child_task(value: int) -> dict:
    log.debug(f"Executing demo_child_task value: {value}")
    return {"value": value}


@task()
def demo_parent_task() -> dict:
    log.debug("Executing demo_parent_task")
    demo_child_task.delay(303)
    return {}


@task()
def demotask(value: int, test_date_time: datetime.datetime = None) -> dict:
    log.debug(f"Executing demotask value: {value}")
    log.debug(f"Executing demotask test_date_time: {test_date_time}  type: {type(test_date_time)}")
    if test_date_time is not None:
        assert isinstance(test_date_time, datetime.datetime)
    return {"executed": utcnow(), "value": value}


@task(unique_key_generator=lambda: "theoneandonly")
def demotask_unique(value: int) -> dict:
    log.debug(f"Executing demotask value: {value}")
    return {"executed": utcnow(), "value": value}


@task()
def demotask_unregistered(value: int) -> dict:
    log.debug(f"Executing demotask_unregistered value: {value}")
    return {"executed": utcnow(), "value": value}


class TaskContextIsEmpty(Exception):
    pass


class OperatorContextIsEmpty(Exception):
    pass


@task()
def demotask_consuming_task_context() -> dict:
    with LsiAccountId() as t:
        if t is None:
            raise TaskContextIsEmpty()

    return {"executed": utcnow()}


@task()
def demotask_consuming_operator_context() -> dict:
    with LsiAccountId() as op:
        if op is None or default_operator in op:
            raise OperatorContextIsEmpty()
    return {"executed": utcnow()}


@pytest.fixture
def generate_many_tasks():
    def gen(client: Backend, spec: dict):
        for status, amount in spec.items():
            for i in range(amount):
                client.put_instance(TEventixTask(task="demotask", status=status, kwargs={"i": i}))

    return gen


@pytest.fixture
def generate_many_random_tasks():
    def gen(client: Backend, spec: dict):
        for status, amount in spec.items():
            for i in range(amount):
                n = randint(0, 9)
                client.put_instance(TEventixTask(task=f"demotask{n}", status=status, kwargs={"i": i}))

    return gen
