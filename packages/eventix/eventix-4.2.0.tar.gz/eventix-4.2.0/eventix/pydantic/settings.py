import os
from typing import Literal

from pydantic_settings import BaseSettings

BackendNames = Literal["mongodb", "couchdb"]


class EventixBaseSettings(BaseSettings):
    eventix_url: str
    eventix_delay_tasks: bool = True
    eventix_namespace: str = ""


class EventixClientSettings(EventixBaseSettings):
    pass


class EventixWorkerSettings(EventixBaseSettings):
    eventix_schedule_enabled: bool = False


class EventixServerSettings(EventixBaseSettings):
    eventix_backend: BackendNames = "mongodb"
    eventix_relay_config: str = os.path.abspath(os.path.join(__file__, "../../../relay.yaml"))
    eventix_trigger_config_directory: str = ""
    eventix_url: str = ""
    eventix_api_port: int = 8000
