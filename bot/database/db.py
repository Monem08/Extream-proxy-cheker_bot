from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Tuple
import logging

import aiosqlite

from bot.config import OWNER_ID

import os as _os
DB_PATH = Path(_os.getenv("DATA_DIR", "bot/data")) / "database.db"
logger = logging.getLogger(__name__)


async def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    async with conn.execute("PRAGMA journal_mode=WAL;") as cursor:
        await cursor.fetchone()
    await conn.execute("PRAGMA synchronous=NORMAL;")
    await conn.execute("PRAGMA busy_timeout=5000;")
    await conn.execute("PRAGMA foreign_keys=ON;")
    return conn


async def _fetchone(conn: aiosqlite.Connection, query: str, params: tuple = ()):
    async with conn.execute(query, params) as cursor:
        return await cursor.fetchone()


async def _fetchall(conn: aiosqlite.Connection, query: str, params: tuple = ()):
    async with conn.execute(query, params) as cursor:
        return await cursor.fetchall()


async def fetchone(query: str, params: tuple = ()):
    async with _managed_connection() as conn:
        return await _fetchone(conn, query, params)


async def fetchall(query: str, params: tuple = ()):
    async with _managed_connection() as conn:
        return await _fetchall(conn, query, params)


@asynccontextmanager
async def _managed_connection():
    conn = await _connect()
    try:
        yield conn
    finally:
        await conn.close()


async def init_db():
    try:
        async with _managed_connection() as conn:
            await conn.execute(
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
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS referrals (
                    user_id INTEGER PRIMARY KEY,
                    referrer_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS force_groups (
                    group_id INTEGER PRIMARY KEY
                )
                """
            )
            await conn.execute(
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
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_codes (
                    user_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    PRIMARY KEY (user_id, code)
                )
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await conn.execute("CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY)")
            await conn.execute("CREATE TABLE IF NOT EXISTS premium_users (user_id INTEGER PRIMARY KEY)")
            await conn.commit()
    except Exception:
        logger.exception("Failed to initialize database")
        return


async def ensure_user(user_id: int):
    try:
        uid = int(user_id)
        role = "owner" if uid == int(OWNER_ID) else "user"
        async with _managed_connection() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, role)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO NOTHING
                """,
                (uid, role),
            )
            await conn.commit()
    except Exception:
        logger.exception("Failed to ensure user in database: %s", user_id)
        return


async def add_user(user_id: int):
    await ensure_user(user_id)


async def get_user(user_id: int) -> Optional[Dict]:
    try:
        await ensure_user(user_id)
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT * FROM users WHERE user_id = ?", (int(user_id),))
            return dict(row) if row else None
    except Exception:
        logger.exception("Failed to fetch user from database: %s", user_id)
        return None


async def add_points(user_id: int, amount: int):
    try:
        await ensure_user(user_id)
        async with _managed_connection() as conn:
            await conn.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (int(amount), int(user_id)))
            await conn.commit()
    except Exception:
        return


async def add_credits(user_id: int, amount: int):
    try:
        await ensure_user(user_id)
        async with _managed_connection() as conn:
            await conn.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (int(amount), int(user_id)))
            await conn.commit()
    except Exception:
        return


async def get_balance(user_id: int) -> Dict[str, int]:
    try:
        await ensure_user(user_id)
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT points, credits FROM users WHERE user_id = ?", (int(user_id),))
            if not row:
                return {"points": 0, "credits": 0}
            return {"points": int(row["points"]), "credits": int(row["credits"])}
    except Exception:
        logger.exception("Failed to fetch user balance: %s", user_id)
        return {"points": 0, "credits": 0}


async def save_referral(user_id: int, referrer_id: int):
    try:
        uid = int(user_id)
        rid = int(referrer_id)
        if uid == rid:
            return

        async with _managed_connection() as conn:
            exists = await _fetchone(conn, "SELECT 1 FROM referrals WHERE user_id = ?", (uid,))
            if exists:
                return

            await conn.execute(
                "INSERT INTO referrals (user_id, referrer_id, status) VALUES (?, ?, 'pending')",
                (uid, rid),
            )
            await conn.commit()
    except Exception:
        return


async def get_referral(user_id: int) -> Optional[Dict]:
    try:
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT * FROM referrals WHERE user_id = ?", (int(user_id),))
            return dict(row) if row else None
    except Exception:
        return None


async def complete_referral(user_id: int) -> Optional[int]:
    try:
        uid = int(user_id)
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT referrer_id, status FROM referrals WHERE user_id = ?", (uid,))
            if not row or row["status"] == "completed":
                return None

            referrer_id = int(row["referrer_id"])
            await conn.execute("UPDATE referrals SET status = 'completed' WHERE user_id = ?", (uid,))
            await conn.execute("UPDATE users SET points = points + 25 WHERE user_id = ?", (referrer_id,))
            await conn.commit()
            return referrer_id
    except Exception:
        return None


