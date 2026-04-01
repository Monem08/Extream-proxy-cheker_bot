import logging
from aiogram import types
from aiogram.types import ReplyKeyboardRemove

from bot.loader import dp
from bot.config import GROUP_LINK, OWNER_ID
from bot.middlewares.access_guard import is_joined

from bot.database.db import ensure_user, get_balance
from bot.services.role_service import get_role
from bot.services.ban_service import is_banned
from bot.services.maintenance_service import is_maintenance
from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.task_manager import cancel_task
from bot.states.user_state import get_state, set_state, reset_state
from bot.services.message_manager import edit_or_send
from bot.services.admin_storage import get_totals

from bot.keyboards.inline.main_menu import build_main_menu
from bot.keyboards.inline.scan_menu import build_scan_menu, build_upload_menu
from bot.keyboards.inline.settings_menu import build_settings_menu, build_owner_menu
from bot.keyboards.inline.join_menu import build_join_menu

logger = logging.getLogger(__name__)

_ALLOWED = {
    "menu": {"home", "verify", "settings", "info"},
    "scan": {"start"},
    "proxy": {"upload", "live"},
    "settings": {"open", "refresh"},
    "owner": {"panel"},
    "info": {"view"},
    "action": {"cancel"},
}


async def _guard_user(callback: types.CallbackQuery) -> bool:
    user_id = callback.from_user.id
    role = get_role(user_id)

    if is_banned(user_id):
        await edit_or_send(user_id, callback.message, "🚫 Access blocked")
        return False

    if is_maintenance() and role not in {"owner", "admin"}:
        await callback.answer("🚧 Maintenance", show_alert=True)
        return False

    if user_id != int(OWNER_ID):
        if is_spamming(user_id):
            banned = add_strike(user_id)
            await edit_or_send(user_id, callback.message, "🚫 Banned" if banned else "⚠️ Slow down")
            return False
        if not is_allowed(user_id):
            await callback.answer("⏳ Try again", show_alert=True)
            return False

    return True


async def show_home(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    role = get_role(user_id)
    await ensure_user(user_id)
    state = get_state(user_id)
    status = "🟢 Active" if state in {"WAITING_PROXY", "WAITING_FILE"} else "⚪ Idle"
    await edit_or_send(
        user_id,
        callback.message,
        f"🚀 Main Menu\nStatus: {status}",
        build_main_menu(role),
    )


async def show_settings(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    await ensure_user(user_id)
    balance = await get_balance(user_id)
    text = f"⚙️ Settings\n⭐ Points: {balance['points']}\n💳 Credits: {balance['credits']}"
    await edit_or_send(user_id, callback.message, text, build_settings_menu())


async def show_info(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    role = get_role(user_id)
    if role == "owner":
        totals = get_totals()
        text = f"ℹ️ Info\n👥 Users: {totals['total_users']}\n⚡ Scans: {totals['total_scans']}"
    else:
        text = "ℹ️ Info\nUse scan or upload to check proxies."
    await edit_or_send(user_id, callback.message, text, build_owner_menu())


async def show_owner(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    if get_role(user_id) != "owner":
        await callback.answer("❌ Access denied", show_alert=True)
        return
    totals = get_totals()
    text = f"👑 Owner Panel\n👥 Users: {totals['total_users']}\n⚡ Scans: {totals['total_scans']}"
    await edit_or_send(user_id, callback.message, text, build_owner_menu())


@dp.callback_query_handler()
async def callback_router(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        if not callback.message:
            await callback.answer("⚠️ Message unavailable", show_alert=True)
            return
        loading = await callback.message.answer(
            "♻️ Resetting UI...",
            reply_markup=ReplyKeyboardRemove()
        )

        raw = (callback.data or "").strip()
        parts = raw.split(":")
        if len(parts) != 2:
            await callback.answer("⚠️ Invalid action", show_alert=True)
            return

        module, action = parts
        if module not in _ALLOWED or action not in _ALLOWED[module]:
            await callback.answer("⚠️ Unknown action", show_alert=True)
            return

        if not await _guard_user(callback):
            return

        if module == "menu" and action == "home":
            await show_home(callback)
        elif module == "menu" and action == "verify":
            joined = await is_joined(callback.bot, user_id)
            if not joined:
                await edit_or_send(user_id, callback.message, "🔐 Join required", build_join_menu(GROUP_LINK))
            else:
                await show_home(callback)
        elif module == "menu" and action == "settings":
            await show_settings(callback)
        elif module == "menu" and action == "info":
            await show_info(callback)
        elif module == "scan" and action == "start":
            await cancel_task(user_id)
            set_state(user_id, "WAITING_PROXY")
            await edit_or_send(user_id, callback.message, "📥 Send proxies (ip:port)", build_scan_menu())
        elif module == "proxy" and action == "upload":
            await cancel_task(user_id)
            set_state(user_id, "WAITING_FILE")
            await edit_or_send(user_id, callback.message, "📎 Upload .txt proxy file", build_upload_menu())
        elif module == "proxy" and action == "live":
            from bot.handlers.live import handle_live_action

            await handle_live_action(callback)
        elif module == "settings" and action in {"open", "refresh"}:
            await show_settings(callback)
        elif module == "owner" and action == "panel":
            await show_owner(callback)
        elif module == "info" and action == "view":
            await show_info(callback)
        elif module == "action" and action == "cancel":
            reset_state(user_id)
            await cancel_task(user_id)
            await show_home(callback)

        await callback.answer()
        await loading.delete()
    except Exception:
        logger.exception("Callback router failed for user %s", user_id)
        await callback.answer("⚠️ Unexpected error", show_alert=True)
        if callback.message:
            await edit_or_send(user_id, callback.message, "⚠️ Something went wrong", build_main_menu(get_role(user_id)))
