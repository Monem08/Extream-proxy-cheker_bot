import asyncio
import logging
import os
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


# =========================
# 🔧 LOGGING SETUP
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_lock_file = None


# =========================
# 🔒 SAFE SINGLE INSTANCE LOCK
# =========================
def acquire_single_instance_lock() -> None:
    global _lock_file
    lock_path = os.getenv("POLLING_LOCK_FILE", "/tmp/telegram_bot_polling.lock")

    try:
        import fcntl
    except ImportError:
        logger.warning("⚠️ fcntl not available → skipping lock system")
        return

    try:
        _lock_file = open(lock_path, "w")
        fcntl.flock(_lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_file.write(str(os.getpid()))
        _lock_file.flush()
        logger.info("🔒 Lock acquired (single instance running)")
    except BlockingIOError:
        logger.error("❌ Another instance already running → exiting")
        raise SystemExit(1)
    except Exception:
        logger.exception("⚠️ Lock system failed → continuing without lock")


# =========================
# 🤖 POLLING SYSTEM
# =========================
async def run_polling() -> None:
    await tg_bot.delete_webhook(drop_pending_updates=True)

    logger.info("🚀 Starting polling...")

    try:
        await dp.start_polling()
    except TerminatedByOtherGetUpdates:
        logger.warning("⚠️ Polling stopped: another instance is consuming updates.")
    except Exception:
        logger.exception("❌ Polling crashed")


# =========================
# 🧠 MAIN ENTRY
# =========================
async def main() -> None:
    logger.info("🧠 Bot starting...")

    await init_db()
    acquire_single_instance_lock()

    port = int(os.getenv("PORT", "10000"))
    health_runner = await start_health_server(port)

    logger.info("🌐 Health server running on port %s", port)

    try:
        await run_polling()
    finally:
        logger.info("🧹 Shutting down...")

        with suppress(Exception):
            await health_runner.cleanup()

        with suppress(Exception):
            await tg_bot.session.close()

        global _lock_file
        if _lock_file is not None:
            try:
                import fcntl

                fcntl.flock(_lock_file.fileno(), fcntl.LOCK_UN)
                _lock_file.close()
                logger.info("🔓 Lock released")
            except Exception:
                pass


# =========================
# 🚀 START BOT (CRASH SAFE)
# =========================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("💀 Fatal crash in main")
