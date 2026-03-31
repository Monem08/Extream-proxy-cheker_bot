from bot.database.db import (
    add_user,
    get_user,
    add_points,
    get_balance,
    get_user_count,
    get_all_user_ids,
    ban_user as db_ban_user,
    unban_user as db_unban_user,
    is_banned as db_is_banned,
    add_premium_user,
    remove_premium_user,
    is_premium_user,
)

# legacy JSON-backed lists kept as-is in ban_service/premium handlers elsewhere.
# this service now uses DB for users + scan stats counters.

_scan_total = 0


def register_user(user_id):
    add_user(int(user_id))


def increment_scans(count=1):
    global _scan_total
    _scan_total += int(count)


def get_totals():
    return {
        "total_users": get_user_count(),
        "total_scans": int(_scan_total),
    }


def ban_user(user_id):
    db_ban_user(int(user_id))


def unban_user(user_id):
    db_unban_user(int(user_id))


def is_banned(user_id):
    return db_is_banned(int(user_id))


def add_premium(user_id):
    add_premium_user(int(user_id))


def remove_premium(user_id):
    remove_premium_user(int(user_id))


def is_premium(user_id):
    return is_premium_user(int(user_id))


def get_all_users():
    return get_all_user_ids()
