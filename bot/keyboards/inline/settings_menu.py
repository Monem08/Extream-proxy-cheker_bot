from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_settings_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🔙 Back", callback_data="menu:home"),
        InlineKeyboardButton("🔄 Refresh", callback_data="settings:refresh"),
    )
    return kb


def build_owner_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.row(InlineKeyboardButton("🔙 Back", callback_data="menu:home"))
    return kb
