import sqlite3

from bot.config import OWNER_ID
from bot.database.db import DB_PATH


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_role(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return "user"

    if uid == int(OWNER_ID):
        return "owner"

    try:
        with _conn() as conn:
            row = conn.execute("SELECT role FROM users WHERE user_id = ?", (uid,)).fetchone()
            if not row:
                conn.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, 'user')", (uid,))
                conn.commit()
                return "user"

            role = (row["role"] or "user").lower()
            if role in ["owner", "admin", "user"]:
                return role
    except Exception:
        pass

    return "user"


def is_owner(user_id):
    return get_role(user_id) == "owner"
