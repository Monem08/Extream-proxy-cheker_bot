from aiogram import types
from bot.loader import dp

@dp.callback_query_handler(lambda c: c.data == "start_scan")
async def start_scan(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📂 Send proxy list (ip:port per line)"
    )
