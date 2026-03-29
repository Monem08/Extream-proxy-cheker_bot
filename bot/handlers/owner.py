from aiogram import types
from bot.loader import dp

from bot.services.role_service import get_role
from bot.services.maintenance_service import set_maintenance, is_maintenance

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.config import OWNER_ID


# 👑 MAINTENANCE TOGGLE
@dp.callback_query_handler(lambda c: c.data == "maintenance")
async def toggle_maintenance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    # ❌ Only owner/admin allowed
    if role not in ["owner", "admin"]:
        await callback.answer("❌ Not allowed", show_alert=True)
        return

    # 👑 OWNER BYPASS SECURITY
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

    current = is_maintenance()
    new_state = not current
    set_maintenance(new_state)

    status = "ON 🔒" if new_state else "OFF ✅"

    try:
        await callback.message.edit_text(f"⚙️ Maintenance Mode: {status}")
    except:
        await callback.message.answer(f"⚙️ Maintenance Mode: {status}")

    await callback.answer()


# 👑 ADMIN PANEL (OPTIONAL BUTTON)
@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    if role not in ["owner", "admin"]:
        await callback.answer("❌ Not allowed", show_alert=True)
        return

    text = """👑 ADMIN PANEL

⚙️ Controls:
• Toggle Maintenance
• Manage Users (coming soon)
• Stats (via Info)

🔥 Control Access Enabled
"""

    await callback.message.answer(text)
    await callback.answer()
