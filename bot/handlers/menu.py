from aiogram import types
from bot.loader import dp
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu
from bot.services.task_manager import start_task, cancel_task, get_task
from bot.states.user_state import set_state, reset_state


# 🚀 START SCAN (DELETE + NEW SCREEN)
@dp.callback_query_handler(lambda c: c.data == "upload")
async def upload_proxy(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # 💀 delete menu
    try:
        await callback.message.delete()
    except:
        pass

    # set state
    set_state(user_id, "WAITING_FILE")

    await callback.message.answer(
        "📂 Send .txt file with proxies",
        reply_markup=cancel_kb()
    )


# ❌ CANCEL → BACK MENU
@dp.callback_query_handler(lambda c: c.data == "cancel_action")
async def cancel_action(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    cancel_task(user_id)
    reset_state(user_id)

    # 💀 DELETE CURRENT SCREEN
    try:
        await callback.message.delete()
    except:
        pass

    # 🔙 SHOW MENU AGAIN
    await callback.message.answer(
        "✅ System Ready\n\n👑 Welcome Operator",
        reply_markup=main_menu()
    )
