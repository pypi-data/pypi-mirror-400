import importlib
from pathlib import Path

import toml


def get_version():
    # noinspection PyBroadException
    try:
        path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        pyproject = toml.loads(open(str(path)).read())
        v = pyproject["tool"]["poetry"]["version"]

    except Exception:
        # noinspection PyBroadException
        try:
            # noinspection PyUnresolvedReferences
            v = importlib.metadata.version("eventix")
        except Exception:
            v = "0.0.0"
    return v


__version__ = get_version()
