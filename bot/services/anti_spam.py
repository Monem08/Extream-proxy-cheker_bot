import time

spam_tracker = {}

# max 5 request in 5 sec
LIMIT = 5
WINDOW = 5


def is_spamming(user_id):
    now = time.time()

    if user_id not in spam_tracker:
        spam_tracker[user_id] = []

    spam_tracker[user_id].append(now)

    # remove old
    spam_tracker[user_id] = [
        t for t in spam_tracker[user_id] if now - t < WINDOW
    ]

    if len(spam_tracker[user_id]) > LIMIT:
        return True

    return False
