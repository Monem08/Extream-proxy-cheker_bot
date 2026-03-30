from aiogram.utils.exceptions import MessageToDeleteNotFound

user_messages = {}


async def save_message(user_id, message):
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
    except MessageToDeleteNotFound:
        pass
    except Exception:
        pass
