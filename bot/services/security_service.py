from bot.services.ban_service import ban_user

# track spam count
user_strikes = {}


def add_strike(user_id):
    if user_id not in user_strikes:
        user_strikes[user_id] = 0

    user_strikes[user_id] += 1

    # 💀 3 strike = BAN
    if user_strikes[user_id] >= 3:
        ban_user(user_id)
        return True

    return False
