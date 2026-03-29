import json
from pathlib import Path

DATA_FILE = Path("bot/data/users.json")


def load_users():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())


def save_users(users):
    DATA_FILE.write_text(json.dumps(users, indent=2))


def add_user(user_id, name):
    users = load_users()

    if user_id not in [u["id"] for u in users]:
        users.append({
            "id": user_id,
            "name": name
        })
        save_users(users)


def get_all_users():
    return load_users()
