from bot.config import OWNER_ID


def get_role(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return "user"

    if user_id == int(OWNER_ID):
        return "owner"
    return "user"


def is_owner(user_id):
    return get_role(user_id) == "owner"
