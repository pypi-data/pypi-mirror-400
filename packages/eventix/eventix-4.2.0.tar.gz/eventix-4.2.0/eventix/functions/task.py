import datetime
import logging
from typing import List, Type

from pydantic_db_backend.backend import Backend
from pydantic_db_backend.contexts.custom_aggregation import custom_aggregation_provider
from pydantic_db_backend.contexts.pagination_parameter import (
    pagination_parameter_provider,
)
from pydantic_db_backend.pagination import pagination_parameter_resolve
from pydantic_db_backend_common.exceptions import RevisionConflict
from pydantic_db_backend_common.pydantic import (
    CustomAggregationModel,
    FindResultModel,
    PaginationParameterModel,
)
from pydantic_db_backend_common.utils import Undefined, utcnow

from eventix.exceptions import NoTaskFoundForUniqueKey, TaskUniqueKeyNotUnique, WrongTaskStatus
from eventix.functions.features import backend_features
from eventix.functions.relay import RelayManager
from eventix.pydantic.task import EventixTaskStatusEnum, TEventixTask

# post
# already exists
# still scheduled -> update
# not scheduled --> post new.
# scheduled -> update
#
#   on update:
#       get task
#       scheck scheduled, if not post
#       update task
#
#       if worker grabs , version should conflict
#       on conflict : try again

log = logging.getLogger(__name__)


def task_post(task: TEventixTask) -> TEventixTask:
    # try to relay
    r = RelayManager.try_relay(task)
    if r is not None:
        return r  # relay successful

    # no relay

    is_unique = task.unique_key is not None
    client = Backend.client()

    if not is_unique:
        # not unique , just try to save. If exists, raise error
        # noinspection PyTypeChecker
        return client.post_instance(task)

    # has unique_key

    while True:
        # noinspection PyTypeChecker
        with pagination_parameter_provider(
            PaginationParameterModel(filter={"unique_key": task.unique_key, "namespace": task.namespace})
        ):
            existing_tasks = client.get_instances(TEventixTask)
        next_scheduled_task = next(
            filter(
                lambda t: t.status in (EventixTaskStatusEnum.scheduled, EventixTaskStatusEnum.retry),
                existing_tasks.data,
            ),
            None,
        )

        if next_scheduled_task is None:
            # no existing ones that are only scheduled, we have to post
            # noinspection PyTypeChecker
            return client.post_instance(task)

        #   update:
        #       get task
        #       scheck scheduled, if not post
        #       update task
        #
        #       if worker grabs , version should conflict
        #       on conflict: try again

        next_scheduled_task.unique_update_from(task)
        try:
            updated_task = client.put_instance(next_scheduled_task)
            # noinspection PyTypeChecker
            log.debug(f"updated task {updated_task.uid}")
            # noinspection PyTypeChecker
            return updated_task  # update worked
        except RevisionConflict:
            continue  # try again.


def task_clean_expired_workers():
    client = Backend.client()
    with pagination_parameter_provider(
        PaginationParameterModel(
            skip=0,
            limit=1,
            filter=dict(worker_expires={"$ne": None, "$lt": utcnow()}),
            sort="priority,eta",
        )
    ):
        while True:
            existing_task: TEventixTask | None = next(iter(client.get_instances(model=TEventixTask).data), None)

            # repeat until we were able to take something or nothing is left.
            if existing_task is None:
                break

            existing_task.status = EventixTaskStatusEnum.scheduled
            existing_task.worker_id = None
            existing_task.worker_expires = None

            try:
                client.put_instance(existing_task)
                log.info(f"Released task {existing_task.uid}")
                # noinspection PyTypeChecker
            except RevisionConflict:
                continue


def task_clean_expired_tasks():
    client = Backend.client()
    pagination_parameter = PaginationParameterModel(
        skip=0, limit=100, filter=dict(expires={"$ne": None, "$lt": utcnow()})
    )

    while True:
        existing_uids = client.get_uids(TEventixTask, pagination_parameter)

        # repeat until we were able to take something or nothing is left.
        if len(existing_uids.data) == 0:
            break

        for uid in existing_uids.data:
            client.delete_uid(TEventixTask, uid)
            log.info(f"Removed expired task {uid}")


