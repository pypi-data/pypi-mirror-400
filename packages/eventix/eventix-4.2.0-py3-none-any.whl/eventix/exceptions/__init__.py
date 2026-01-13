from typing import Any, Dict, List, Optional

from pydantic_db_backend_common.exceptions import (
    AlreadyExists,
    NotFound,
    RevisionConflict,
)
from webexception.webexception import WebException


class TaskNotUnique(WebException):
    status_code = 409

    def __init__(self, uid: str) -> None:
        super().__init__(
            f"Task with uid '{uid}' already exists and task unique is not activated for overwriting.",
            uid=uid,
        )


class NoTaskFound(WebException):
    status_code = 204

    def __init__(self, namespace: str) -> None:
        super().__init__(f"No task for namespace {namespace}", namespace=namespace)


class NoTaskFoundForUniqueKey(WebException):
    status_code = 404

    def __init__(self, unique_key: str, stati: str = None) -> None:
        super().__init__(
            f"No task for unique_key {unique_key} and stati {stati} found",
        )
        self.unique_id = unique_key


class TaskUniqueKeyNotUnique(WebException):
    status_code = 409

    def __init__(self, unique_key: str) -> None:
        super().__init__(
            f"Task with unique_key {unique_key} not unique",
        )
        self.unique_id = unique_key


class TaskNotRegistered(WebException):
    status_code = 404

    def __init__(self, task: str) -> None:
        super().__init__(f"Task '{task}' not registered.", task=task)


class EventixHTTPException(WebException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BackendFeaturesMissing(WebException):
    status_code = 501

    def __init__(self, backend_name: str, features: List[str]) -> None:
        super().__init__(f"Backend {backend_name} does not support all features {features}", features)


class WrongTaskStatus(WebException):
    status_code = 422

    def __init__(self, uid: str, status: str) -> None:
        super().__init__(f"Task {uid} has wrong status: '{status}'", uid=uid, status=status)


class TriggerIgnored(WebException):
    status_code = 200

    def __init__(self, name: str) -> None:
        super().__init__(f"[{name}] Trigger ignored.")


backend_exceptions = [AlreadyExists, NotFound, RevisionConflict]
