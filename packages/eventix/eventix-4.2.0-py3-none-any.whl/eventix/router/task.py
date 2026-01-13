import datetime
import logging

from fastapi import APIRouter
from fastapi.params import Query
from pydantic_db_backend.backend import Backend

from eventix.functions.task import task_by_unique_key, task_post, task_reschedule
from eventix.pydantic.task import EventixTaskStatusEnum, TEventixTask

log = logging.getLogger(__name__)

router = APIRouter(tags=["task"])


@router.post("/task")
async def route_task_post(task: TEventixTask) -> TEventixTask:
    return task_post(task)


@router.get("/task/{uid}")
async def route_task_get(uid: str) -> TEventixTask:
    # noinspection PyTypeChecker
    return Backend.client().get_instance(TEventixTask, uid)


@router.delete("/task/{uid}")
async def route_task_delete(uid: str) -> None:
    return Backend.client().delete_uid(TEventixTask, uid)


@router.get("/task/{uid}/reschedule")
async def route_task_reschedule_get(uid: str, eta: datetime.datetime | None = None):
    return task_reschedule(uid, eta)


@router.get("/task/by_unique_key/{unique_key}")
async def router_task_by_unique_key_get(unique_key: str) -> TEventixTask:
    """
    !!!DEPRECATED: use router_task_by_unique_key_for_namespace_get instead

    Fetch a task based on its unique key.

    This asynchronous endpoint retrieves a task identified by
    a given unique key.

    :param unique_key: A string representing the unique key of the task to fetch.
    :return: The task object corresponding to the provided unique key.
    """
    return task_by_unique_key(unique_key=unique_key)


@router.get("/task/by_unique_key/{namespace}/{unique_key}")
async def router_task_by_unique_key_for_namespace_get(
    unique_key: str, namespace: str, stati: list[EventixTaskStatusEnum] = Query(None)
) -> TEventixTask:
    if stati is None:
        stati = [EventixTaskStatusEnum.scheduled, EventixTaskStatusEnum.retry]
    ret = task_by_unique_key(unique_key=unique_key, namespace=namespace, stati=stati)
    return ret


@router.delete("/task/by_unique_key/{unique_key}")
async def route_task_(unique_key: str) -> None:
    uid = task_by_unique_key(unique_key=unique_key).uid
    return Backend.client().delete_uid(TEventixTask, uid)


@router.put("/task/{uid}")
async def route_task_put(uid: str, task: TEventixTask) -> TEventixTask:
    task.uid = uid  # overwrite uid
    # noinspection PyTypeChecker
    return Backend.client().put_instance(task)