def task_next_scheduled(worker_id: str, namespace: str, expires: int = 300) -> TEventixTask | None:
    log.debug(f"[{worker_id}] Worker getting next scheduled task...")
    client = Backend.client()

    # looking up possible tasks in right order
    # take first one
    # try to set worker_id and expiration

    eta = utcnow()  # eta has to be now or in the past

    pagination_parameter = PaginationParameterModel(
        filter=(
            dict(
                namespace=namespace,  # namespace has to match
                worker_id=None,  # no worker assigned
                status={"$in": [EventixTaskStatusEnum.scheduled, EventixTaskStatusEnum.retry]},
                eta={"$lte": eta},
            )
        ),
        limit=1,
        sort="priority,eta",
    )

    while True:  # repeat until we were able to take something or nothing is left.
        existing_task = next(iter(client.get_instances(TEventixTask, pagination_parameter).data), None)

        if existing_task is None:
            return None  # no task left

        existing_task.status = "processing"
        existing_task.worker_id = worker_id
        existing_task.worker_expires = utcnow() + datetime.timedelta(seconds=expires)
        log.debug(f"task_next_scheduled: existing task revision: {existing_task.revision}")
        try:
            # noinspection PyTypeChecker
            t: TEventixTask = client.put_instance(existing_task)
            return t
        except RevisionConflict:
            continue


def tasks_by_status(
    status: EventixTaskStatusEnum | None = None,
    namespace: str | None = None,
    pagination_parameter: PaginationParameterModel | None | Type[Undefined] = Undefined,
) -> FindResultModel:
    client = Backend.client()
    pagination_parameter = pagination_parameter_resolve(pagination_parameter)

    filter = {}
    if status is not None:
        filter |= {"status": status}

    if namespace is not None:
        filter |= {"namespace": namespace}

    if len(filter) != 0:
        pagination_parameter.filter = (
            filter if pagination_parameter.filter is None else pagination_parameter.filter | filter
        )

    tasks = client.get_instances(TEventixTask, pagination_parameter)
    return tasks


@backend_features(features=["find_extend_pipeline"])
def tasks_by_task(
    task: str = None,
    namespace: str | None = None,
    pagination_parameter: PaginationParameterModel | None | Type[Undefined] = Undefined,
) -> FindResultModel:
    client = Backend.client()
    pagination_parameter = pagination_parameter_resolve(pagination_parameter)

    filter = {}
    filter |= {"task": task}

    if namespace is not None:
        filter |= {"namespace": namespace}

    pagination_parameter.sort = "status_id,-eta"

    if len(filter) != 0:
        pagination_parameter.filter = (
            filter if pagination_parameter.filter is None else pagination_parameter.filter | filter
        )

    with custom_aggregation_provider(
        CustomAggregationModel(
            before_tail=[
                {
                    "$addFields": {
                        "status_id": {
                            "$indexOfArray": [
                                [
                                    EventixTaskStatusEnum.scheduled,
                                    EventixTaskStatusEnum.processing,
                                    EventixTaskStatusEnum.retry,
                                    EventixTaskStatusEnum.error,
                                    EventixTaskStatusEnum.done,
                                ],
                                "$status",
                            ]
                        }
                    }
                }
            ]
        )
    ):
        tasks = client.get_instances(TEventixTask, pagination_parameter)
    return tasks


def task_by_unique_key(
    unique_key: str, namespace: str = None, stati: List[EventixTaskStatusEnum] = None
) -> TEventixTask:
    filter_params = {"unique_key": unique_key}
    if namespace is not None:
        filter_params["namespace"] = namespace

    if stati is None:
        stati = [EventixTaskStatusEnum.scheduled.value, EventixTaskStatusEnum.retry.value]

    existing_tasks = Backend.client().get_instances(
        TEventixTask,
        PaginationParameterModel(limit=10, filter=filter_params),
    )

    filtered = list(filter(lambda t: t.status in stati, existing_tasks.data))
    if len(filtered) == 0:
        raise NoTaskFoundForUniqueKey(unique_key=unique_key)

    if len(filtered) > 1 and namespace is None:
        raise TaskUniqueKeyNotUnique(unique_key)
    return filtered[0]


def task_reschedule(uid: str, eta: datetime.datetime | None = None) -> TEventixTask:
    # noinspection PyTypeChecker
    t: TEventixTask = Backend.client().get_instance(TEventixTask, uid)

    if t.status not in ["error", "retry"]:
        raise WrongTaskStatus(uid, t.status)

    if eta is None:
        eta = utcnow()

    t.status = EventixTaskStatusEnum.scheduled
    t.eta = eta
    t.worker_id = None
    Backend.client().put_instance(t)
    return t


def tasks_dump(
    pagination_parameter: PaginationParameterModel | None | Type[Undefined] = Undefined,
) -> FindResultModel:
    client = Backend.client()
    pagination_parameter = pagination_parameter_resolve(pagination_parameter)
    pagination_parameter.sort = "_id"

    tasks = client.get_instances(TEventixTask, pagination_parameter)
    return tasks
