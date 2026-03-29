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
import asyncio


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id

    # 💀 Cancel previous task if exists
    if get_task(user_id):
        cancel_task(user_id)
        reset_state(user_id)
        await message.answer("⚠️ Previous task cancelled")

    # 🔐 Force join check
    joined = await is_joined(bot, user_id)

    if not joined:
        await message.answer(
            "🔐 Access Restricted\n\nJoin group to use bot",
            reply_markup=join_keyboard(GROUP_LINK),
        )
        return

    # ⚡ Animation start
    msg = await message.answer("⚡ Initializing...")

    for p in range(10, 101, 10):
        await asyncio.sleep(0.3)
        await msg.edit_text(
            f"⚡ Booting Proxy OS...\n\n{progress_bar(p)}"
        )

    # ✅ Final UI
    await msg.edit_text(
        "✅ System Ready\n\n👑 Welcome Operator",
        reply_markup=main_menu(),
    )


@dp.callback_query_handler(lambda c: c.data == "verify_join")
async def verify(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    joined = await is_joined(bot, user_id)

    if joined:
        await callback.message.delete()
        await callback.message.answer(
            "✅ Access Granted",
            reply_markup=main_menu()
        )
    else:
        await callback.answer("❌ Join first", show_alert=True)
