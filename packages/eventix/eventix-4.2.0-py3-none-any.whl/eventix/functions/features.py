import functools
from typing import List

from pydantic_db_backend.backend import Backend, has_backend_features

from eventix.exceptions import BackendFeaturesMissing


def backend_features(features: List[str]):
    """
    Raises an error if decorated function is called with an active backend
    not supporting all!!! requested features.

    :param features: list with requested features.
    """

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            backend = Backend.client()
            if not has_backend_features(backend, features):
                raise BackendFeaturesMissing(backend.__class__.__name__, features)
            else:
                return func(*args, **kwargs)

        return wrapper

    return inner
