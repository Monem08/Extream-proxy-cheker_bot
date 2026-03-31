# bot/handlers/menu.py
from aiogram import types
from bot.loader import dp

from bot.keyboards.main_menu import main_menu, join_keyboard
from bot.keyboards.cancel_kb import cancel_kb

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role
from bot.config import OWNER_ID, GROUP_LINK
from bot.middlewares.access_guard import is_joined

from bot.services.message_manager import save_message, delete_message
from bot.states.user_state import set_state, reset_state
from bot.services.task_manager import cancel_task
from bot.services.ban_service import is_banned

from bot.handlers.callback_utils import safe_answer
from bot.database.db import ensure_user, get_balance
from bot.utils.response_manager import typing_delay, edit_or_send


@dp.callback_query_handler(lambda c: c.data in {"menu", "start_scan", "upload", "settings", "cancel", "verify_join"})
async def handle_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)
    is_elevated = role in ["owner", "admin"]

    try:
        await typing_delay(callback.bot, callback.message.chat.id)

        if is_maintenance() and not is_elevated:
            await safe_answer(callback, "🚧 Bot Under Maintenance", show_alert=True)
            return

        if is_banned(user_id):
            msg = await callback.message.answer("🚫 You are banned")
            await save_message(user_id, msg)
            return

        if user_id != int(OWNER_ID):
            if is_spamming(user_id):
                banned = add_strike(user_id)
                msg = await callback.message.answer("🚫 You are banned for spam" if banned else "⚠️ Stop spamming!")
                await save_message(user_id, msg)
                return

            if not is_allowed(user_id):
                await safe_answer(callback, "⏳ Slow down bro...", show_alert=True)
                return

        data = callback.data
        await ensure_user(user_id)
        balance = await get_balance(user_id)

        await delete_message(user_id, callback.bot)

        if data == "menu":
            await edit_or_send(user_id, callback.message, "🚀 Choose an option:", reply_markup=main_menu(role))

        elif data == "start_scan":
            cancel_task(user_id)
            reset_state(user_id)
            set_state(user_id, "WAITING_PROXY")
            await edit_or_send(user_id, callback.message, "⏳ Processing...\n\n📂 Send proxy list (ip:port)", reply_markup=cancel_kb())

        elif data == "upload":
            cancel_task(user_id)
            reset_state(user_id)
            set_state(user_id, "WAITING_FILE")
            await edit_or_send(user_id, callback.message, "⏳ Processing...\n\n📂 Send .txt file with proxies", reply_markup=cancel_kb())

        elif data == "settings":
            await edit_or_send(
                user_id,
                callback.message,
                f"⚙️ Settings\n\n⭐ Points: {balance['points']}\n💳 Credits: {balance['credits']}",
                reply_markup=cancel_kb(),
            )

        elif data == "verify_join":
            joined = await is_joined(callback.bot, user_id)
            if not joined:
                await safe_answer(callback, "❌ You must join first", show_alert=True)
                await edit_or_send(user_id, callback.message, "🔐 Join group to use bot", reply_markup=join_keyboard(GROUP_LINK))
                return

            await edit_or_send(user_id, callback.message, "✅ Completed\n\n🚀 Choose an option:", reply_markup=main_menu(role))

        elif data == "cancel":
            await delete_message(user_id, callback.bot)
            reset_state(user_id)
            cancel_task(user_id)
            await edit_or_send(user_id, callback.message, "🔙 Back to menu", reply_markup=main_menu(role))

    except Exception:
        await edit_or_send(user_id, callback.message, "❌ Failed\nPlease try again.")
    finally:
        await safe_answer(callback)
