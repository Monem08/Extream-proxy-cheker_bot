from aiogram import types
from bot.loader import dp

from bot.services.role_service import get_role
from bot.services.stats_service import get_stats

# 💀 NEW
from bot.services.message_manager import delete_message, save_message
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu


@dp.callback_query_handler(lambda c: c.data == "info")
async def info_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    # 💀 DELETE OLD UI
    await delete_message(user_id)

    try:
        await callback.message.delete()
    except:
        pass

    stats = get_stats()

    # 👑 OWNER
    if role == "owner":
        text = f"""👑 OWNER PANEL

📊 Users: {stats['users']}
📊 Scans: {stats['scans']}
📊 Live: {stats['live']}

⚙️ Commands:
• /start
• Maintenance toggle
• Admin control
• Full access"""

    # 🛡 ADMIN
    elif role == "admin":
        text = f"""🛡 ADMIN PANEL

📊 Users: {stats['users']}

⚙️ Commands:
• /start
• View stats
• Limited control"""

    # 👤 USER
    else:
        text = """👤 USER PANEL

🚀 Features:
• Proxy Scan
• Live Proxies

💡 Use buttons below 👇"""

    # 💀 SHOW WITH CANCEL BUTTON
    msg = await callback.message.answer(
        text,
        reply_markup=cancel_kb()
    )

    await save_message(user_id, msg)

    await callback.answer()
