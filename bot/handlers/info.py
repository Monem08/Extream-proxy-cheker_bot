from aiogram import types
from bot.loader import dp
from bot.services.role_service import get_role
from bot.services.stats_service import get_stats


@dp.callback_query_handler(lambda c: c.data == "info")
async def info_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    stats = get_stats()

    if role == "owner":
        text = f"""👑 OWNER PANEL

📊 Users: {stats['users']}
📊 Scans: {stats['scans']}
📊 Live: {stats['live']}

⚙️ Commands:
• Admin control
• Maintenance toggle
• Full access"""

    elif role == "admin":
        text = f"""🛡 ADMIN PANEL

📊 Users: {stats['users']}

⚙️ Commands:
• Ban/Unban
• View stats"""

    else:
        text = """👤 USER PANEL

🚀 Features:
• Proxy Scan
• Live Proxies"""

    await callback.message.answer(text)
    await callback.answer()
