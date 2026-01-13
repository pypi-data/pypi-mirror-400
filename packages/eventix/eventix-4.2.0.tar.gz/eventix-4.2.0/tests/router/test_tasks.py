import logging

from freezegun import freeze_time
from pydantic_db_backend_common.pagination import pagination_convert_response_list
from pydantic_db_backend_common.pydantic import PaginationResponseModel

from eventix.contexts import namespace_context, worker_id_context
from eventix.pydantic.task import TEventixTask
from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_tasks import demotask

log = logging.getLogger(__name__)


@all_clients()
def test_route_tasks_next_scheduled(app_client, client):
    amount = 1
    with cleanup(client):
        with worker_id_context() as worker_id:
            with namespace_context() as namespace:
                with freeze_time("2022-01-01"):
                    for i in range(amount):
                        demotask.delay(value=i, _priority=i)

                for i in range(amount):
                    r = app_client.get(
                        "/tasks/next_scheduled",
                        params=dict(worker_id=worker_id, namespace=namespace),
                    )
                    tm = TEventixTask.model_validate_json(r.content)
                    assert tm.worker_id == worker_id
                    assert tm.status == "processing"

                # getting 204 after last task
                r = app_client.get(
                    "/tasks/next_scheduled",
                    params=dict(worker_id=worker_id, namespace=namespace),
                )
                assert r.status_code == 204


@all_clients()
def test_router_tasks_by_status_put(generate_many_tasks, app_client, client):
    tests = [
        ("scheduled", None, 0, 10, None, dict(length=10)),
        # ("scheduled", None, 0, 0, [], dict(length=200)),
        # ("done", None, 0, 0, [], dict(length=100)),
        ## ("done", None, 0, 20, [], dict(length=20, max_results=100)),
        # ("done", None, 95, 20, [], dict(length=5)),
    ]

    with cleanup(client):
        generate_many_tasks(
            client,
            {"scheduled": 200, "processing": 2, "done": 100, "retry": 50, "error": 30},
        )

        for i, (status, namespace, skip, limit, sort, exp) in enumerate(tests):
            log.info(f"test {i}: {[status, namespace, skip, limit, sort, exp]}")

            params = dict(
                status=status,
                namespace=namespace,
                skip=skip,
                limit=limit,
                sort=sort,
            )

            r = app_client.put("/tasks/by_status", json=params)
            response = PaginationResponseModel.model_validate(r.json())

            if "length" in exp:
                assert len(response.data) == exp["length"]
            if "max_results" in exp:
                assert response.max_results == exp["max_results"]


@all_clients(features=["find_extend_pipeline"])
def test_router_tasks_by_task_put(client, generate_many_tasks, app_client):
    with cleanup(client):
        generate_many_tasks(
            client,
            {
                "scheduled": 10,
                "retry": 5,
                "processing": 2,
                "error": 3,
                "done": 20,
            },
        )

        params = dict(task="demotask", namespace="default", skip=0, limit=100)
        r = app_client.put("/tasks/by_task", json=params)
        rtrm = PaginationResponseModel.model_validate(r.json())
        print(rtrm.max_results, len(rtrm.data))
        data = pagination_convert_response_list(rtrm, TEventixTask)
        for d in data:
            print(f"[{d.status:>10s}] {d.uid} {d.scheduled}")
