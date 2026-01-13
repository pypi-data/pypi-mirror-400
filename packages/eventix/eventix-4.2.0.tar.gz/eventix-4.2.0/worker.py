from eventix.functions.fastapi import init_backend
from eventix.functions.task_worker import TaskWorker
from eventixconfig import config

worker = TaskWorker(config)

if __name__ == "__main__":
    init_backend()
    worker.start(endless=True)
