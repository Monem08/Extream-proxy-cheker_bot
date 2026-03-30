from aiogram import types
from bot.loader import dp

from bot.keyboards.main_menu import main_menu
from bot.keyboards.cancel_kb import cancel_kb

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role
from bot.config import OWNER_ID

# 💀 NEW
from bot.services.message_manager import save_message, delete_message
from bot.states.user_state import set_state, reset_state
from bot.services.task_manager import cancel_task


@dp.callback_query_handler()
async def handle_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    # 🚧 MAINTENANCE
    if is_maintenance() and role not in ["owner", "admin"]:
        await callback.answer("🚧 Bot Under Maintenance", show_alert=True)
        return

    # 👑 OWNER BYPASS
    if user_id != OWNER_ID:

        if is_spamming(user_id):
            banned = add_strike(user_id)
            if banned:
                await callback.message.answer("🚫 You are banned for spam")
            else:
                await callback.message.answer("⚠️ Stop spamming!")
            return

        if not is_allowed(user_id):
            await callback.answer("⏳ Slow down bro...", show_alert=True)
            return

    data = callback.data

    # 💀 DELETE OLD UI (IMPORTANT)
    await delete_message(user_id)

    try:
        await callback.message.delete()
    except:
        pass

    # =========================
    # 🚀 MAIN MENU
    # =========================
    if data == "menu":
        msg = await callback.message.answer(
            "🚀 Choose an option:",
            reply_markup=main_menu(role)
        )
        await save_message(user_id, msg)

    # =========================
    # 🚀 START SCAN
    # =========================
    elif data == "start_scan":
        msg = await callback.message.answer(
            "📂 Send proxy list (ip:port)",
            reply_markup=cancel_kb()
        )
        await save_message(user_id, msg)
        set_state(user_id, "WAITING_PROXY")

    # =========================
    # 📂 UPLOAD FILE
    # =========================
    elif data == "upload":
        msg = await callback.message.answer(
            "📂 Send .txt file with proxies",
            reply_markup=cancel_kb()
        )
        await save_message(user_id, msg)
        set_state(user_id, "WAITING_FILE")

    # =========================
    # 🌍 LIVE PROXY
    # =========================
    elif data == "live":
        msg = await callback.message.answer(
            "🌍 Fetching proxies...",
            reply_markup=cancel_kb()
        )
        await save_message(user_id, msg)

    # =========================
    # ⚙️ SETTINGS
    # =========================
    elif data == "settings":
        msg = await callback.message.answer(
            "⚙️ Settings coming soon...",
            reply_markup=cancel_kb()
        )
        await save_message(user_id, msg)

    # =========================
    # 👑 ADMIN PANEL
    # =========================
    elif data == "admin_panel":
        if role not in ["admin", "owner"]:
            await callback.answer("🚫 Access Denied", show_alert=True)
            return

        msg = await callback.message.answer(
            "👑 Admin Panel\n\nMore features coming...",
            reply_markup=cancel_kb()
        )
        await save_message(user_id, msg)

    # =========================
    # ℹ️ INFO
    # =========================
    elif data == "info":
        if role == "owner":
            text = "👑 Owner Commands:\n/start\n/ban\n/unban\n/stats\n..."
        elif role == "admin":
            text = "👑 Admin Commands:\n/start\n/stats\n..."
        else:
            text = "ℹ️ Send proxy list or use buttons"

        msg = await callback.message.answer(
            text,
            reply_markup=cancel_kb()
        )
        await save_message(user_id, msg)

    # =========================
    # ❌ CANCEL (MAIN FIX 💀)
    # =========================
    elif data == "cancel":
        reset_state(user_id)
        cancel_task(user_id)

        msg = await callback.message.answer(
            "🔙 Back to menu",
            reply_markup=main_menu(role)
        )
        await save_message(user_id, msg)

    # =========================
    await callback.answer()
