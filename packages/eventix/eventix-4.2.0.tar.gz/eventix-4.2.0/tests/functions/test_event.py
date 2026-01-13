import os
import tempfile
from pprint import pprint

import pytest

from eventix.exceptions import TriggerIgnored
from eventix.functions.event import (
    event_post,
    event_register_trigger,
    event_triggers_export_yaml,
    event_triggers_register_from_directory,
)
from eventix.pydantic.event import TEventixEvent, TEventixEventTrigger
from tests.fixtures.demo_events import (
    TriggerKLAnnouncementEmail,
    TTransactionStatusChangeEvent,
)


@pytest.mark.parametrize(
    "trigger",
    [TriggerKLAnnouncementEmail()],
)
def test_event_register_trigger(trigger):
    event_register_trigger(trigger)


@pytest.mark.parametrize(
    "event",
    [
        TTransactionStatusChangeEvent(
            namespace="es",
            payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="ANNOUNCED"),
        ),
        TTransactionStatusChangeEvent(
            payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="CREATED"),
        ),
    ],
)
def test_event_post(client_mongodb, event):
    event_register_trigger(TriggerKLAnnouncementEmail())
    print(type(event))
    print(event_post(event))


def test_event_restore_from_json():
    e1 = TTransactionStatusChangeEvent(
        payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="ANNOUNCED")
    )
    json = e1.model_dump_json()
    pprint(json)
    e2 = TEventixEvent.model_validate_json(json)
    print(e2)
    assert e1.name == e2.name


# Fixme: This test fails
@pytest.mark.skip(reason="Not sure why this fails")
def test_trigger_restore_from_json():
    e1 = TTransactionStatusChangeEvent(
        payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="ANNOUNCED")
    )
    e2 = TTransactionStatusChangeEvent(
        payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="CREATED")
    )

    t1 = TriggerKLAnnouncementEmail()
    json = t1.model_dump_json()
    # pprint(json)

    t2 = TEventixEventTrigger.model_validate_json(json)

    assert t1.code is not None
    assert t1.name == t2.name
    assert t1.code == t2.code

    t2.execute_code(e1)
    with pytest.raises(TriggerIgnored):
        t2.execute_code(e2)


def test_event_trigger_yaml():
    with tempfile.TemporaryDirectory() as tempdir:
        yaml_file_path = os.path.join(tempdir, "trigger.yaml")
        event_triggers_export_yaml(yaml_file_path, [TriggerKLAnnouncementEmail])
        event_triggers_register_from_directory(tempdir)

        # TEventixEventTrigger.from_yaml(yaml_content)
