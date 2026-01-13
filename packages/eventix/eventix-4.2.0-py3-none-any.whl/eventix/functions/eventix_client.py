from __future__ import annotations

import logging
import sys
from typing import Any, List

from lsrestclient import LsRestClient

from eventix.contexts import (
    delay_tasks_context_var,
    namespace_context,
    namespace_context_var,
)
from eventix.exceptions import NoTaskFoundForUniqueKey
from eventix.functions.errors import raise_errors
from eventix.pydantic.event import TEventixEvent
from eventix.pydantic.settings import EventixClientSettings
from eventix.pydantic.task import EventixTaskStatusEnum, TEventixTask

log = logging.getLogger(__name__)


# class EventixClientSession(LsRestClient):
#     def __init__(self, base_url: str = None) -> None:
#         self.client = LsRestClient(base_url, name="")
#         self.base_url = base_url
#         super().__init__()
#
#     def request(
#         self,
#         method,
#         url,
#         *args,
#         **kwargs
#     ) -> Response:  # pragma: no cover
#         return requests.request(
#             method,
#             f"{self.base_url}{url}",
#             *args,
#             **kwargs
#         )


def get_client():
    s = LsRestClient(base_url="nohost://", name="eventix_client")
    # s.headers["Connection"] = "close"
    return s


class EventixClient:
    # interface: Any | None = EventixClientSession()
    interface: Any | None = get_client()
    namespace: str | None = None

    @classmethod
    def set_base_url(cls, base_url):
        if isinstance(cls.interface, LsRestClient):
            log.debug(f"Setting EventixClient base_url: {base_url}")
            cls.interface.base_url = base_url

    @classmethod
    def config(cls, config: dict):
        # Be aware that the namespace context is set direct through
        # the context variable.... so no reset possible

        # noinspection PyArgumentList
        settings = EventixClientSettings()
        cls.set_base_url(settings.eventix_url)

        namespace = ""
        if "namespace" in config:
            namespace = config["namespace"]

        if namespace == "":
            namespace = settings.eventix_namespace

        if namespace == "":
            log.error("No EVENTIX_NAMESPACE set.")
            sys.exit()

        namespace_context_var.set(namespace)
        if not settings.eventix_delay_tasks:
            log.info("ATTENTION!!!: Delay tasks disabled. All tasks are run directly. No delay.")
        delay_tasks_context_var.set(settings.eventix_delay_tasks)

    @classmethod
    def post_event(cls, event: TEventixEvent) -> List[TEventixTask]:
        with namespace_context() as namespace:
            event.namespace = namespace
            r = cls.interface.post("/event", body=event.model_dump())
            with raise_errors(r, []):
                json = r.json()
                assert isinstance(json, list)
                return [TEventixTask(**t) for t in json]

    @classmethod
    def get_task_by_unique_key_and_namespace(
        cls, unique_key: str, namespace: str = None, stati: list[EventixTaskStatusEnum] = None
    ) -> TEventixTask:
        params = {
            "stati": [EventixTaskStatusEnum.scheduled.value, EventixTaskStatusEnum.retry.value]
            if stati is None
            else stati
        }

        r = cls.interface.get(f"/task/by_unique_key/{namespace}/{unique_key}", params=params)
        if r.status_code == 404:
            r_data = r.json()
            error_class = r_data.get("error_class")
            if error_class == "NoTaskFoundForUniqueKey":
                raise NoTaskFoundForUniqueKey(unique_key=unique_key, stati=stati)

        with raise_errors(r, []):
            j = r.json()
            return TEventixTask.model_validate(j)

    @classmethod
    def ping(cls) -> bool:
        try:
            r = cls.interface.get("/healthz")
            return r.status_code == 200
        except Exception as e:
            log.exception("Error while pinging Eventix server.")
            log.error(e)
            return False
