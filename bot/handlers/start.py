from aiogram import types
from bot.loader import dp, bot
from bot.utils.ui_builder import progress_bar
from bot.keyboards.main_menu import main_menu, join_keyboard
from bot.middlewares.access_guard import is_joined
from bot.config import GROUP_LINK
from bot.services.task_manager import get_task, cancel_task
from bot.states.user_state import reset_state
from bot.services.user_service import add_user
from bot.services.role_service import get_role
from bot.services.ban_service import is_banned

import asyncio


@dp.message_handler(commands=["start"], state="*")
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "User"

    # 🚫 BAN CHECK
    if is_banned(user_id):
        await message.answer("🚫 You are banned")
        return

    # 💀 CANCEL OLD TASK
    if get_task(user_id):
        cancel_task(user_id)
        reset_state(user_id)
        await message.answer("⚠️ Previous task cancelled")

    # 🔐 JOIN CHECK
    joined = await is_joined(bot, user_id)
    if not joined:
        await message.answer(
            "🔐 Join group to use bot",
            reply_markup=join_keyboard(GROUP_LINK),
        )
        return

    # 👤 ADD USER (SAFE)
    try:
        add_user(user_id)
    except:
        pass

    role = get_role(user_id)

    # ⚡ LOADING UI
    msg = await message.answer("⚡ Initializing...")

    try:
        for p in range(10, 101, 10):
            await asyncio.sleep(0.2)
            await msg.edit_text(
                f"⚡ Booting...\n{progress_bar(p)}"
            )

        # ✅ FINAL MENU
        await msg.edit_text(
            f"""✅ System Ready

👑 Welcome {name}

🆔 ID: {user_id}
🎭 Role: {role}

📊 Status:
• System: Online 🟢
• Scanner: Ready ⚡
• Live API: Active 🌍

🚀 Choose an action below:""",
            reply_markup=main_menu(),
        )

    except Exception as e:
        print("START ERROR:", e)
        await message.answer("⚠️ Failed to load UI")
