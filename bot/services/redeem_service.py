from bot.database.db import create_code, redeem_code


async def create_redeem_code(code, points=0, credits=0, limit=1):
    await create_code(code, int(points), int(credits), int(limit))


async def redeem(user_id, code):
    return await redeem_code(int(user_id), code)
