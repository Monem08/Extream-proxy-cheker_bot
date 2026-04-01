import logging
from aiogram import types

from bot.loader import dp
from bot.services.message_manager import edit_or_send
from bot.services.role_service import get_role
from bot.keyboards.inline.main_menu import build_main_menu

logger = logging.getLogger(__name__)


@dp.message_handler()
async def fallback_message(message: types.Message):
    user_id = message.from_user.id
    try:
        await edit_or_send(
            user_id,
            message,
            "⚠️ Use the inline buttons to navigate.",
            build_main_menu(get_role(user_id)),
        )
    except Exception:
        logger.exception("Fallback handler failed for user %s", user_id)
