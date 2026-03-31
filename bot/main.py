import asyncio
import logging
import os
import fcntl
from contextlib import suppress

from aiogram.utils.exceptions import TerminatedByOtherGetUpdates

from bot.loader import dp, bot as tg_bot
from bot.web import start_health_server
from bot.database.db import init_db

# Register handlers (specific first, fallback last)
import bot.handlers.start  # noqa: F401
import bot.handlers.menu  # noqa: F401
import bot.handlers.scanner  # noqa: F401
import bot.handlers.live  # noqa: F401
import bot.handlers.owner  # noqa: F401
import bot.handlers.upload  # noqa: F401
import bot.handlers.info  # noqa: F401
import bot.handlers.fallback  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_lock_file = None


def acquire_single_instance_lock() -> None:
    global _lock_file
    lock_path = os.getenv("POLLING_LOCK_FILE", "/tmp/telegram_bot_polling.lock")

    _lock_file = open(lock_path, "w")
    try:
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_file.write(str(os.getpid()))
        _lock_file.flush()
    except BlockingIOError:
        logger.error("Another polling instance is already running. Exiting.")
        _lock_file.close()
        _lock_file = None
        raise SystemExit(1)


async def run_polling() -> None:
    # Ensure polling mode only (remove webhook conflicts)
    await tg_bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling()
    except TerminatedByOtherGetUpdates:
        logger.warning("Polling stopped: another instance is consuming updates.")

async def main() -> None:
    await init_db()
    acquire_single_instance_lock()

    port = int(os.getenv("PORT", "10000"))
    health_runner = await start_health_server(port)
    logger.info("Health server started on port %s", port)

    try:
        await run_polling()
    finally:
        await health_runner.cleanup()
        await tg_bot.session.close()

        if _lock_file is not None:
            with suppress(Exception):
                fcntl.flock(_lock_file.fileno(), fcntl.LOCK_UN)
                _lock_file.close()


if __name__ == "__main__":
    asyncio.run(main())
