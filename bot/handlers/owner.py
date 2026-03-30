from aiogram import types
from bot.loader import dp

from bot.services.role_service import get_role
from bot.services.maintenance_service import set_maintenance, is_maintenance

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.config import OWNER_ID

from bot.services.message_manager import save_message, delete_message
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu

from bot.handlers.callback_utils import safe_answer


@dp.callback_query_handler(lambda c: c.data == "maintenance")
async def toggle_maintenance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    try:
        if role not in ["owner", "admin"]:
            await safe_answer(callback, "❌ Not allowed", show_alert=True)
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

        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        new_state = not is_maintenance()
        set_maintenance(new_state)
        status = "ON 🔒" if new_state else "OFF ✅"

        msg = await callback.message.answer(f"⚙️ Maintenance Mode: {status}", reply_markup=cancel_kb())
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to update maintenance mode")
    finally:
        await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    try:
        if role not in ["owner", "admin"]:
            await safe_answer(callback, "❌ Not allowed", show_alert=True)
            return

        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        text = """👑 ADMIN PANEL

⚙️ Controls:
• Toggle Maintenance
• View Stats (via Info)
• Future: Ban / Unban

🔥 Full Control Access Enabled
"""

        msg = await callback.message.answer(text, reply_markup=cancel_kb())
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to open admin panel")
    finally:
        await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data == "cancel_admin")
async def cancel_admin(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    try:
        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        msg = await callback.message.answer("🔙 Back to menu", reply_markup=main_menu(role))
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to return to menu")
    finally:
        await safe_answer(callback)
