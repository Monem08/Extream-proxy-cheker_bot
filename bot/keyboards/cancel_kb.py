from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cancel_kb():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    )
    return kb
