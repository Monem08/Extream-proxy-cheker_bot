from aiogram import types
from bot.loader import dp
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu
from bot.services.message_manager import save_message
from bot.services.task_manager import start_task, cancel_task, get_task
from bot.states.user_state import set_state, reset_state


# 🚀 START SCAN (SINGLE SCREEN MODE)
@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # 💀 DELETE CURRENT MENU (MAIN MAGIC)
    try:
        await callback.message.delete()
    except:
        pass

    # cancel previous task
    if get_task(user_id):
        cancel_task(user_id)

    # start new
    start_task(user_id, "SCAN")
    set_state(user_id, "WAITING_PROXY")

    msg = await callback.message.answer(
        "📂 Send proxy list (ip:port)",
        reply_markup=cancel_kb()
    )

    save_message(user_id, msg.message_id)


# ❌ CANCEL → BACK TO MENU
@dp.callback_query_handler(lambda c: c.data == "cancel_action")
async def cancel_action(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # cancel + reset
    cancel_task(user_id)
    reset_state(user_id)

    # 💀 DELETE CURRENT SCREEN
    try:
        await callback.message.delete()
    except:
        pass

    # 🔙 BACK MENU
    msg = await callback.message.answer(
        "🔙 Back to Menu",
        reply_markup=main_menu()
    )

    save_message(user_id, msg.message_id)
