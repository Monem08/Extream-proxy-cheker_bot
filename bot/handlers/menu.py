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


@dp.callback_query_handler(lambda c: c.data in {"menu", "start_scan", "upload", "settings", "cancel", "verify_join"})
async def handle_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    try:
        if is_maintenance() and role not in ["owner", "admin"]:
            await safe_answer(callback, "🚧 Bot Under Maintenance", show_alert=True)
            return

        if is_banned(user_id):
            msg = await callback.message.answer("🚫 You are banned")
            await save_message(user_id, msg)
            return

        if user_id != OWNER_ID:
            if is_spamming(user_id):
                banned = add_strike(user_id)
                msg = await callback.message.answer("🚫 You are banned for spam" if banned else "⚠️ Stop spamming!")
                await save_message(user_id, msg)
                return

            if not is_allowed(user_id):
                await safe_answer(callback, "⏳ Slow down bro...", show_alert=True)
                return

        data = callback.data

        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        if data == "menu":
            msg = await callback.message.answer("🚀 Choose an option:", reply_markup=main_menu(role))
            await save_message(user_id, msg)

        elif data == "start_scan":
            set_state(user_id, "WAITING_PROXY")
            msg = await callback.message.answer("📂 Send proxy list (ip:port)", reply_markup=cancel_kb())
            await save_message(user_id, msg)

        elif data == "upload":
            set_state(user_id, "WAITING_FILE")
            msg = await callback.message.answer("📂 Send .txt file with proxies", reply_markup=cancel_kb())
            await save_message(user_id, msg)

        elif data == "settings":
            msg = await callback.message.answer("⚙️ Settings coming soon...", reply_markup=cancel_kb())
            await save_message(user_id, msg)

        elif data == "verify_join":
            joined = await is_joined(callback.bot, user_id)
            if not joined:
                await safe_answer(callback, "❌ You must join first", show_alert=True)
                msg = await callback.message.answer("🔐 Join group to use bot", reply_markup=join_keyboard(GROUP_LINK))
                await save_message(user_id, msg)
                return

            msg = await callback.message.answer("✅ Verification successful.\n🚀 Choose an option:", reply_markup=main_menu(role))
            await save_message(user_id, msg)

        elif data == "cancel":
            await delete_message(user_id, callback.bot)
            reset_state(user_id)
            cancel_task(user_id)
            msg = await callback.message.answer("🔙 Back to menu", reply_markup=main_menu(role))
            await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Something went wrong. Please try again.")
    finally:
        await safe_answer(callback)
