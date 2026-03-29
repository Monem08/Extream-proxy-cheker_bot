from aiogram import types
from bot.loader import dp
from bot.keyboards.main_menu import main_menu

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role
from bot.config import OWNER_ID


@dp.callback_query_handler()
async def handle_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    role = get_role(user_id)

    # 💀 MAINTENANCE
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

    try:
        await callback.message.delete()
    except:
        pass

    if data == "menu":
        await callback.message.answer("🚀 Choose:", reply_markup=main_menu())

    elif data == "start_scan":
        await callback.message.answer("📂 Send proxy list (ip:port)")

    elif data == "upload":
        await callback.message.answer("📂 Send .txt file")

    elif data == "live":
        await callback.message.answer("🌍 Fetching proxies...")

    elif data == "settings":
        await callback.message.answer("⚙️ Settings coming soon...")

    elif data == "cancel":
        await callback.message.answer("🔙 Back", reply_markup=main_menu())

    await callback.answer()
