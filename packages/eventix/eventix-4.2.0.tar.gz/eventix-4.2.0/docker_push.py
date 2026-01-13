import logging
import subprocess

from docker_build import get_tags, get_versions
from eventix.functions.tools import setup_logging

log = logging.getLogger(__name__)


def push():
    setup_logging()
    versions = get_versions()
    tags = get_tags(versions)

    log.info(f"Pushing Eventix Version {versions[-1]}")

    for tag in tags:
        cmd = ["docker", "push", tag]
        log.info(" ".join(cmd))
        subprocess.run(cmd)


if __name__ == "__main__":
    push()
