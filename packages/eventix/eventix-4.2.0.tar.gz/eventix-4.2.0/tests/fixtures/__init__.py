import contextlib
import os

import pytest


@pytest.fixture
def set_env():
    @contextlib.contextmanager
    def inner(**environ):
        old_environ = dict(os.environ)
        os.environ.update(environ)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_environ)

    return inner
