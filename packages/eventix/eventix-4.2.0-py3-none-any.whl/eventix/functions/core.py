import datetime
import functools
import logging
from inspect import isclass, signature
from types import GenericAlias

# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import Any, Callable, Dict, _BaseGenericAlias, get_args

from lsidentity.contexts import LsiAccountId, LsiAccountIdProvider
from pydantic import BaseModel
from pydantic_db_backend_common.utils import str_to_datetime_if_parseable

from eventix.contexts import (
    delay_tasks_context,
    namespace_context,
    task_priority_context,
)
from eventix.functions.task_scheduler import TaskScheduler
from eventix.pydantic.task import TEventixTask

log = logging.getLogger(__name__)


class EventixTaskBase(object):
    pass


def task(
    store_result: bool = True,
    unique_key_generator: Callable = None,
    retry: bool = True,
    error_eta_max: int | None = None,
    max_retries: int | None = None,
    error_expires: int | None = None,
    result_expires: int | None = 604800,
    error_eta_inc: int | None = 15,
    default_priority: int = 0,
):
    # parameters suggested:
    #
    # store_result: bool , whether to store or not to store results
    # unique_uid: ....  having a unique id, which leads to update the task if it is rescheduled.

    # retry: bool, whether to retry failed tasks
    # max_retry: int, maximum retries default 5 ... each retry doubles the time to wait, starting with 30 sec

    is_unique = unique_key_generator is not None

    def inner(f):
        class EventixTask(EventixTaskBase):
            def __init__(self):
                self.func = f
                self.func_name = f.__name__
                self.arg_spec = list(signature(f).parameters.values())
                self.arg_spec_args = [arg.annotation for arg in self.arg_spec]
                self.arg_spec_kwargs = {arg.name: arg.annotation for arg in self.arg_spec}
                assert True

            @staticmethod
            def get_arg_from_cls(cls, arg) -> Any:
                # commented code is a first start to restructure

                # if isinstance(arg, dict):
                #     if isinstance(cls, _BaseGenericAlias):
                #         cls = cls.__origin__
                #
                # match cls:
                #     case datetime.datetime:
                #         if isinstance(arg, str):
                #             arg = str_to_datetime_if_parseable(arg)
                #     case BaseModel:
                #         if isinstance(arg, dict):
                #             arg = cls.parse_obj(arg)

                match cls:
                    case datetime.datetime:
                        # next line if is for calling task with run. in this case the arg is already a datetime
                        if isinstance(arg, str):
                            arg = str_to_datetime_if_parseable(arg)
                    case _:
                        if isinstance(arg, dict):
                            if isinstance(cls, _BaseGenericAlias):
                                cls = cls.__origin__
                            if issubclass(cls, BaseModel):
                                arg = cls.model_validate(arg)
                        if isinstance(arg, list):
                            if isinstance(cls, GenericAlias):
                                cls_tuple = get_args(cls)
                                if len(cls_tuple) == 1:
                                    cls = cls_tuple[0]
                            if isclass(cls) and issubclass(cls, BaseModel):
                                arg = [cls.model_validate(arg) for arg in arg]
                return arg

            def restore_original_types(self, args, kwargs) -> tuple[list[Any], Dict[str, Any]]:
                new_args = []
                for i, arg in enumerate(args):
                    cls = self.arg_spec_args[i]
                    arg = self.get_arg_from_cls(cls=cls, arg=arg)
                    new_args.append(arg)
                new_kwargs = {}
                for kw, arg in kwargs.items():
                    cls = self.arg_spec_kwargs[kw]
                    new_kwargs[kw] = self.get_arg_from_cls(cls=cls, arg=arg)
                return new_args, new_kwargs

            @functools.wraps(f)
            def delay(
                self,
                *args,
                _priority: int | None = None,
                _eta: datetime.datetime | None = None,
                _operator: str | None = None,
                **kwargs,
            ) -> TEventixTask:
                if _priority is None:
                    with task_priority_context() as task_priority:
                        _priority = task_priority

                if _priority == 0:
                    _priority = default_priority

                if _operator is None:
                    with LsiAccountId() as op:
                        _operator = op

                # priority has to be negated, needed for fixing ascending sort order
                tm = self.make_task_model(args, kwargs, priority=_priority * -1, eta=_eta, operator=_operator)
                with delay_tasks_context() as delay:
                    if delay:
                        tm = TaskScheduler.schedule(tm)
                    else:
                        self.run(*args, **kwargs, _operator=_operator)

                # IDEA: It could be possible to run worker execute with generated task during tests
                return tm

            @functools.wraps(f)
            def run(self, *args, _operator: str | None = None, **kwargs):
                if _operator is None:
                    with LsiAccountId() as op:
                        _operator = op

                with LsiAccountIdProvider(_operator):
                    args, kwargs = self.restore_original_types(args, kwargs)
                    return self.func(*args, **kwargs)

            def make_task_model(self, args, kwargs, priority, eta, operator) -> TEventixTask:
                with namespace_context() as namespace:
                    params = dict(
                        task=self.func_name,
                        args=args,
                        kwargs=kwargs,
                        priority=priority,
                        operator=operator,
                        store_result=store_result,
                        retry=retry,
                        max_retries=max_retries,
                        error_expires=error_expires,
                        result_expires=result_expires,
                        namespace=(kwargs["namespace"] if "namespace" in kwargs else namespace),
                    )
                    if error_eta_max is not None:
                        params["error_eta_max"] = error_eta_max
                    if error_eta_inc is not None:
                        params["error_eta_inc"] = error_eta_inc

                    if eta is not None:
                        if eta.tzinfo is None:
                            eta.replace(tzinfo=datetime.timezone.utc)
                        params["eta"] = eta

                    if is_unique:
                        unique_key = unique_key_generator(*args, **kwargs)
                        params |= dict(unique_key=unique_key)

                return TEventixTask.model_validate(params)

        return EventixTask()

    return inner
