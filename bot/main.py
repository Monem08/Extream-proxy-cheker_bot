import threading
import logging

from aiogram import executor
from bot.loader import dp, bot
from bot.web import app

import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner
import bot.handlers.live
import bot.handlers.owner


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_web():
    app.run(host="0.0.0.0", port=10000)


def start_web():
    try:
        run_web()
    except Exception as e:
        print(f"🌐 Web error: {e}")


async def on_startup(dp):
    print("🤖 Bot started successfully!")
    print("🌍 Web server running")

    await bot.delete_webhook(drop_pending_updates=True)


async def on_shutdown(dp):
    print("🛑 Bot stopped!")


if __name__ == "__main__":
    threading.Thread(target=start_web, daemon=True).start()

    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
