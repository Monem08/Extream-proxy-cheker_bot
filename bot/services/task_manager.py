active_tasks = {}

def start_task(user_id, task_name):
    active_tasks[user_id] = task_name

def get_task(user_id):
    return active_tasks.get(user_id)

def cancel_task(user_id):
    if user_id in active_tasks:
        del active_tasks[user_id]
        return True
    return False
