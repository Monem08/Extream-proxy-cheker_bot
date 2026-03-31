from bot.config import OWNER_ID
from bot.database.db import add_user, get_user


def get_role(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return "user"

    if uid == int(OWNER_ID):
        return "owner"

    add_user(uid)
    user = get_user(uid)
    if not user:
        return "user"

    role = (user.get("role") or "user").lower()
    if role not in ["owner", "admin", "user"]:
        return "user"
    return role


def is_owner(user_id):
    return get_role(user_id) == "owner"
