import json
from pathlib import Path

FILE = Path("bot/data/stats.json")


def load_stats():
    if not FILE.exists():
        return {
            "users": [],
            "scans": 0,
            "live": 0
        }
    return json.loads(FILE.read_text())


def save_stats(data):
    FILE.parent.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(data, indent=2))


def add_user(user_id):
    data = load_stats()

    if user_id not in data["users"]:
        data["users"].append(user_id)

    save_stats(data)


def add_scan():
    data = load_stats()
    data["scans"] += 1
    save_stats(data)


def add_live():
    data = load_stats()
    data["live"] += 1
    save_stats(data)


def get_stats():
    data = load_stats()

    return {
        "users": len(data["users"]),
        "scans": data["scans"],
        "live": data["live"]
    }
