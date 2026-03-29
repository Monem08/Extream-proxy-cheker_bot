import time

# store user request time
user_last_action = {}

# ⚡ cooldown seconds
COOLDOWN = 5


def is_allowed(user_id):
    now = time.time()

    if user_id in user_last_action:
        diff = now - user_last_action[user_id]

        if diff < COOLDOWN:
            return False

    user_last_action[user_id] = now
    return True
