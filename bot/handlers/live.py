import logging
from aiogram import types

from bot.services.live_proxy_service import fetch_proxies
from bot.services.scanner_service import run_scan
from bot.keyboards.cancel_kb import cancel_kb

from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role

from bot.services.message_manager import edit_or_send
from bot.services.ban_service import is_banned
from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.task_manager import start_user_task, cancel_task

logger = logging.getLogger(__name__)


async def handle_live_action(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        role = get_role(user_id)

        if is_banned(user_id):
            await edit_or_send(user_id, callback.message, "🚫 Access blocked.")
            return

        if is_maintenance() and role not in ["owner", "admin"]:
            await callback.answer("🚧 Maintenance", show_alert=True)
            return

        if is_spamming(user_id):
            banned = add_strike(user_id)
            await edit_or_send(user_id, callback.message, "🚫 Banned for spam." if banned else "⚠️ Slow down.")
            return

        if not is_allowed(user_id):
            await callback.answer("⏳ Try again in a moment.", show_alert=True)
            return

        await edit_or_send(user_id, callback.message, "🌐 Fetching live proxies...\n⏳ Processing...", cancel_kb())

        proxies = await fetch_proxies()
        if not proxies:
            await edit_or_send(user_id, callback.message, "❌ No live proxies found.", cancel_kb())
            return

        task = await start_user_task(user_id, run_scan(proxies[:50]))
        results = await task
        alive = [p for p, ok, _ in results if ok]

        text = "❌ No alive proxies." if not alive else f"✅ Live ready\n🟢 Alive: {len(alive)}\n\n" + "\n".join(alive[:10])
        await edit_or_send(user_id, callback.message, text, cancel_kb())
    except Exception:
        logger.exception("handle_live_action failed for user %s", user_id)
        if callback.message:
            await edit_or_send(user_id, callback.message, "⚠️ Live scan failed", cancel_kb())
    finally:
        await cancel_task(user_id)
