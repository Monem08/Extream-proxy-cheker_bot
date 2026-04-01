from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_main_menu(role: str):
    buttons = [
        [
            InlineKeyboardButton("🚀 Scan", callback_data="scan:start"),
            InlineKeyboardButton("📂 Upload", callback_data="proxy:upload"),
        ],
        [
            InlineKeyboardButton("🌐 Live", callback_data="proxy:live"),
            InlineKeyboardButton("⚙️ Settings", callback_data="menu:settings"),
        ],
        [
            InlineKeyboardButton("ℹ️ Info", callback_data="menu:info")
        ]
    ]

    if role == "owner":
        buttons.insert(2, [
            InlineKeyboardButton("👑 Panel", callback_data="owner:panel")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
