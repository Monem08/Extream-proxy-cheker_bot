import json
from pathlib import Path

FILE = Path("bot/data/stats.json")


def load_stats():
    if not FILE.exists():
        return {}
    return json.loads(FILE.read_text())


def save_stats(data):
    FILE.write_text(json.dumps(data, indent=2))


def inc_stat(key):
    data = load_stats()
    data[key] = data.get(key, 0) + 1
    save_stats(data)


def get_stats():
    return load_stats()
    
stats = {
    "users": set(),
    "scans": 0,
    "live": 0
}

def add_user(user_id):
    stats["users"].add(user_id)

def add_scan():
    stats["scans"] += 1

def add_live():
    stats["live"] += 1

def get_stats():
    return {
        "users": len(stats["users"]),
        "scans": stats["scans"],
        "live": stats["live"]
    }
