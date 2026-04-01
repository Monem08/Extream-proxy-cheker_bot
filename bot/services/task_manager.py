import asyncio
import logging
from contextlib import suppress
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_active_tasks: Dict[int, asyncio.Task] = {}


def _cleanup_done_task(user_id: int, task: asyncio.Task) -> None:
    current = _active_tasks.get(user_id)
    if current is task:
        _active_tasks.pop(user_id, None)


def get_task(user_id: int) -> Optional[asyncio.Task]:
    task = _active_tasks.get(user_id)
    if task and task.done():
        _active_tasks.pop(user_id, None)
        return None
    return task


async def cancel_task(user_id: int) -> bool:
    task = _active_tasks.pop(user_id, None)
    if not task:
        return False

    if not task.done():
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        excepted = task.exception() if task.done() and not task.cancelled() else None
        if excepted:
            logger.error("Task for user %s failed during cancellation: %s", user_id, excepted)
    return True


def start_task(user_id: int, task: asyncio.Task) -> None:
    previous = get_task(user_id)
    if previous and not previous.done():
        previous.cancel()

    _active_tasks[user_id] = task
    task.add_done_callback(lambda t: _cleanup_done_task(user_id, t))


async def start_user_task(user_id: int, coroutine) -> asyncio.Task:
    await cancel_task(user_id)
    task = asyncio.create_task(coroutine)
    start_task(user_id, task)
    return task
