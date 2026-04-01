import logging
from aiogram import types

from bot.loader import dp

from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import start_user_task, cancel_task
from bot.services.message_manager import edit_or_send
from bot.services.ban_service import is_banned

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role

from bot.keyboards.cancel_kb import cancel_kb
from bot.services.admin_storage import increment_scans

logger = logging.getLogger(__name__)


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_file(message: types.Message):
    user_id = message.from_user.id

    try:
        if is_banned(user_id):
            await edit_or_send(user_id, message, "🚫 You are banned")
            return

        role = get_role(user_id)
        if is_maintenance() and role != "owner":
            await edit_or_send(user_id, message, "🚧 Bot Under Maintenance\n⏳ Try later")
            return

        if is_spamming(user_id):
            banned = add_strike(user_id)
            await edit_or_send(user_id, message, "🚫 You are banned" if banned else "⚠️ Stop spamming!")
            return

        if not is_allowed(user_id):
            await edit_or_send(user_id, message, "⏳ Slow down...")
            return

        if get_state(user_id) != "WAITING_FILE":
            return

        file = await message.document.get_file()
        downloaded = await message.bot.download_file(file.file_path)
        content = downloaded.read().decode(errors="ignore")
        proxies = [p.strip() for p in content.split("\n") if ":" in p and p.strip()]

        if not proxies:
            await edit_or_send(user_id, message, "❌ No valid proxies found", cancel_kb())
            return

        await edit_or_send(user_id, message, "🚀 Scanning file...", cancel_kb())

        async def _run_scan_job():
            return await run_scan(proxies)

        task = await start_user_task(user_id, _run_scan_job())
        results = await task
        increment_scans()

        alive = [(p, s) for p, ok, s in results if ok and s]
        fast = [p for p, s in alive if s < 1000]
        dead = [p for p, ok, s in results if not ok]
        details = "\n".join(fast[:20]) if fast else "-"

        await edit_or_send(
            user_id,
            message,
            f"✅ File Scan Complete\n\n🟢 Alive: {len(fast)}\n🔴 Dead: {len(dead)}\n\nTop proxies:\n{details}",
            cancel_kb(),
        )
    except Exception:
        logger.exception("handle_file failed for user %s", user_id)
        await edit_or_send(user_id, message, "⚠️ File scan failed", cancel_kb())
    finally:
        reset_state(user_id)
        await cancel_task(user_id)
