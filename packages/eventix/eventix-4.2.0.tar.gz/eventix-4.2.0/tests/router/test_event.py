from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_events import TTransactionStatusChangeEvent


@all_clients()
def test_route_event_post(client, app_client):
    with cleanup(client):
        e = TTransactionStatusChangeEvent(
            payload=TTransactionStatusChangeEvent.Payload(full_tr_number="KL1234", status="ANNOUNCED")
        )
        json = e.model_dump()
        r = app_client.post("/event", body=json)
        print(r)
