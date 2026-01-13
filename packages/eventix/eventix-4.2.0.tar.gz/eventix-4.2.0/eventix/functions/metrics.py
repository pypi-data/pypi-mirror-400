import psutil

from eventix.pydantic.task import EventixTaskStatusEnum


class Metrics(object):
    @classmethod
    def dict(cls):
        return {
            "memory": cls.memory_info(),
            "worker": cls.worker_info(),
            "tasks": cls.task_info(),
        }

    @classmethod
    def memory_info(cls):
        memory_info = psutil.Process().memory_info()
        return dict(rss=memory_info.rss, vms=memory_info.vms, data=memory_info.data)

    @classmethod
    def worker_info(cls):
        return {"number_of_worker": 0}

    @classmethod
    def task_info(cls):
        return {
            EventixTaskStatusEnum.scheduled.value: 0,
            EventixTaskStatusEnum.scheduled.retry: 0,
            EventixTaskStatusEnum.scheduled.error: 0,
            EventixTaskStatusEnum.scheduled.done: 0,
        }


def metrics() -> dict:
    memory_info = psutil.Process().memory_info()
    return {"memory": dict(rss=memory_info.rss, vms=memory_info.vms, data=memory_info.data)}
