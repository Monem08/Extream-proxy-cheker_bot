from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_main_menu(role: str = "user") -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.row(
        InlineKeyboardButton("🚀 Start Scan", callback_data="scan:start"),
        InlineKeyboardButton("📂 Upload", callback_data="proxy:upload"),
    )
    kb.row(
        InlineKeyboardButton("🌐 Live", callback_data="proxy:live"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings:open"),
    )
    if role == "owner":
        kb.row(InlineKeyboardButton("👑 Owner Panel", callback_data="owner:panel"))
    kb.row(InlineKeyboardButton("ℹ️ Info", callback_data="info:view"))
    return kb
