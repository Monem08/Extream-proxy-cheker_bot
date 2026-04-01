import logging
from aiogram import types

from bot.keyboards.main_menu import main_menu, join_keyboard
from bot.keyboards.cancel_kb import cancel_kb

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role
from bot.config import OWNER_ID, GROUP_LINK
from bot.middlewares.access_guard import is_joined

from bot.services.message_manager import edit_or_send
from bot.states.user_state import set_state, reset_state, get_state
from bot.services.task_manager import cancel_task
from bot.services.ban_service import is_banned

from bot.database.db import ensure_user, get_balance
from bot.handlers.callback_utils import safe_answer

logger = logging.getLogger(__name__)


async def handle_menu_action(callback: types.CallbackQuery, action: str, data: str | None = None):
    user_id = callback.from_user.id
    try:
        role = get_role(user_id)
        is_elevated = role in ["owner", "admin"]
        if not callback.message:
            await safe_answer(callback, "⚠️ Message is unavailable.", show_alert=True)
            return

        if is_maintenance() and not is_elevated:
            await callback.answer("🚧 Maintenance", show_alert=True)
            return

        if is_banned(user_id):
            await edit_or_send(user_id, callback.message, "🚫 Access blocked.")
            return

        if user_id != int(OWNER_ID):
            if is_spamming(user_id):
                banned = add_strike(user_id)
                await edit_or_send(user_id, callback.message, "🚫 Banned for spam." if banned else "⚠️ Slow down.")
                return
            if not is_allowed(user_id):
                await callback.answer("⏳ Try again in a moment.", show_alert=True)
                return

        await ensure_user(user_id)
        balance = await get_balance(user_id)
        ui_state = "scanning" if get_state(user_id) in {"WAITING_PROXY", "WAITING_FILE"} else "idle"

        if action in {"home", "menu"}:
            await edit_or_send(user_id, callback.message, "🚀 Choose action", main_menu(role, ui_state))
            return

        if action == "settings":
            text = f"⚙️ Settings\n\n⭐ Points: {balance['points']}\n💳 Credits: {balance['credits']}"
            await edit_or_send(user_id, callback.message, text, cancel_kb())
            return

        if action == "verify_join":
            joined = await is_joined(callback.bot, user_id)
            if not joined:
                await edit_or_send(user_id, callback.message, "🔐 Join the group first.", join_keyboard(GROUP_LINK))
                return
            await edit_or_send(user_id, callback.message, "✅ Verified\n🚀 Choose action", main_menu(role, ui_state))
            return

        if action == "cancel":
            reset_state(user_id)
            await cancel_task(user_id)
            await edit_or_send(user_id, callback.message, "🔙 Back to menu", main_menu(role, "idle"))
            return

        if action == "scan_start":
            set_state(user_id, "WAITING_PROXY")
            await edit_or_send(user_id, callback.message, "📂 Send proxies\n(ip:port per line)", cancel_kb())
            return

        if action == "upload":
            set_state(user_id, "WAITING_FILE")
            await edit_or_send(user_id, callback.message, "📂 Send .txt file", cancel_kb())
            return

        await callback.answer("⚠️ Invalid action", show_alert=True)
    except Exception:
        logger.exception("Menu handler failed for user %s", user_id)
        if callback.message:
            await edit_or_send(user_id, callback.message, "⚠️ Something went wrong. Please try again.")
