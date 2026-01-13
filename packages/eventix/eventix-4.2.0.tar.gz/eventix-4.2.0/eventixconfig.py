config = dict(
    namespace="eventix_system",
    register_tasks=["eventix.tasks.cleanup"],
    schedule=[
        {"schedule": "*/2 * * * *", "task": "task_cleanup_worker", "args": [], "kwargs": {}},
        {
            "schedule": "*/2 * * * *",
            "task": "task_cleanup_results",
            # "args": [],
            # "kwargs": {}
        },
    ],
)
