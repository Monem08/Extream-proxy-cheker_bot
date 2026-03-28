from bot.config import GROUP_ID

async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False
