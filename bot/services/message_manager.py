import logging

from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted, BadRequest

user_messages = {}
logger = logging.getLogger(__name__)


async def save_message(user_id, message):
    previous = user_messages.get(user_id)
    if previous and not (
        previous["chat_id"] == message.chat.id and previous["message_id"] == message.message_id
    ):
        try:
            await message.bot.delete_message(previous["chat_id"], previous["message_id"])
        except (MessageToDeleteNotFound, MessageCantBeDeleted, BadRequest):
            pass
        except Exception:
            logger.exception("Failed to delete previous message for user %s", user_id)

    user_messages[user_id] = {
        "chat_id": message.chat.id,
        "message_id": message.message_id,
    }


def get_message(user_id):
    return user_messages.get(user_id)


async def delete_message(user_id, bot=None):
    data = user_messages.pop(user_id, None)
    if not data or bot is None:
        return

    try:
        await bot.delete_message(data["chat_id"], data["message_id"])
    except (MessageToDeleteNotFound, MessageCantBeDeleted, BadRequest):
        pass
    except Exception:
        logger.exception("Failed to delete tracked message for user %s", user_id)
