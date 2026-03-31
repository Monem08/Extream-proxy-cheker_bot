from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cancel_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel"))
    return kb
