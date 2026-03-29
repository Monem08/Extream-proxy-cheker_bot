from aiogram import types
from bot.loader import dp
from bot.services.task_manager import start_task, get_task, cancel_task
from bot.states.user_state import set_state, reset_state

@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # 💀 delete old message
    old_msg = get_message(user_id)
    if old_msg:
        try:
            await callback.message.bot.delete_message(callback.message.chat.id, old_msg)
        except:
            pass

    # cancel previous task
    if get_task(user_id):
        cancel_task(user_id)
        await callback.message.answer("⚠️ Previous task cancelled")

    start_task(user_id, "SCAN")
    set_state(user_id, "WAITING_PROXY")

    msg = await callback.message.answer("📂 Send proxy list (ip:port)")
    save_message(user_id, msg.message_id)
