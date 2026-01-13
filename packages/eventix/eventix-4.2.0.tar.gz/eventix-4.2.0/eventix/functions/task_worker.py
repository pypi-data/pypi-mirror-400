from __future__ import annotations

import datetime
import importlib
import logging
import os
import time
from traceback import format_tb
from typing import Any, Dict, List

import dotenv
import requests.exceptions
from pydantic_db_backend_common.utils import utcnow
from webexception.webexception import WebException

from eventix.contexts import (
    namespace_provider,
    task_priority_provider,
    task_provider,
    worker_id_context,
    worker_id_provider,
)
from eventix.exceptions import TaskNotRegistered, backend_exceptions
from eventix.functions.core import EventixTaskBase, namespace_context
from eventix.functions.errors import raise_errors
from eventix.functions.eventix_client import EventixClient
from eventix.functions.schedule import schedule_set_next_schedule
from eventix.functions.tools import setup_logging
from eventix.pydantic.schedule import Schedule
from eventix.pydantic.settings import EventixWorkerSettings
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


class TaskWorker(EventixClient):
    _wait_interval = 10
    _tasks = {}
    _schedule: Dict[str, Schedule] = {}

    namespace: str = None
    worker_id: str = "default"
    schedule_enabled: bool = False
    log_level: str = None

    @classmethod
    def config(cls, config: dict):
        # noinspection PyArgumentList
        settings = EventixWorkerSettings()
        cls.set_base_url(settings.eventix_url)

        cls.config_register_tasks(config)

        if "namespace" in config:
            cls.namespace = config["namespace"]

        if settings.eventix_namespace != "":
            cls.namespace = settings.eventix_namespace

        cls.worker_id = cls.get_worker_id()

        cls.schedule_enabled = settings.eventix_schedule_enabled
        cls.config_schedule(config)

    @classmethod
    def get_worker_id(cls):
        worker_id = os.environ.get("EVENTIX_TASK_WORKER_ID", "default")
        if worker_id != "":
            if worker_id == "K8S_HOSTNAME":
                worker_id = os.environ.get("HOSTNAME", "default").split("-")[-1]
        return worker_id

    @classmethod
    def config_register_tasks(cls, config):
        if "register_tasks" in config:
            cls.register_tasks(config["register_tasks"])

    @classmethod
    def config_schedule(cls, config):
        if "schedule" in config:
            for entry in config["schedule"]:
                s = Schedule.model_validate(entry)
                if s.task not in cls._tasks:
                    raise TaskNotRegistered(s.task)

                schedule_set_next_schedule(s)
                cls._schedule[s.uid] = s
                log.info(f"Scheduled '{s.name}' on '{s.schedule}'")

    @classmethod
    def check_scheduled_tasks(cls):
        log.debug("Check scheduled tasks...")
        for s in cls._schedule.values():
            if s.next_schedule <= utcnow():
                # trigger task
                # update schedule
                log.debug(f"triggering scheduled task '{s.name}'")
                cls._tasks[s.task].delay(*s.args, _priority=s.priority, **s.kwargs)
                schedule_set_next_schedule(s)

    @classmethod
    def register_tasks(cls, paths=List[str]):
        log.info("registering tasks...")
        # noinspection PyTypeChecker
        for path in paths:
            try:
                imported_module = importlib.import_module(path)
                for f in filter(
                    lambda x: isinstance(x, EventixTaskBase),
                    [getattr(imported_module, x) for x in dir(imported_module)],
                ):
                    log.info(f"registered '{f.func_name}' from {path}")
                    cls._tasks[f.func_name] = f
            except ImportError as e:
                print(e)

    # with raise_errors(r):
    #     return TaskModel.parse_raw(r.content)

    @classmethod
    def task_next_scheduled(cls) -> TEventixTask | None:
        with namespace_context() as namespace:
            with worker_id_context() as worker_id:
                params = dict(worker_id=worker_id, namespace=namespace)
                r = cls.interface.get("/tasks/next_scheduled", params=params)
                try:
                    with raise_errors(r, backend_exceptions):
                        if r.status_code == 200:
                            tm = TEventixTask.model_validate_json(r.content)
                            return tm
                        if r.status_code == 204:
                            return None
                except Exception as e:
                    log.error("Upstream server error:")
                    log.exception(str(e))
                    return None

    @classmethod
    def listen(cls, endless=True, schedule_enabled: bool = False):
        log.info(f"Schedule {'enabled' if schedule_enabled else 'disabled'}")
        log.info("Start listening...")
        while True:
            try:
                if schedule_enabled:
                    cls.check_scheduled_tasks()
                log.debug("Looking for tasks...")
                t = cls.task_next_scheduled()
                if t is not None:
                    cls.execute_task(t)
                else:
                    log.debug(f"Nothing to do... waiting {cls._wait_interval}s")
                    if not endless:
                        return
                    time.sleep(cls._wait_interval)
            except requests.exceptions.ConnectionError:
                log.error(f"Upstream Eventix server {cls.interface.base_url} not reachable.")
                time.sleep(5)

    @classmethod
    def execute_task(cls, task: TEventixTask):
        try:
            log.debug(f"Executing task: {task.task} uid: {task.uid} ...")

            if task.task not in cls._tasks:
                raise TaskNotRegistered(task=task.task)  # Task not registered in worker

            f = cls._tasks[task.task]
            with task_provider(task):
                with task_priority_provider(task.priority):
                    r = f.run(*task.args, **task.kwargs)
            cls.task_set_result(task, r)

        except TaskNotRegistered as e:
            log.error(f"Error executing task: {task.task} uid: {task.uid}")
            log.exception(e)
            cls.task_set_error(task, TaskNotRegistered(task=task.task))

        except Exception as e:
            log.exception(e)
            cls.task_set_error(task, e)

        finally:
            cls.task_write_back(task)

    @classmethod
    def task_write_back(cls, task: TEventixTask) -> TEventixTask | None:
        try:
            if task.expires is not None and task.expires < utcnow():  # gammel
                # if task is already expired, delete it instead of updating
                cls.interface.delete(f"/task/{task.uid}")
                return None
            else:
                # task not yet expired.... update
                # TODO: use Pydantic v2 json
                r = cls.interface.put(f"/task/{task.uid}", body=task.model_dump())

            with raise_errors(r, backend_exceptions):
                if r.status_code == 200:
                    tm = TEventixTask.model_validate_json(r.content)
                    return tm

        except Exception as e:
            log.error("Exception raised when calling eventix")
            log.exception(e)
            log.error("Exception used this task info")
            log.error(task.model_dump_json())

        return None

    @classmethod
    def load_env(cls):
        dotenv.load_dotenv(".env.local")

    def __init__(self, config: dict) -> None:
        self.load_env()
        self.init_logging()
        self.config(config)

    def init_logging(self):
        worker_id = self.get_worker_id()
        self.log_level = os.environ.get("EVENTIX_WORKER_LOG_LEVEL", "INFO")
        urllib3_logger = logging.getLogger("urllib3.connectionpool")
        urllib3_logger.setLevel(logging.INFO)
        setup_logging(level=self.log_level.upper(), module=False, prefix=f"[WORKER-{worker_id}]")

    def start(self, endless: bool | None = True):
        log.info(f"Using namespace: {self.namespace}")
        with namespace_provider(self.namespace):
            with worker_id_provider(self.worker_id):
                self.listen(endless, self.schedule_enabled)

    @staticmethod
    def task_set_error(task: TEventixTask, error: Any):
        if isinstance(error, WebException):
            task.result = error.dict()
        elif isinstance(error, Exception):
            task.result = dict(
                error_class=error.__class__.__name__,
                error_message=str(error),
                error_status_code=500,
                error_traceback=format_tb(error.__traceback__),
                error_payload={},
            )
        else:
            task.result = error

        if task.retry and (task.max_retries is None or task.max_retries != 0):
            task.status = "retry"
            if task.max_retries is not None:
                task.max_retries -= 1  # decrease max_retries until it reaches zero.

            task.eta = utcnow() + datetime.timedelta(seconds=task.error_eta_inc)
            task.error_eta_inc = min([task.error_eta_inc * 2, task.error_eta_max])

            task.worker_id = None

        else:
            task.status = "error"
            if task.error_expires is not None:
                task.expires = utcnow() + datetime.timedelta(seconds=task.error_expires)

        task.worker_expires = None  # removes worker_expires for cleanup prevention

    @staticmethod
    def task_set_result(task: TEventixTask, result: Any):
        task.status = "done"
        if task.store_result:
            task.result = result
            if task.result_expires is not None:
                task.expires = utcnow() + datetime.timedelta(seconds=task.result_expires)
        else:
            task.expires = utcnow()

        task.worker_expires = None  # removes worker_expires for cleanup prevention
