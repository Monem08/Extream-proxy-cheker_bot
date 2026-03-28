from aiogram import executor
from bot.loader import dp

import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner

def start_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    start_bot()
