user_messages = {}

def save_message(user_id, message_id):
    user_messages[user_id] = message_id

def get_message(user_id):
    return user_messages.get(user_id)

def delete_message(user_id):
    if user_id in user_messages:
        del user_messages[user_id]
