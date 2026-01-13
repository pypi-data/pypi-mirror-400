import logging
import os
from collections import defaultdict
from typing import Dict, List, Type

import pydash
import yaml

from eventix.functions.task import task_post
from eventix.pydantic.settings import EventixServerSettings


def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

from eventix.exceptions import TriggerIgnored
from eventix.functions.log import log_prefix, set_log_prefix
from eventix.pydantic.event import TEventixEvent, TEventixEventTrigger
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


class EventManager(object):
    _triggers: Dict[str, Dict[str, TEventixEventTrigger]] = defaultdict(lambda: dict())

    @classmethod
    def post_event(cls, event: TEventixEvent) -> List[TEventixTask]:
        with set_log_prefix(f"[{event.name}]"):
            log.info(log_prefix("Event posted."))
            triggers: Dict[str, TEventixEventTrigger] = cls._triggers.get(event.name, {})
            ret = []
            for trigger in triggers.values():
                with set_log_prefix(f"[{trigger.name}]"):
                    try:
                        task = trigger.execute_code(event)
                        if task.namespace is None or task.namespace == "default":
                            task.namespace = event.namespace
                        task.priority = event.priority
                        task.operator = event.operator

                        updated_task = task_post(task)
                        log.info(log_prefix(f"Trigger executed. Task {updated_task.uid} scheduled."))
                        ret.append(updated_task)

                    except TriggerIgnored:
                        log.info(log_prefix("Trigger ignored:"))

                    except Exception as e:
                        log.error(log_prefix("Trigger failed with error:"))
                        log.error(log_prefix(str(e)))
                        log.exception(e)
        return ret

    @classmethod
    def register_trigger(cls, trigger: TEventixEventTrigger):
        log.info(f'[{trigger.name}] Registered for event "{trigger.event_name}"')
        cls._triggers[trigger.event_name][trigger.name] = trigger


def event_register_trigger(trigger: TEventixEventTrigger):
    return EventManager.register_trigger(trigger)


def event_post(event: TEventixEvent) -> List[TEventixTask]:
    return EventManager.post_event(event)


def event_trigger_yaml_data(trigger: Type[TEventixEventTrigger]) -> dict:
    d = pydash.omit(
        trigger().model_dump(),
        ["created_time", "uid", "updated_time"],
    )
    return d


def event_triggers_yaml_data(triggers: List[Type[TEventixEventTrigger]]) -> dict:
    trigger_data = {
        d["name"]: pydash.omit(d, "name") for d in [event_trigger_yaml_data(trigger) for trigger in triggers]
    }
    return trigger_data


def event_triggers_export_yaml(out_path: str, triggers: List[Type[TEventixEventTrigger]]):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fp:
        content = dict(triggers=event_triggers_yaml_data(triggers))
        fp.write(yaml.dump(content, indent=2))
    log.info(f"Exported trigger config to '{out_path}'")


def event_triggers_register_from_directory(directory: str):
    for file in os.listdir(directory):
        if file.endswith(".yaml"):
            with open(os.path.join(directory, file)) as fp:
                data = yaml.load(fp, Loader=yaml.SafeLoader)
            triggers = data.get("triggers", {})
            for name, trigger_data in triggers.items():
                trigger_data["name"] = name
                trigger = TEventixEventTrigger.model_validate(trigger_data)
                event_register_trigger(trigger)


def init_triggers():
    settings = EventixServerSettings()
    path = settings.eventix_trigger_config_directory
    if path == "":
        log.info("No trigger config directory specified.")
        return

    log.info(f"Trying to load trigger configs from '{path}'")
    event_triggers_register_from_directory(path)
