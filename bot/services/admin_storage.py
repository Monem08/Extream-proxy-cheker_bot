import sqlite3

from bot.database.db import DB_PATH


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def register_user(user_id):
    try:
        with _conn() as conn:
            conn.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, 'user')", (int(user_id),))
            conn.commit()
    except Exception:
        return


def increment_scans(count=1):
    # DB-only logging counter
    try:
        with _conn() as conn:
            for _ in range(int(count)):
                conn.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (0, "scan"))
            conn.commit()
    except Exception:
        return


def get_totals():
    try:
        with _conn() as conn:
            users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
            scans = conn.execute("SELECT COUNT(*) AS c FROM logs WHERE action IN ('scan','scan_proxies')").fetchone()
            return {
                "total_users": int(users["c"]) if users else 0,
                "total_scans": int(scans["c"]) if scans else 0,
            }
    except Exception:
        return {"total_users": 0, "total_scans": 0}


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


def add_premium(user_id):
    try:
        with _conn() as conn:
            conn.execute("INSERT OR IGNORE INTO premium_users (user_id) VALUES (?)", (int(user_id),))
            conn.commit()
    except Exception:
        return


def remove_premium(user_id):
    try:
        with _conn() as conn:
            conn.execute("DELETE FROM premium_users WHERE user_id = ?", (int(user_id),))
            conn.commit()
    except Exception:
        return


def is_premium(user_id):
    try:
        with _conn() as conn:
            row = conn.execute("SELECT 1 FROM premium_users WHERE user_id = ?", (int(user_id),)).fetchone()
            return bool(row)
    except Exception:
        return False


def get_all_users():
    try:
        with _conn() as conn:
            rows = conn.execute("SELECT user_id FROM users").fetchall()
            return [int(r["user_id"]) for r in rows]
    except Exception:
        return []
