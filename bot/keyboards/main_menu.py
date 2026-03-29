from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Start Scan", callback_data="start_scan"),
        InlineKeyboardButton("📂 Upload Proxy", callback_data="upload"),
        InlineKeyboardButton("🌍 Live Proxies", callback_data="live"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton("⚙️ Maintenance", callback_data="maintenance"),
        InlineKeyboardButton("👑 Admin", callback_data="admin_panel"),
        InlineKeyboardButton("ℹ️ Info", callback_data="info")
    )
    return kb


def join_keyboard(link):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🚀 Join Group", url=link),
        InlineKeyboardButton("✅ Verify", callback_data="verify_join"),
    )
    return kb
