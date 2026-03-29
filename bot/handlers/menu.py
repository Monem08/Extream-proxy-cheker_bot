from aiogram import types
from bot.loader import dp
from bot.services.task_manager import start_task, get_task, cancel_task
from bot.states.user_state import set_state, reset_state

@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # ⚠️ cancel previous task
    if get_task(user_id):
        cancel_task(user_id)
        await callback.message.delete()
        await callback.message.answer("⚠️ Previous task cancelled")

    # start new task
    start_task(user_id, "SCAN")
    set_state(user_id, "WAITING_PROXY")

    await callback.message.answer("📂 Send proxy list (ip:port)")
