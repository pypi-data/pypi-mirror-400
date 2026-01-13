import datetime
import inspect
import logging
import textwrap
from typing import Any, Callable, Literal, Type

from lsidentity.contexts import LsiAccountId
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic_db_backend_common.pydantic import BackendModel
from pydantic_db_backend_common.utils import utcnow

from eventix.exceptions import TriggerIgnored
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


class TEventPayload(BaseModel):
    pass


class TEventixEvent(BackendModel):
    namespace: str | None = "default"
    timestamp: datetime.datetime | None = Field(default_factory=utcnow)
    priority: int | None = 0
    payload: dict | None = Field(default_factory=dict)
    name: str | None = None
    operator: str | None = "unknown"

    def __init__(self, **data: Any) -> None:
        if "name" not in data:
            data["name"] = self.__class__.__name__
        if "operator" not in data:
            with LsiAccountId() as operator:
                data["operator"] = operator

        super().__init__(**data)

    def payload_object(self, model: Type[BaseModel]) -> BaseModel:
        return model(**self.payload) if isinstance(self.payload, dict) else self.payload

    def payload_dict(self):
        p = self.payload
        ret = p.model_dump() if isinstance(p, BaseModel) else p
        return ret


TEventixEventTriggerType = Literal["default"]
TEventTriggerExecuteFunction = Callable[[TEventixEvent], TEventixTask]


class TEventixEventTrigger(BackendModel):
    event_name: str
    trigger_type: TEventixEventTriggerType | None = "default"
    namespace: str | None = "default"
    name: str | None = None
    code: str | None = None

    def __init__(self, **data: Any) -> None:
        if "name" not in data:
            data["name"] = self.__class__.__name__
        if "code" not in data:
            data["code"] = self.get_code()

        super().__init__(**data)

    def get_code(self):
        return textwrap.dedent(inspect.getsource(self.execute))

    def ignore(self):
        raise TriggerIgnored(self.name)

    def execute_code(self, event: TEventixEvent):
        code = self.code
        code += "\n\ntask = execute(self, event)"
        # f = compile(code, "<string>", "exec")
        # exec(f)
        exec(code)
        ret: TEventixTask = locals()["task"]
        return ret

    def execute(self, event: TEventixEvent) -> TEventixTask:
        raise NotImplementedError
