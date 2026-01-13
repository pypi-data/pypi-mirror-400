from eventix.functions.core import task
from eventix.functions.task import task_clean_expired_tasks, task_clean_expired_workers


@task(unique_key_generator=lambda: "cleanup_worker", store_result=False)
def task_cleanup_worker():
    task_clean_expired_workers()


@task(unique_key_generator=lambda: "cleanup_tasks", store_result=False)
def task_cleanup_results():
    task_clean_expired_tasks()
