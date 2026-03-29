from aiogram import types
from bot.loader import dp
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu
from bot.services.message_manager import save_message, get_message
from bot.services.task_manager import start_task, cancel_task, get_task
from bot.states.user_state import set_state, reset_state


# 🚀 START SCAN BUTTON
@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # 💀 delete old menu
    old_msg = get_message(user_id)
    if old_msg:
        try:
            await callback.bot.delete_message(callback.message.chat.id, old_msg)
        except:
            pass

    # cancel previous task
    if get_task(user_id):
        cancel_task(user_id)

    # start new task
    start_task(user_id, "SCAN")
    set_state(user_id, "WAITING_PROXY")

    msg = await callback.message.answer(
        "📂 Send proxy list (ip:port)",
        reply_markup=cancel_kb()
    )

    save_message(user_id, msg.message_id)


# ❌ CANCEL BUTTON
@dp.callback_query_handler(lambda c: c.data == "cancel_action")
async def cancel_action(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # cancel + reset
    cancel_task(user_id)
    reset_state(user_id)

    # delete current screen
    try:
        await callback.message.delete()
    except:
        pass

    # back to menu
    msg = await callback.message.answer(
        "🔙 Back to Menu",
        reply_markup=main_menu()
    )

    save_message(user_id, msg.message_id)
