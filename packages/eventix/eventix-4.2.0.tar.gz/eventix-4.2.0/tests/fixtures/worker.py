import pytest

from eventix.functions.task_worker import TaskWorker


@pytest.fixture(autouse=False, scope="session")
def register_tasks():
    TaskWorker.register_tasks(["tests.fixtures.demo_tasks"])

    # noinspection PyProtectedMember
    del TaskWorker._tasks["demotask_unregistered"]  # hack to have it unregistered
