from aiogram import types

from bot.services.role_service import get_role
from bot.services.admin_storage import get_totals
from bot.services.message_manager import edit_or_send
from bot.keyboards.cancel_kb import cancel_kb
from bot.database.db import get_balance, ensure_user


async def handle_info_action(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    if role == "owner":
        totals = get_totals()
        balance = await get_balance(user_id)
        text = (
            "👑 Owner Panel\n\n"
            f"👥 Users: {totals['total_users']}\n"
            f"⚡ Scans: {totals['total_scans']}\n"
            f"⭐ Points: {balance['points']}\n"
            f"💳 Credits: {balance['credits']}"
        )
    else:
        await ensure_user(user_id)
        balance = await get_balance(user_id)
        text = (
            "👤 User Panel\n\n"
            "🚀 Proxy Scan\n"
            "🌐 Live Proxies\n"
            f"⭐ Points: {balance['points']}\n"
            f"💳 Credits: {balance['credits']}"
        )

    await edit_or_send(user_id, callback.message, text, cancel_kb())
