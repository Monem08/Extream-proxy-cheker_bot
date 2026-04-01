from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_join_menu(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🚀 Join Group", url=link),
                InlineKeyboardButton("✅ Verify", callback_data="menu:verify"),
            ]
        ]
    )
