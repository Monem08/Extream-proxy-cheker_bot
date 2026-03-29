from aiogram import types
from bot.loader import dp, bot
from bot.config import OWNER_ID

from bot.services.role_service import add_admin, remove_admin, load_admins
from bot.services.user_service import get_all_users
from bot.services.broadcast_service import broadcast
from bot.services.ban_service import ban_user, unban_user


# 👑 ADD ADMIN
@dp.message_handler(commands=["add_admin"])
async def add_admin_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(message.get_args())
        add_admin(user_id)
        await message.answer(f"✅ Admin added: {user_id}")
    except:
        await message.answer("❌ Usage: /add_admin 123456")


# ❌ REMOVE ADMIN
@dp.message_handler(commands=["remove_admin"])
async def remove_admin_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(message.get_args())
        remove_admin(user_id)
        await message.answer(f"❌ Admin removed: {user_id}")
    except:
        await message.answer("❌ Usage: /remove_admin 123456")


# 📊 STATS
@dp.message_handler(commands=["stats"])
async def stats_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    users = len(get_all_users())
    admins = len(load_admins())

    await message.answer(
        f"""📊 Stats

👤 Users: {users}
⚡ Admins: {admins}
"""
    )


# 📢 BROADCAST
@dp.message_handler(commands=["broadcast"])
async def broadcast_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    text = message.get_args()

    if not text:
        await message.answer("❌ Usage: /broadcast your message")
        return

    ok, fail = await broadcast(bot, text)

    await message.answer(
        f"""📢 Broadcast Done

✅ Sent: {ok}
❌ Failed: {fail}
"""
    )


# 🚫 BAN USER
@dp.message_handler(commands=["ban"])
async def ban_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(message.get_args())
        ban_user(user_id)
        await message.answer(f"🚫 Banned: {user_id}")
    except:
        await message.answer("❌ Usage: /ban 123456")


# ✅ UNBAN USER
@dp.message_handler(commands=["unban"])
async def unban_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    try:
        user_id = int(message.get_args())
        unban_user(user_id)
        await message.answer(f"✅ Unbanned: {user_id}")
    except:
        await message.answer("❌ Usage: /unban 123456")
