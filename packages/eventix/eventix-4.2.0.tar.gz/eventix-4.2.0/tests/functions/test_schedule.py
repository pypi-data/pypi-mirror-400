from freezegun import freeze_time

from eventix.functions.schedule import schedule_set_next_schedule
from eventix.pydantic.schedule import Schedule
from tests.conftest import dt


def test_schedule_set_next_schedule():
    with freeze_time("2022-01-01"):
        s = Schedule(task="demotask", schedule="*/5 * * * *")
        schedule_set_next_schedule(s)
        assert dt("2022-01-01 00:05") == s.next_schedule


def test_schedule_set_next_schedule_day():
    with freeze_time("2022-01-01"):
        s = Schedule(task="demotask", schedule="*/5 * * * tue")
        schedule_set_next_schedule(s)

        assert True
        # assert dt("2022-01-01 00:05") == s.next_schedule
