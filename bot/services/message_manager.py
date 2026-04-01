import asyncio
import logging
from random import uniform
from typing import Dict, Optional

from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.exceptions import (
    BadRequest,
    MessageCantBeDeleted,
    MessageCantBeEdited,
    MessageNotModified,
    MessageToDeleteNotFound,
    MessageToEditNotFound,
)

logger = logging.getLogger(__name__)

_user_messages: Dict[int, Dict[str, int]] = {}
_user_locks: Dict[int, asyncio.Lock] = {}


def _get_lock(user_id: int) -> asyncio.Lock:
    lock = _user_locks.get(user_id)
    if lock is None:
        lock = asyncio.Lock()
        _user_locks[user_id] = lock
    return lock


async def save_message(user_id: int, message: Message) -> None:
    _user_messages[user_id] = {
        "chat_id": int(message.chat.id),
        "message_id": int(message.message_id),
    }


def get_message(user_id: int) -> Optional[Dict[str, int]]:
    return _user_messages.get(user_id)


async def _typing(bot, chat_id: int) -> None:
    try:
        await bot.send_chat_action(chat_id, "typing")
    except Exception:
        logger.debug("Typing indicator failed for user chat %s", chat_id)


async def _small_delay(min_delay: float = 0.25, max_delay: float = 0.55) -> None:
    await asyncio.sleep(uniform(min_delay, max_delay))


async def _delete_tracked(bot, tracked: Dict[str, int]) -> None:
    try:
        await bot.delete_message(chat_id=tracked["chat_id"], message_id=tracked["message_id"])
    except (MessageToDeleteNotFound, MessageCantBeDeleted, BadRequest):
        return
    except Exception:
        logger.exception("Failed deleting tracked message")


async def delete_previous(user_id: int, bot=None) -> None:
    lock = _get_lock(user_id)
    async with lock:
        tracked = _user_messages.pop(user_id, None)
        if tracked and bot is not None:
            await _delete_tracked(bot, tracked)


async def edit_or_send(
    user_id: int,
    source_message: Message,
    text: str,
    keyboard: InlineKeyboardMarkup = None,
    disable_web_page_preview: bool = True,
) -> Message:
    bot = source_message.bot
    chat_id = source_message.chat.id

    lock = _get_lock(user_id)
    async with lock:
        await _typing(bot, chat_id)
        await _small_delay()

        tracked = get_message(user_id)
        if tracked:
            try:
                edited = await bot.edit_message_text(
                    chat_id=tracked["chat_id"],
                    message_id=tracked["message_id"],
                    text=text,
                    reply_markup=keyboard,
                    disable_web_page_preview=disable_web_page_preview,
                )
                await save_message(user_id, edited)
                return edited
            except MessageNotModified:
                msg = await bot.send_message(
                    chat_id=tracked["chat_id"],
                    text=text,
                    reply_markup=keyboard,
                    disable_web_page_preview=disable_web_page_preview,
                )
                await _delete_tracked(bot, tracked)
                await save_message(user_id, msg)
                return msg
            except (MessageToEditNotFound, MessageCantBeEdited, BadRequest):
                pass
            except Exception:
                logger.exception("Edit failed for user %s", user_id)

        msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=disable_web_page_preview,
        )

        previous = _user_messages.get(user_id)
        if previous and previous != {"chat_id": msg.chat.id, "message_id": msg.message_id}:
            await _delete_tracked(bot, previous)

        await save_message(user_id, msg)
        return msg


async def delete_message(user_id: int, bot=None) -> None:
    await delete_previous(user_id, bot)
