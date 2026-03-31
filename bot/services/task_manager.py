import asyncio

active_tasks = {}


def start_task(user_id, task):
    old_task = active_tasks.get(user_id)
    if old_task and isinstance(old_task, asyncio.Task) and not old_task.done():
        old_task.cancel()
    active_tasks[user_id] = task


def get_task(user_id):
    return active_tasks.get(user_id)


def cancel_task(user_id):
    task = active_tasks.pop(user_id, None)
    if isinstance(task, asyncio.Task) and not task.done():
        task.cancel()
    return task is not None
