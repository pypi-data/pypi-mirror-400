import pytest
from eventix.functions.core import task
from eventix.pydantic.task import EventixTaskStatusEnum, TEventixTask
from pydantic_db_backend.contexts.pagination_parameter import (
    pagination_parameter_provider,
)
from pydantic_db_backend_common.pydantic import PaginationParameterModel
from tests.fixtures.backend import all_clients, cleanup

@all_clients()
def test_task_default_priority(client):
    @task(default_priority=5)
    def priority_task(test_value: str):
        return dict(test_value=test_value)

    with cleanup(client):
        # Case 1: Use default priority from decorator
        priority_task.delay(test_value="default")

        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=10)
        ):
            tasks = list(client.get_instances(TEventixTask).data)
            existing_task = next(t for t in tasks if t.task == "priority_task" and t.kwargs["test_value"] == "default")

        # Note: priority is negated in delay()
        assert existing_task.priority == -5

        # Case 2: Override default priority with _priority parameter
        priority_task.delay(test_value="override", _priority=10)

        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=10)
        ):
            tasks = list(client.get_instances(TEventixTask).data)
            existing_task = next(t for t in tasks if t.task == "priority_task" and t.kwargs["test_value"] == "override")

        assert existing_task.priority == -10

@all_clients()
def test_task_default_priority_zero(client):
    @task() # default_priority should be 0
    def priority_task_zero(test_value: str):
        return dict(test_value=test_value)

    @task(default_priority=0)
    def priority_task_explicit_zero(test_value: str):
        return dict(test_value=test_value)

    with cleanup(client):
        priority_task_zero.delay(test_value="zero")
        priority_task_explicit_zero.delay(test_value="explicit_zero")

        with pagination_parameter_provider(
            PaginationParameterModel(filter={"status": EventixTaskStatusEnum.scheduled}, limit=10)
        ):
            tasks = list(client.get_instances(TEventixTask).data)
            t1 = next(t for t in tasks if t.task == "priority_task_zero")
            t2 = next(t for t in tasks if t.task == "priority_task_explicit_zero")

        assert t1.priority == 0
        assert t2.priority == 0
