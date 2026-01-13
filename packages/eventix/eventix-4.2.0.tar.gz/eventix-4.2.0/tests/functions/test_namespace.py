import logging

from eventix.contexts import namespace_provider
from eventix.functions.namespace import list_namespaces
from tests.fixtures.backend import all_clients, cleanup
from tests.fixtures.demo_tasks import demotask

log = logging.getLogger(__name__)


@all_clients()
def test_list_namespaces_function(client):
    with cleanup(client):
        # create tasks in multiple namespaces
        with namespace_provider("ns1"):
            for i in range(3):
                demotask.delay(value=i)

        with namespace_provider("ns2"):
            for i in range(2):
                demotask.delay(value=i)

        # also create some in the default pytest namespace from conftest
        for i in range(1):
            demotask.delay(value=i)

        namespaces = list_namespaces()
        assert set(["ns1", "ns2", "pytest"]).issubset(set(namespaces))
