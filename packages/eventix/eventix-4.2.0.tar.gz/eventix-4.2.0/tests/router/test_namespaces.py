from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_tasks import demotask
from eventix.contexts import namespace_provider


@all_clients()
def test_router_namespaces_get(client, app_client):
    with cleanup(client):
        # seed tasks across namespaces
        with namespace_provider("alpha"):
            for i in range(2):
                demotask.delay(value=i)

        with namespace_provider("beta"):
            for i in range(1):
                demotask.delay(value=i)

        # default pytest namespace from conftest will be used here
        demotask.delay(value=99)

        r = app_client.get("/namespaces")
        assert r.status_code == 200
        payload = r.json()
        assert "namespaces" in payload
        # At least these should be present; others (like 'default') may appear depending on env
        for ns in ["alpha", "beta", "pytest"]:
            assert ns in payload["namespaces"], payload
