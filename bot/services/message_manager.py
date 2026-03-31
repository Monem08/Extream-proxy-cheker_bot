import asyncio
from random import uniform

from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.exceptions import (
    MessageCantBeEdited,
    MessageNotModified,
    MessageToDeleteNotFound,
    MessageToEditNotFound,
)

user_messages = {}


async def save_message(user_id: int, message: Message):
    user_messages[user_id] = {"chat_id": message.chat.id, "message_id": message.message_id}


def get_message(user_id: int):
    return user_messages.get(user_id)


async def delete_previous(user_id: int, bot=None):
    data = user_messages.pop(user_id, None)
    if not data or bot is None:
        return

    try:
        await bot.delete_message(data["chat_id"], data["message_id"])
    except MessageToDeleteNotFound:
        pass
    except Exception:
        pass


async def _human_delay(min_delay: float = 0.4, max_delay: float = 0.9):
    await asyncio.sleep(uniform(min_delay, max_delay))


async def edit_or_send(user_id: int, source_message: Message, text: str, keyboard: InlineKeyboardMarkup = None):
    bot = source_message.bot
    chat_id = source_message.chat.id

    await bot.send_chat_action(chat_id, "typing")
    await _human_delay()

    tracked = get_message(user_id)
    if tracked:
        try:
            edited = await bot.edit_message_text(
                chat_id=tracked["chat_id"],
                message_id=tracked["message_id"],
                text=text,
                reply_markup=keyboard,
            )
            await save_message(user_id, edited)
            return edited
        except (MessageNotModified, MessageToEditNotFound, MessageCantBeEdited):
            pass
        except Exception:
            pass

    fresh = await source_message.answer(text, reply_markup=keyboard)
    await save_message(user_id, fresh)
    return fresh


# backwards compatible alias
async def delete_message(user_id: int, bot=None):
    await delete_previous(user_id, bot)
