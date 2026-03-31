import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from bot.config import OWNER_ID

DB_PATH = Path("bot/data/bot.sqlite3")


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(_connect()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER DEFAULT 0,
                credits INTEGER DEFAULT 0,
                role TEXT DEFAULT 'user',
                joined INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS referrals (
                user_id INTEGER PRIMARY KEY,
                referrer_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS force_groups (
                group_id INTEGER PRIMARY KEY
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS redeem_codes (
                code TEXT PRIMARY KEY,
                points INTEGER DEFAULT 0,
                credits INTEGER DEFAULT 0,
                code_limit INTEGER DEFAULT 1,
                used_count INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS code_redeems (
                user_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                PRIMARY KEY (user_id, code)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id INTEGER PRIMARY KEY
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY
            )
            """
        )


def add_user(user_id: int):
    role = "owner" if int(user_id) == int(OWNER_ID) else "user"
    with closing(_connect()) as conn, conn:
        conn.execute(
            """
            INSERT INTO users (user_id, role)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (int(user_id), role),
        )


def get_user(user_id: int) -> Optional[Dict]:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (int(user_id),)).fetchone()
        return dict(row) if row else None


def add_points(user_id: int, amount: int):
    add_user(user_id)
    with closing(_connect()) as conn, conn:
        conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (int(amount), int(user_id)))


def add_credits(user_id: int, amount: int):
    add_user(user_id)
    with closing(_connect()) as conn, conn:
        conn.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (int(amount), int(user_id)))


def get_balance(user_id: int) -> Dict[str, int]:
    add_user(user_id)
    with closing(_connect()) as conn:
        row = conn.execute("SELECT points, credits FROM users WHERE user_id = ?", (int(user_id),)).fetchone()
        if not row:
            return {"points": 0, "credits": 0}
        return {"points": int(row["points"]), "credits": int(row["credits"])}


def save_referral(user_id: int, referrer_id: int):
    if int(user_id) == int(referrer_id):
        return
    with closing(_connect()) as conn, conn:
        conn.execute(
            """
            INSERT INTO referrals (user_id, referrer_id, status)
            VALUES (?, ?, 'pending')
            ON CONFLICT(user_id) DO NOTHING
            """,
            (int(user_id), int(referrer_id)),
        )


def complete_referral(user_id: int) -> Optional[int]:
    with closing(_connect()) as conn, conn:
        row = conn.execute(
            "SELECT referrer_id, status FROM referrals WHERE user_id = ?", (int(user_id),)
        ).fetchone()
        if not row or row["status"] == "completed":
            return None

        conn.execute("UPDATE referrals SET status = 'completed' WHERE user_id = ?", (int(user_id),))
        return int(row["referrer_id"])


def add_group(group_id: int):
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT OR IGNORE INTO force_groups (group_id) VALUES (?)", (int(group_id),))


def get_groups() -> List[int]:
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT group_id FROM force_groups").fetchall()
        return [int(r["group_id"]) for r in rows]


def create_code(code: str, points: int, credits: int, limit: int):
    with closing(_connect()) as conn, conn:
        conn.execute(
            """
            INSERT INTO redeem_codes (code, points, credits, code_limit, used_count)
            VALUES (?, ?, ?, ?, 0)
            ON CONFLICT(code) DO UPDATE SET
                points=excluded.points,
                credits=excluded.credits,
                code_limit=excluded.code_limit
            """,
            (code.strip(), int(points), int(credits), int(limit)),
        )


def redeem_code(user_id: int, code: str) -> Tuple[bool, str]:
    code = code.strip()
    add_user(user_id)

    with closing(_connect()) as conn, conn:
        code_row = conn.execute("SELECT * FROM redeem_codes WHERE code = ?", (code,)).fetchone()
        if not code_row:
            return False, "Invalid code"

        already = conn.execute(
            "SELECT 1 FROM code_redeems WHERE user_id = ? AND code = ?", (int(user_id), code)
        ).fetchone()
        if already:
            return False, "Code already redeemed"

        if int(code_row["used_count"]) >= int(code_row["code_limit"]):
            return False, "Code limit reached"

        conn.execute("INSERT INTO code_redeems (user_id, code) VALUES (?, ?)", (int(user_id), code))
        conn.execute(
            "UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?",
            (code,),
        )
        conn.execute(
            "UPDATE users SET points = points + ?, credits = credits + ? WHERE user_id = ?",
            (int(code_row["points"]), int(code_row["credits"]), int(user_id)),
        )
        return True, "Code redeemed"


def log_action(user_id: int, action: str):
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (int(user_id), action[:255]))


def set_joined(user_id: int, joined: bool):
    add_user(user_id)
    with closing(_connect()) as conn, conn:
        conn.execute("UPDATE users SET joined = ? WHERE user_id = ?", (1 if joined else 0, int(user_id)))


def get_user_count() -> int:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        return int(row["c"]) if row else 0


def get_all_user_ids() -> List[int]:
    with closing(_connect()) as conn:
        rows = conn.execute("SELECT user_id FROM users").fetchall()
        return [int(r["user_id"]) for r in rows]


def ban_user(user_id: int):
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (int(user_id),))


def unban_user(user_id: int):
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM banned_users WHERE user_id = ?", (int(user_id),))


def is_banned(user_id: int) -> bool:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT 1 FROM banned_users WHERE user_id = ?", (int(user_id),)).fetchone()
        return bool(row)


def add_premium_user(user_id: int):
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT OR IGNORE INTO premium_users (user_id) VALUES (?)", (int(user_id),))


def remove_premium_user(user_id: int):
    with closing(_connect()) as conn, conn:
        conn.execute("DELETE FROM premium_users WHERE user_id = ?", (int(user_id),))


def is_premium_user(user_id: int) -> bool:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT 1 FROM premium_users WHERE user_id = ?", (int(user_id),)).fetchone()
        return bool(row)
