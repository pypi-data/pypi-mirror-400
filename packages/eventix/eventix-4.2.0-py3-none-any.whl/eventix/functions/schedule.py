import datetime

from croniter import croniter
from pydantic_db_backend_common.utils import utcnow

from eventix.pydantic.schedule import Schedule


def schedule_set_next_schedule(schedule: Schedule):
    if schedule.next_schedule is None or schedule.next_schedule < utcnow():
        schedule.last_schedule = schedule.next_schedule
        schedule.next_schedule = croniter(schedule.schedule).get_next(datetime.datetime, utcnow())
