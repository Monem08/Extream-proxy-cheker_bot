from bot.services.user_service import get_all_users


async def broadcast(bot, text):
    users = get_all_users()

    success = 0
    fail = 0

    for user in users:
        try:
            await bot.send_message(user["id"], text)
            success += 1
        except:
            fail += 1

    return success, fail
