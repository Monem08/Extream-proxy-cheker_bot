from aiogram import types
from bot.loader import dp
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu
from bot.services.task_manager import start_task, cancel_task, get_task
from bot.states.user_state import set_state, reset_state


# 🚀 START SCAN (DELETE + NEW SCREEN)
@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # 💀 DELETE MENU MESSAGE
    try:
        await callback.message.delete()
    except:
        pass

    # cancel previous task
    if get_task(user_id):
        cancel_task(user_id)

    start_task(user_id, "SCAN")
    set_state(user_id, "WAITING_PROXY")

    # ✅ NEW SCREEN
    await callback.message.answer(
        "📂 Send proxy list (ip:port)",
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
