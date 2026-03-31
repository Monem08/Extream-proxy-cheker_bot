import sqlite3
from bot.database.db import DB_PATH


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ban_user(user_id):
    try:
        with _conn() as conn:
            conn.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (int(user_id),))
            conn.commit()
    except Exception:
        return


def unban_user(user_id):
    try:
        with _conn() as conn:
            conn.execute("DELETE FROM banned_users WHERE user_id = ?", (int(user_id),))
            conn.commit()
    except Exception:
        return


def is_banned(user_id):
    try:
        with _conn() as conn:
            row = conn.execute("SELECT 1 FROM banned_users WHERE user_id = ?", (int(user_id),)).fetchone()
            return bool(row)
    except Exception:
        return False
