from aiogram import types
from bot.loader import dp, bot

from bot.keyboards.main_menu import main_menu, join_keyboard

from bot.middlewares.access_guard import is_joined
from bot.config import GROUP_LINK

from bot.services.task_manager import get_task, cancel_task
from bot.states.user_state import reset_state

from bot.services.role_service import get_role
from bot.services.ban_service import is_banned
from bot.services.maintenance_service import is_maintenance
from bot.services.admin_storage import register_user, get_totals

from bot.services.message_manager import save_message, delete_message


@dp.message_handler(commands=["start"], state="*")
async def start_cmd(message: types.Message):
    user_id = message.from_user.id

    if is_banned(user_id):
        await message.answer("🚫 You are banned")
        return

    await delete_message(user_id, message.bot)

    if get_task(user_id):
        cancel_task(user_id)
        reset_state(user_id)

    role = get_role(user_id)

    if is_maintenance() and role != "owner":
        msg = await message.answer("🚧 Bot Under Maintenance\n⏳ Try later")
        await save_message(user_id, msg)
        return

    joined = await is_joined(bot, user_id)
    if not joined:
        msg = await message.answer(
            "🔐 Join group to use bot",
            reply_markup=join_keyboard(GROUP_LINK),
        )
        await save_message(user_id, msg)
        return

    register_user(user_id)

    if role == "owner":
        totals = get_totals()
        text = f"""👑 OWNER PANEL

📊 Stats
👥 Users: {totals['total_users']}
⚡ Scans: {totals['total_scans']}

⚙️ Controls:
- /broadcast → send message to all users
- /ban <user_id> → ban user
- /unban <user_id> → unban user
- /addpremium <user_id> → give premium
- /removepremium <user_id> → remove premium"""
    else:
        text = """👤 USER PANEL

🚀 Proxy Scan
🌍 Live Proxies"""

    msg = await message.answer(text, reply_markup=main_menu(role))
    await save_message(user_id, msg)
