from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_scan_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("❌ Cancel", callback_data="action:cancel"),
        InlineKeyboardButton("🔙 Back", callback_data="menu:home"),
    )
    return kb


def build_upload_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("❌ Cancel", callback_data="action:cancel"),
        InlineKeyboardButton("🔙 Back", callback_data="menu:home"),
    )
    return kb
