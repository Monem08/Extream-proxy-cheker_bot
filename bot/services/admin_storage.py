import json
from pathlib import Path

FILE = Path("bot/data/admin_storage.json")


def _default_data():
    return {
        "users": [],
        "banned_users": [],
        "premium_users": [],
        "stats": {
            "total_scans": 0,
        },
    }


def load_data():
    if not FILE.exists():
        return _default_data()

    try:
        data = json.loads(FILE.read_text())
        if not isinstance(data, dict):
            data = _default_data()
    except Exception:
        data = _default_data()

    base = _default_data()
    base.update(data)
    base["stats"].update(data.get("stats", {}))
    return base


def save_data(data):
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(data, indent=2))


def register_user(user_id):
    user_id = int(user_id)
    data = load_data()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)


def increment_scans(count=1):
    data = load_data()
    data["stats"]["total_scans"] = int(data["stats"].get("total_scans", 0)) + int(count)
    save_data(data)


def get_totals():
    data = load_data()
    return {
        "total_users": len(data["users"]),
        "total_scans": int(data["stats"].get("total_scans", 0)),
    }


def ban_user(user_id):
    user_id = int(user_id)
    data = load_data()
    if user_id not in data["banned_users"]:
        data["banned_users"].append(user_id)
        save_data(data)


def unban_user(user_id):
    user_id = int(user_id)
    data = load_data()
    if user_id in data["banned_users"]:
        data["banned_users"].remove(user_id)
        save_data(data)


def is_banned(user_id):
    user_id = int(user_id)
    return user_id in load_data()["banned_users"]


def add_premium(user_id):
    user_id = int(user_id)
    data = load_data()
    if user_id not in data["premium_users"]:
        data["premium_users"].append(user_id)
        save_data(data)


def remove_premium(user_id):
    user_id = int(user_id)
    data = load_data()
    if user_id in data["premium_users"]:
        data["premium_users"].remove(user_id)
        save_data(data)


def is_premium(user_id):
    user_id = int(user_id)
    return user_id in load_data()["premium_users"]


def get_all_users():
    return load_data()["users"]
