from aiogram import types
from bot.loader import dp

from bot.handlers.callback_utils import safe_answer


@dp.callback_query_handler()
async def fallback_callback(callback: types.CallbackQuery):
    await safe_answer(callback, "⚠️ Unknown action. Please try again.")
