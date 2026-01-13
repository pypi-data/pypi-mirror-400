import logging
import os

import yaml
from lsrestclient import LsRestClient

from eventix.exceptions import backend_exceptions
from eventix.functions.errors import raise_errors
from eventix.pydantic.relay import RelayModel
from eventix.pydantic.settings import EventixServerSettings
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


class RelayManager(object):
    relays: dict = {}

    @classmethod
    def load_config(cls) -> dict | None:
        path = EventixServerSettings().eventix_relay_config
        log.info(f"trying to load relay config at '{path}'")
        if not os.path.exists(path):
            log.info("no relay config found.")
            return None

        with open(path) as fp:
            d = yaml.load(fp, Loader=yaml.SafeLoader)
        config = d.get("relay", None)
        if config is None:
            raise ValueError(f"key 'relay' not found in relay configuration at '{path}'")
        return config

    @classmethod
    def add_relay(cls, relay: RelayModel):
        log.info(f"Adding relay for namespace... {relay.namespace} -> {relay.url}")
        cls.relays[relay.namespace] = relay

    @classmethod
    def try_relay(cls, task: TEventixTask) -> TEventixTask | None:
        relay = cls.relays.get(task.namespace, None)
        if relay is None:
            return None
        else:
            log.info(f"Relaying {relay.namespace}/{task.task} to {relay.url}")
            client = LsRestClient(relay.url, name=f"relay-{relay.namespace}")
            r = client.post("/task", body=task.model_dump())
            with raise_errors(r, backend_exceptions):
                return TEventixTask.model_validate_json(r.content)


def init_relay():
    config = RelayManager.load_config()
    if config is not None:
        relays = [RelayModel.model_validate(x) for x in config]
        for relay in relays:
            RelayManager.add_relay(relay)
