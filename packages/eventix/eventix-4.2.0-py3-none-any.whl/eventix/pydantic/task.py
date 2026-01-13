from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, Literal, Self

from pydantic import Field
from pydantic_db_backend_common.indexes import AggregationIndex, SortingIndex
from pydantic_db_backend_common.pydantic import BackendModel
from pydantic_db_backend_common.utils import utcnow


class EventixTaskStatusEnum(str, Enum):
    scheduled = "scheduled"
    processing = "processing"
    done = "done"
    error = "error"
    retry = "retry"


TEventixTaskStatusLiteral = Literal["scheduled", "processing", "done", "error", "retry"]


class TEventixTask(BackendModel):
    unique_key: str | None = None
    eta: datetime.datetime | None = Field(default_factory=utcnow)
    scheduled: datetime.datetime | None = Field(default_factory=utcnow)
    status: EventixTaskStatusEnum | None = EventixTaskStatusEnum.scheduled
    priority: int | None = 0  # lower value -> higher priority, because of sorting
    namespace: str | None = "default"
    task: str
    args: tuple | None = Field(default_factory=tuple)
    kwargs: Dict[str, Any] | None = Field(default_factory=dict)

    worker_id: str | None = None
    worker_expires: datetime.datetime | None = None

    retry: bool = True
    max_retries: int | None = None  # None forever, positive value gets decremented until 0
    error_eta_inc: int = 15
    error_eta_max: int = 300
    store_result: bool = True

    result: Any = None

    # Expirations will keep the task in the db.
    # If there is one with None it will keep forever.
    # Otherwise, the expiration is set to the one with the longest duration
    # depending on which ones are applicable.

    error_expires: int | None = None  # keep forever on error
    result_expires: int | None = 604800  # 7 days

    expires: datetime.datetime | None = None
    operator: str | None = "unknown"

    def unique_update_from(self, task: Self):
        self.eta = min([task.eta, self.eta])
        self.priority = min([task.priority, self.priority])
        self.args = task.args
        self.kwargs = task.kwargs

        self.status = task.status  # from retry to scheduled
        self.error_eta_inc: task.error_eta_inc  # reset retry inc

    class Config:
        use_enum_values = True
        validate_assignment = True
        collection_name = "task"
        backend_indexes = [
            SortingIndex("_id", [{"_id": "asc"}]),
            SortingIndex("priority_eta", [{"priority": "asc"}, {"eta": "asc"}]),
            SortingIndex("status_scheduled", [{"status": "desc"}, {"scheduled": "desc"}]),
            AggregationIndex("status_sum", {"status": "_sum"}),
            AggregationIndex("unique_key_sum", {"unique_key": "_sum"}),
            AggregationIndex("unique_key_status_sum", {"unique_key": "_sum", "status": "_sum"}),
            AggregationIndex("task_namespace_sum", {"task": "_sum", "namespace": "_sum"}),
            AggregationIndex("status_namespace_sum", {"status": "_sum", "namespace": "_sum"}),
        ]

    # sort order
    # priority-, eta-

    # 9    0
    # 9    1
    # 9    2
    # 9    3
    # 8    1
    # 8    2
    # 5    4
