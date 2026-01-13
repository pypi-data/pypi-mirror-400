import logging
from typing import List

from fastapi import APIRouter

from eventix.functions.event import event_post
from eventix.pydantic.event import TEventixEvent
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)

router = APIRouter(tags=["event"])


@router.post("/event")
async def route_event_post(event: TEventixEvent) -> List[TEventixTask]:
    return event_post(event)
