from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu(role="user", state="idle"):
    kb = InlineKeyboardMarkup(row_width=2)
    scan_label = "🛑 Stop Scan" if state == "scanning" else "🚀 Start Scan"
    scan_action = "scan:stop" if state == "scanning" else "scan:start"

    kb.add(
        InlineKeyboardButton(scan_label, callback_data=scan_action),
        InlineKeyboardButton("📂 Upload", callback_data="proxy:upload"),
    )
    kb.add(
        InlineKeyboardButton("🌐 Live", callback_data="proxy:live"),
        InlineKeyboardButton("⚙️ Settings", callback_data="menu:settings"),
    )

    if role == "owner":
        kb.add(
            InlineKeyboardButton("🛠 Maintenance", callback_data="owner:maintenance"),
            InlineKeyboardButton("👑 Panel", callback_data="owner:panel"),
        )

    kb.add(InlineKeyboardButton("ℹ️ Info", callback_data="menu:info"))
    return kb


def nav_keyboard(role="user"):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("🚀 Scan"), KeyboardButton("📂 Upload"))
    kb.row(KeyboardButton("🌐 Live"), KeyboardButton("⚙️ Settings"))
    if role == "owner":
        kb.row(KeyboardButton("👑 Panel"), KeyboardButton("ℹ️ Info"))
    else:
        kb.row(KeyboardButton("ℹ️ Info"))
    return kb


def join_keyboard(link):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Join Group", url=link),
        InlineKeyboardButton("✅ Verify", callback_data="menu:verify_join"),
    )
    return kb
