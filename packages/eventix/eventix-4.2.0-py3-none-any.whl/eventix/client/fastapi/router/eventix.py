import os

from fastapi import APIRouter, FastAPI, Query

from eventix.functions.eventix_client import EventixClient
from eventix.pydantic.task import EventixTaskStatusEnum

router = APIRouter(prefix="", tags=["eventix"])


@router.get("/task/by_unique_key/{unique_key}")
def router_task_by_unique_key_for_namespace_get(unique_key: str, stati: list[EventixTaskStatusEnum] = Query(None)):
    if stati is None:
        stati = [
            EventixTaskStatusEnum.scheduled.value,
            EventixTaskStatusEnum.retry.value,
        ]
    namespace = os.environ.get("EVENTIX_NAMESPACE", None)
    r = EventixClient.get_task_by_unique_key_and_namespace(unique_key, namespace=namespace, stati=stati)
    return r.model_dump_json()


def fastapi_eventix_router_wrapper(app: FastAPI):
    app.include_router(router)
