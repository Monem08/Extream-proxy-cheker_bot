import logging
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
from bot.services.admin_storage import get_totals
from bot.database.db import (
    ensure_user,
    get_user,
    get_balance,
    save_referral,
    complete_referral,
    set_joined,
)

from bot.services.message_manager import save_message, delete_previous

logger = logging.getLogger(__name__)


@dp.message_handler(commands=["start"], state="*")
async def start_cmd(message: types.Message):
    user_id = message.from_user.id

    try:
        # ❌ banned check
        if is_banned(user_id):
            await message.answer("🚫 You are banned")
            return

        # 🧹 clean old messages
        await delete_previous(user_id, message.bot)

        # 🔄 cancel old tasks
        if get_task(user_id):
            cancel_task(user_id)
            reset_state(user_id)

        await ensure_user(user_id)

        # 🎁 referral system
        ref_arg = (message.get_args() or "").strip()
        if ref_arg.isdigit():
            referrer_id = int(ref_arg)
            if referrer_id != user_id:
                await save_referral(user_id, referrer_id)

        role = get_role(user_id)

        # 🚧 maintenance check
        if is_maintenance() and role not in ["owner", "admin"]:
            msg = await message.answer("🚧 Bot Under Maintenance\n⏳ Try later")
            await save_message(user_id, msg)
            return

        # 🔐 force join check
        joined = await is_joined(bot, user_id)
        if not joined:
            msg = await message.answer(
                "🔐 Join required to use bot",
                reply_markup=join_keyboard(GROUP_LINK),
            )
            await save_message(user_id, msg)
            return

        await set_joined(user_id, True)
        await complete_referral(user_id)

        # 👤 user data
        user = await get_user(user_id) or {"role": "user"}
        balance = await get_balance(user_id)

        # 👑 OWNER PANEL
        if role == "owner":
            totals = get_totals()
            text = f"""👑 OWNER PANEL

📊 Stats
👥 Users: {totals['total_users']}
⚡ Scans: {totals['total_scans']}

💰 Balance
⭐ Points: {balance['points']}
💳 Credits: {balance['credits']}

⚙️ Controls:
- /broadcast → send message to all users
- /ban <user_id> → ban user
- /unban <user_id> → unban user
- /addpremium <user_id> → give premium
- /removepremium <user_id> → remove premium"""
        else:
            # 👤 USER PANEL
            text = f"""👤 USER PANEL

🚀 Proxy Scan
🌍 Live Proxies

💰 Balance
⭐ Points: {balance['points']}
💳 Credits: {balance['credits']}

🎭 Role: {user.get('role', 'user')}"""

        # 📩 send message
        msg = await message.answer(text, reply_markup=main_menu(role))
        await save_message(user_id, msg)

    except Exception:
        logger.exception("Failed to process /start for user %s", user_id)
        msg = await message.answer("❌ Failed to open menu. Please try again.")
        await save_message(user_id, msg)
