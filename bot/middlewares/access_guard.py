from bot.services.group_service import get_force_groups


async def is_joined(bot, user_id):
    try:
        groups = await get_force_groups()
        if not groups:
            return True

        for group_id in groups:
            member = await bot.get_chat_member(group_id, user_id)
            if member.status in ["member", "administrator", "creator"]:
                return True

        return False
    except Exception:
        return False
