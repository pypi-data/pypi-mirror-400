import contextlib
import unittest.mock

from pydantic import BaseModel

from eventix.pydantic.event import TEventixEvent


@contextlib.contextmanager
def pytest_eventix_event_posted(event_name: str | None = None):
    class EventMock(BaseModel):
        event: TEventixEvent | None = None

    ret = EventMock()

    with (
        unittest.mock.patch(
            "eventix.functions.eventix_client.EventixClient.ping",
            return_value=True,
        ),
        unittest.mock.patch(
            "eventix.functions.eventix_client.EventixClient.post_event",
            side_effect=lambda x: [],
        ) as mock_post,
    ):
        yield ret
        if not mock_post.called:
            raise Exception("EventixClient.post_event was not called")

        event_obj: TEventixEvent = mock_post.call_args[0][0]
        event = TEventixEvent.model_validate(event_obj.model_dump())
        if event_name is not None and event.name != event_name:
            raise Exception(f"Event name does not match: {event.name}")
        ret.event = event
