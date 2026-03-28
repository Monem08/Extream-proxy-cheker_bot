def progress_bar(percent):
    total = 10
    filled = int(total * percent / 100)
    return "█" * filled + "░" * (total - filled)
