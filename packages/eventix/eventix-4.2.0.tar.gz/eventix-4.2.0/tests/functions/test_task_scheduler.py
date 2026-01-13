from pprint import pprint

from eventix.functions.task_scheduler import TaskScheduler
from eventix.pydantic.task import TEventixTask
from tests.fixtures.backend import all_clients, cleanup


@all_clients()
def test_schedule(client):
    with cleanup(client):
        tm = TEventixTask(task="demotask", priority=1, kwargs={"data": "Pokémon"})
        try:
            TaskScheduler.schedule(tm)
        except Exception as e:
            pprint(e)
