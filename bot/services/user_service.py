from bot.database.db import add_user, get_user, get_all_user_ids


async def ensure_user(user_id):
    await add_user(int(user_id))


async def get_user_data(user_id):
    return await get_user(int(user_id))


async def get_all_users():
    return await get_all_user_ids()
