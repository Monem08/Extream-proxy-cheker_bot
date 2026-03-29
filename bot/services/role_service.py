import json
from pathlib import Path
from bot.config import OWNER_ID

ADMIN_FILE = Path("bot/data/admins.json")


def load_admins():
    if not ADMIN_FILE.exists():
        return []
    return json.loads(ADMIN_FILE.read_text())


def save_admins(admins):
    ADMIN_FILE.write_text(json.dumps(admins, indent=2))


def get_role(user_id):
    if user_id == OWNER_ID:
        return "Owner 👑"
    elif user_id in load_admins():
        return "Admin ⚡"
    else:
        return "User 👤"


def is_admin(user_id):
    return user_id in load_admins() or user_id == OWNER_ID


def add_admin(user_id):
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)


def remove_admin(user_id):
    admins = load_admins()
    if user_id in admins:
        admins.remove(user_id)
        save_admins(admins)
