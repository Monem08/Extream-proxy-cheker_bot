from bot.database.db import add_group, remove_group, get_groups


async def add_force_group(group_id):
    await add_group(int(group_id))


async def remove_force_group(group_id):
    await remove_group(int(group_id))


async def get_force_groups():
    return await get_groups()
