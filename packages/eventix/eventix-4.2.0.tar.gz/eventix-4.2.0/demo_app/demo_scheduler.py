import os

import dotenv

from eventix.functions.core import task
from eventix.functions.task_scheduler import TaskScheduler


@task()
def mytask(data: str):
    print(data)


if __name__ == "__main__":
    env_local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env.local"))
    print(env_local_path)
    dotenv.load_dotenv(env_local_path)
    print(os.environ.get("EVENTIX_URL"))
    TaskScheduler.config({})
    mytask.delay(data="Pokèmon")
    # mytask.delay(data="gammel")
