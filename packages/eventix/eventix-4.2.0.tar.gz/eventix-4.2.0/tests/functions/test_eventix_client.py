from eventix.functions.eventix_client import EventixClient
from eventix.functions.task import task_post
from eventix.pydantic.task import TEventixTask
from tests.fixtures.backend import cleanup
from tests.fixtures.demo_events import TTransactionStatusChangeEvent


def test_eventix_client_post_event(client_mongodb):
    e1 = TTransactionStatusChangeEvent(
        payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="ANNOUNCED")
    )
    EventixClient.post_event(e1)


def test_ping(client_mongodb):
    assert EventixClient.ping()


def test_EventixClient_get_task_by_unique_key_and_namespace(client_mongodb):
    with cleanup(client_mongodb):
        # with pytest.raises(WebException):
        #     r = EventixClient.get_task_by_unique_key_and_namespace("git_et_net")

        unique_key = "unique_key"
        ns = "gammel"
        task_post(TEventixTask(unique_key=unique_key, task="demotask", priority=1, namespace=ns))

        r = EventixClient.get_task_by_unique_key_and_namespace(unique_key, namespace=ns)
        assert isinstance(r, TEventixTask)
