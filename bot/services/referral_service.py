from bot.database.db import save_referral, get_referral, complete_referral


async def create_referral(user_id, referrer_id):
    await save_referral(int(user_id), int(referrer_id))


async def fetch_referral(user_id):
    return await get_referral(int(user_id))


async def finalize_referral(user_id):
    return await complete_referral(int(user_id))
