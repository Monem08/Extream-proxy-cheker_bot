import asyncio
import random

from aiogram import types

from bot.services.message_manager import save_message


async def typing_delay(bot, chat_id: int, min_delay: float = 0.5, max_delay: float = 1.0) -> None:
    await bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(random.uniform(min_delay, max_delay))


async def edit_or_send(
    user_id: int,
    message: types.Message,
    text: str,
    reply_markup=None,
):
    try:
        edited = await message.edit_text(text, reply_markup=reply_markup)
        await save_message(user_id, edited)
        return edited
    except Exception:
        sent = await message.bot.send_message(message.chat.id, text, reply_markup=reply_markup)
        await save_message(user_id, sent)
        return sent
