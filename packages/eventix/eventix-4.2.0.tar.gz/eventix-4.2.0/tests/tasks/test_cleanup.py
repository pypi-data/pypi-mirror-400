from freezegun import freeze_time
from pydantic_db_backend_common.pydantic import PaginationParameterModel

from eventix.pydantic.task import TEventixTask
from eventix.tasks.cleanup import task_cleanup_results, task_cleanup_worker
from tests.conftest import dt
from tests.fixtures.backend import all_clients, cleanup, mongodb_client_only


# @all_clients()
@mongodb_client_only
def test_task_cleanup_worker(client):
    with cleanup(client):
        with freeze_time("2022-01-02"):
            t = TEventixTask(task="old_task", worker_id="123", worker_expires=dt("2022-01-01"))
            client.put_instance(t)

            t = TEventixTask(task="old_task", worker_id="123", worker_expires=dt("2022-01-03"))
            client.put_instance(t)

            task_cleanup_worker.run()

            tasks = client.get_instances(
                TEventixTask,
                PaginationParameterModel(limit=10, filter={"worker_expires": None}),
            )
            assert len(tasks.data) == 1


@all_clients()
def test_task_cleanup_results(client):
    with cleanup(client):
        with freeze_time("2022-01-02"):
            t = TEventixTask(task="old_task", worker_id="123", expires=dt("2022-01-01"))
            client.put_instance(t)

            t = TEventixTask(task="old_task", worker_id="123", expires=dt("2022-01-03"))
            client.put_instance(t)

            task_cleanup_results.run()

            tasks = client.get_instances(TEventixTask, PaginationParameterModel(limit=10))
            assert len(tasks.data) == 1
