from aiogram import types
from bot.loader import dp, bot
from bot.utils.ui_builder import progress_bar
from bot.keyboards.main_menu import main_menu, join_keyboard
from bot.middlewares.access_guard import is_joined
from bot.config import GROUP_LINK
import asyncio


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id

    # 💀 cancel previous task if exists
    if get_task(user_id):
        cancel_task(user_id)
        reset_state(user_id)
        await message.answer("⚠️ Previous task cancelled")

    joined = await is_joined(bot, user_id)

    if not joined:
        await message.answer(
            "🔐 Access Restricted\n\nJoin group to use bot",
            reply_markup=join_keyboard(GROUP_LINK),
        )
        return

    msg = await message.answer("⚡ Initializing...")

    for p in range(10, 101, 10):
        await asyncio.sleep(0.3)
        await msg.edit_text(
            f"⚡ Booting Proxy OS...\n\n{progress_bar(p)}"
        )

    await msg.edit_text(
        "✅ System Ready\n\n👑 Welcome Operator",
        reply_markup=main_menu(),
    )
    else:
        await callback.answer("❌ Join first", show_alert=True)