async def add_group(group_id: int):
    try:
        async with _managed_connection() as conn:
            await conn.execute("INSERT OR IGNORE INTO force_groups (group_id) VALUES (?)", (int(group_id),))
            await conn.commit()
    except Exception:
        return


async def remove_group(group_id: int):
    try:
        async with _managed_connection() as conn:
            await conn.execute("DELETE FROM force_groups WHERE group_id = ?", (int(group_id),))
            await conn.commit()
    except Exception:
        return


async def get_groups() -> List[int]:
    try:
        async with _managed_connection() as conn:
            rows = await _fetchall(conn, "SELECT group_id FROM force_groups")
            return [int(r["group_id"]) for r in rows]
    except Exception:
        return []


async def create_code(code: str, points: int, credits: int, limit: int):
    try:
        code = code.strip()
        async with _managed_connection() as conn:
            await conn.execute(
                """
                INSERT INTO redeem_codes (code, points, credits, code_limit, used_count)
                VALUES (?, ?, ?, ?, 0)
                ON CONFLICT(code) DO UPDATE SET
                    points=excluded.points,
                    credits=excluded.credits,
                    code_limit=excluded.code_limit
                """,
                (code, int(points), int(credits), int(limit)),
            )
            await conn.commit()
    except Exception:
        return


async def redeem_code(user_id: int, code: str) -> Tuple[bool, str]:
    try:
        code = code.strip()
        uid = int(user_id)
        await ensure_user(uid)

        async with _managed_connection() as conn:
            code_row = await _fetchone(conn, "SELECT * FROM redeem_codes WHERE code = ?", (code,))
            if not code_row:
                return False, "Invalid code"

            used = await _fetchone(conn, "SELECT 1 FROM user_codes WHERE user_id = ? AND code = ?", (uid, code))
            if used:
                return False, "Code already used"

            if int(code_row["used_count"]) >= int(code_row["code_limit"]):
                return False, "Code limit reached"

            await conn.execute("INSERT INTO user_codes (user_id, code) VALUES (?, ?)", (uid, code))
            await conn.execute("UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
            await conn.execute(
                "UPDATE users SET points = points + ?, credits = credits + ? WHERE user_id = ?",
                (int(code_row["points"]), int(code_row["credits"]), uid),
            )
            await conn.commit()
            return True, "Code redeemed"
    except Exception:
        logger.exception("Failed to redeem code for user %s", user_id)
        return False, "Database error"


async def log_action(user_id: int, action: str):
    try:
        async with _managed_connection() as conn:
            await conn.execute(
                "INSERT INTO logs (user_id, action) VALUES (?, ?)",
                (int(user_id), action[:255]),
            )
            await conn.commit()
    except Exception:
        return


async def set_joined(user_id: int, joined: bool):
    try:
        await ensure_user(user_id)
        async with _managed_connection() as conn:
            await conn.execute("UPDATE users SET joined = ? WHERE user_id = ?", (1 if joined else 0, int(user_id)))
            await conn.commit()
    except Exception:
        return


async def get_user_count() -> int:
    try:
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT COUNT(*) AS c FROM users")
            return int(row["c"]) if row else 0
    except Exception:
        return 0


async def get_all_user_ids() -> List[int]:
    try:
        async with _managed_connection() as conn:
            rows = await _fetchall(conn, "SELECT user_id FROM users")
            return [int(r["user_id"]) for r in rows]
    except Exception:
        return []


async def ban_user(user_id: int):
    try:
        async with _managed_connection() as conn:
            await conn.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (int(user_id),))
            await conn.commit()
    except Exception:
        return


async def unban_user(user_id: int):
    try:
        async with _managed_connection() as conn:
            await conn.execute("DELETE FROM banned_users WHERE user_id = ?", (int(user_id),))
            await conn.commit()
    except Exception:
        return


async def is_banned(user_id: int) -> bool:
    try:
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT 1 FROM banned_users WHERE user_id = ?", (int(user_id),))
            return bool(row)
    except Exception:
        return False


async def add_premium_user(user_id: int):
    try:
        async with _managed_connection() as conn:
            await conn.execute("INSERT OR IGNORE INTO premium_users (user_id) VALUES (?)", (int(user_id),))
            await conn.commit()
    except Exception:
        return


async def remove_premium_user(user_id: int):
    try:
        async with _managed_connection() as conn:
            await conn.execute("DELETE FROM premium_users WHERE user_id = ?", (int(user_id),))
            await conn.commit()
    except Exception:
        return


async def is_premium_user(user_id: int) -> bool:
    try:
        async with _managed_connection() as conn:
            row = await _fetchone(conn, "SELECT 1 FROM premium_users WHERE user_id = ?", (int(user_id),))
            return bool(row)
    except Exception:
        return False
