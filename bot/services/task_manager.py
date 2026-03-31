import asyncio
from typing import Optional

active_tasks = {}

def start_task(user_id, task: Optional[asyncio.Task] = None, task_name: Optional[str] = None):
    cancel_task(user_id)
    active_tasks[user_id] = {"task": task, "name": task_name or getattr(task, "get_name", lambda: None)()}

def get_task(user_id):
    return active_tasks.get(user_id)

def cancel_task(user_id):
    data = active_tasks.pop(user_id, None)
    if not data:
        return False

    task = data.get("task")
    if task and not task.done():
        task.cancel()
    return True
