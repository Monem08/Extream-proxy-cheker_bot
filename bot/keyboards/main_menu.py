from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.keyboards.inline.main_menu import build_main_menu


def main_menu(role="user", state="idle"):
    return build_main_menu(role)


def join_keyboard(link):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🚀 Join Group", url=link),
        InlineKeyboardButton("✅ Verify", callback_data="menu:verify"),
    )
    return kb
