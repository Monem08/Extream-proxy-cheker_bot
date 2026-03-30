from aiogram import types
from bot.loader import dp

from bot.services.role_service import get_role
from bot.services.maintenance_service import set_maintenance, is_maintenance

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.config import OWNER_ID

# 💀 NEW
from bot.services.message_manager import save_message, delete_message
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu


# =========================
# 👑 MAINTENANCE TOGGLE
# =========================
@dp.callback_query_handler(lambda c: c.data == "maintenance")
async def toggle_maintenance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    # ❌ ACCESS CONTROL
    if role not in ["owner", "admin"]:
        await callback.answer("❌ Not allowed", show_alert=True)
        return

    # 🛡 SECURITY (ADMIN ONLY)
    if user_id != OWNER_ID:
        if is_spamming(user_id):
            banned = add_strike(user_id)
            await callback.message.answer(
                "🚫 You are banned for spam" if banned else "⚠️ Stop spamming!"
            )
            return

        if not is_allowed(user_id):
            await callback.answer("⏳ Slow down bro...", show_alert=True)
            return

    # 💀 DELETE OLD UI
    await delete_message(user_id)

    try:
        await callback.message.delete()
    except:
        pass

    # 🔄 TOGGLE
    current = is_maintenance()
    new_state = not current
    set_maintenance(new_state)

    status = "ON 🔒" if new_state else "OFF ✅"

    msg = await callback.message.answer(
        f"⚙️ Maintenance Mode: {status}",
        reply_markup=cancel_kb()
    )

    await save_message(user_id, msg)

    await callback.answer()


# =========================
# 👑 ADMIN PANEL
# =========================
@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    if role not in ["owner", "admin"]:
        await callback.answer("❌ Not allowed", show_alert=True)
        return

    # 💀 DELETE OLD UI
    await delete_message(user_id)

    try:
        await callback.message.delete()
    except:
        pass

    text = """👑 ADMIN PANEL

⚙️ Controls:
• Toggle Maintenance
• View Stats (via Info)
• Future: Ban / Unban

🔥 Full Control Access Enabled
"""

    msg = await callback.message.answer(
        text,
        reply_markup=cancel_kb()
    )

    await save_message(user_id, msg)

    await callback.answer()


# =========================
# ❌ CANCEL SUPPORT (OPTIONAL SAFE)
# =========================
@dp.callback_query_handler(lambda c: c.data == "cancel_admin")
async def cancel_admin(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    await delete_message(user_id)

    try:
        await callback.message.delete()
    except:
        pass

    msg = await callback.message.answer(
        "🔙 Back to menu",
        reply_markup=main_menu(role)
    )

    await save_message(user_id, msg)

    await callback.answer()
