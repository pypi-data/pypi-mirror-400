from pydantic import BaseModel

from eventix.pydantic.event import TEventixEvent, TEventixEventTrigger
from eventix.pydantic.task import TEventixTask


class TTransactionStatusChangeEvent(TEventixEvent):
    class Payload(BaseModel):
        full_tr_number: str
        status: str

    payload: Payload


class TriggerKLAnnouncementEmail(TEventixEventTrigger):
    event_name: str = "TTransactionStatusChangeEvent"

    def execute(self, event: TEventixEvent) -> TEventixTask:
        payload = event.payload_dict()
        full_tr_number = payload.get("full_tr_number")
        status = payload.get("status")

        if not (full_tr_number.startswith("KL") and status == "ANNOUNCED"):
            self.ignore()

        task = TEventixTask(
            task="task_send_shipment_announcement_email",
            kwargs=dict(full_tr_number=full_tr_number),
        )
        return task
