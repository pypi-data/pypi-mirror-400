import contextlib
import logging
from typing import List, Type

import pydash

from eventix.exceptions import EventixHTTPException

log = logging.getLogger(__name__)


@contextlib.contextmanager
def raise_errors(r, exceptions: List[Type[Exception]]):
    exceptions_by_class = {e.__name__: e for e in exceptions}
    if r.status_code < 399:
        yield r
    else:
        try:
            json = r.json()
            detail = pydash.get(json, "detail", json)
            error_class = pydash.get(detail, "error_class")
            payload = pydash.get(detail, "error_payload", {})

            if error_class in exceptions_by_class:
                e = exceptions_by_class[error_class](**payload)
                raise e
            # backend errors
            raise EventixHTTPException(status_code=r.status_code, detail=detail)

        except Exception:
            log.error(r.content)
            raise EventixHTTPException(status_code=r.status_code, detail=r.content)
