def progress_bar(percent):
    total_blocks = 10
    filled_blocks = int(percent / 10)

    bar = "█" * filled_blocks + "░" * (total_blocks - filled_blocks)
    return f"{bar} {percent}%"
