import json
from pathlib import Path

FILE = Path("bot/data/bans.json")


def load_bans():
    if not FILE.exists():
        return []
    return json.loads(FILE.read_text())


def save_bans(data):
    FILE.write_text(json.dumps(data, indent=2))


def ban_user(user_id):
    bans = load_bans()
    if user_id not in bans:
        bans.append(user_id)
        save_bans(bans)


def unban_user(user_id):
    bans = load_bans()
    if user_id in bans:
        bans.remove(user_id)
        save_bans(bans)


def is_banned(user_id):
    return user_id in load_bans()
