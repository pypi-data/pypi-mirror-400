import logging
from typing import List

from pydantic_db_backend.backend import Backend
from pydantic_db_backend_common.pydantic import PaginationParameterModel

from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


def list_namespaces() -> List[str]:
    """Return a distinct, sorted list of namespaces for existing tasks.

    This performs a simple scan limited by backend pagination defaults which is
    sufficient for current test scenarios. It filters out None values.
    """
    client = Backend.client()
    # Fetch a reasonable amount; tests populate modest volumes.
    result = client.get_instances(TEventixTask, PaginationParameterModel(limit=10_000))
    namespaces = {t.namespace for t in result.data if getattr(t, "namespace", None)}
    return sorted(list(namespaces))
