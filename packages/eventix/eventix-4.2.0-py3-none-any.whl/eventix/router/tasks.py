import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from pydantic_db_backend.fastapi import dep_pagination_parameters
from pydantic_db_backend.pagination import pagination_response
from pydantic_db_backend_common.pydantic import PaginationResponseModel

from eventix.exceptions import NoTaskFound
from eventix.functions.task import (
    task_next_scheduled,
    tasks_by_status,
    tasks_by_task,
    tasks_dump,
)
from eventix.pydantic.pagination import PaginationParametersModel
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


@router.get("/tasks/next_scheduled")
async def route_tasks_next_scheduled_get(worker_id: str, namespace: str) -> TEventixTask:
    t = task_next_scheduled(worker_id, namespace)
    if t is None:
        raise NoTaskFound(namespace=namespace)
    return t


@router.put("/tasks/by_status")
async def router_tasks_by_status_put(
    status: Annotated[str, Body()] = None,
    namespace: Annotated[str, Body()] = None,
    pagination: PaginationParametersModel = Depends(dep_pagination_parameters),
) -> PaginationResponseModel:
    tasks = tasks_by_status(status=status, namespace=namespace)
    response = pagination_response(tasks)
    return response


@router.put("/tasks/by_task")
async def router_tasks_by_task_put(
    task: Annotated[str, Body()],
    namespace: Annotated[str, Body()] = None,
    pagination: PaginationParametersModel = Depends(dep_pagination_parameters),
) -> PaginationResponseModel:
    tasks = tasks_by_task(task=task, namespace=namespace)
    response = pagination_response(tasks)
    return response


@router.put("/tasks/dump")
async def router_tasks_uids(
    pagination: PaginationParametersModel = Depends(dep_pagination_parameters),
) -> PaginationResponseModel:
    tasks = tasks_dump()
    response = pagination_response(tasks)
    return response
