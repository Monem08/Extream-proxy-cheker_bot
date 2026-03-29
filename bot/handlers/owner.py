from aiogram import types
from bot.loader import dp
from bot.config import OWNER_ID
from bot.services.role_service import add_admin, remove_admin


@dp.message_handler(commands=["add_admin"])
async def add_admin_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(message.get_args())
        add_admin(user_id)
        await message.answer(f"✅ Added admin: {user_id}")
    except:
        await message.answer("❌ Usage: /add_admin 123456")


@dp.message_handler(commands=["remove_admin"])
async def remove_admin_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(message.get_args())
        remove_admin(user_id)
        await message.answer(f"❌ Removed admin: {user_id}")
    except:
        await message.answer("❌ Usage: /remove_admin 123456")
