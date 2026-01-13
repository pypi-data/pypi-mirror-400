import logging
import os
import traceback
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from pydantic_db_backend.backends.mongodb import MongoDbBackend
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp
from webexception.webexception import WebException

from eventix.pydantic.settings import EventixServerSettings

log = logging.getLogger(__name__)

BACKENDS = {"mongodb": MongoDbBackend}


def init_backend():
    if os.environ.get("APP_CLIENT", "false") != "true":
        settings = EventixServerSettings()
        backend_name = settings.eventix_backend.lower()
        log.info(f"Using {backend_name} backend")
        backend = BACKENDS[backend_name]
        client = backend()
        log.info(client.settings)


# class BackendMiddleware(BaseHTTPMiddleware):
#     def __init__(
#         self,
#         app: ASGIApp,
#         dispatch: DispatchFunction | None = None,
#     ) -> None:
#         super().__init__(app, dispatch)
#
#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
#         response = await call_next(request)
#         return response


class ErrorMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
    ) -> None:
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
        except Exception as e:
            return await self.make_exception_response(e)
        return response

    @staticmethod
    async def make_exception_detail(e: Exception) -> Dict:
        tb = traceback.format_exc()
        ret = dict(error_class=e.__class__.__name__, error_message=str(e), error_traceback=tb)
        return ret

    async def make_exception_response(self, e: Exception, headers: Optional[Dict[str, Any]] = None) -> JSONResponse:
        status_code = None
        if isinstance(e, HTTPException):
            status_code = e.status_code
            content = dict(detail=e.detail)

        elif isinstance(e, WebException):
            status_code = e.status_code
            if status_code == 204:
                content = None
            else:
                content = e.dict()
        else:
            if status_code is None:  # no status code found yet
                status_code = 500
            content = dict(detail=await self.make_exception_detail(e))

        if status_code >= 500:
            log.exception(e, stacklevel=2)

        if isinstance(content, dict):
            response = JSONResponse(status_code=status_code, content=content, headers=headers)
        else:
            response = Response(status_code=status_code, headers=headers, content=content)
        return response
