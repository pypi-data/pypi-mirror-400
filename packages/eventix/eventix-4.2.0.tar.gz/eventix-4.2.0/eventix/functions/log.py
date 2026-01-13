import logging
from contextlib import contextmanager
from contextvars import ContextVar

log = logging.getLogger(__name__)

log_prefix_context_var = ContextVar("log_prefix", default="")


@contextmanager
def set_log_prefix(prefix: str | None = ""):
    existing_prefix = log_prefix_context_var.get()
    token = log_prefix_context_var.set(f"{existing_prefix}{prefix}")
    yield prefix
    log_prefix_context_var.reset(token)


def log_prefix(msg: str) -> str:
    prefix = log_prefix_context_var.get()
    return f"{prefix} {msg}"
