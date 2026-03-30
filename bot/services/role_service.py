from bot.config import OWNER_ID


def get_role(user_id):
    if user_id == OWNER_ID:
        return "owner"
    return "user"


def is_owner(user_id):
    return user_id == OWNER_ID
