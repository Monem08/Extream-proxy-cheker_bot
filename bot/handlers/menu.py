from aiogram import types
from bot.loader import dp
from bot.keyboards.cancel_kb import cancel_kb
from bot.keyboards.main_menu import main_menu
from bot.services.task_manager import start_task, cancel_task, get_task
from bot.states.user_state import set_state, reset_state


# 🚀 START SCAN
@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # 💀 RESET STATE FIRST (IMPORTANT)
    reset_state(user_id)

    # delete current menu
    try:
        await callback.message.delete()
    except:
        pass

    # cancel previous task
    if get_task(user_id):
        cancel_task(user_id)

    # start new scan
    start_task(user_id, "SCAN")
    set_state(user_id, "WAITING_PROXY")

    await callback.message.answer(
        "📂 Send proxy list (ip:port)",
        reply_markup=cancel_kb()
    )


# 📂 UPLOAD PROXY
@dp.callback_query_handler(lambda c: c.data == "upload")
async def upload_proxy(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    # 💀 RESET STATE FIRST
    reset_state(user_id)

    # delete current menu
    try:
        await callback.message.delete()
    except:
        pass

    # set upload mode
    set_state(user_id, "WAITING_FILE")

    await callback.message.answer(
        "📂 Send .txt file with proxies",
        reply_markup=cancel_kb()
    )


# ❌ CANCEL ACTION
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
    await callback.message.answer(
        "✅ System Ready\n\n👑 Welcome Operator",
        reply_markup=main_menu()
    )
