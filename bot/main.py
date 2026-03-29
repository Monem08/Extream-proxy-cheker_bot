import threading
import logging
import os

from aiogram import executor
from bot.loader import dp, bot as tg_bot
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
    try:
        app.run(
            host="0.0.0.0",
            port=10000,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        print(f"🌐 Web error: {e}")


async def on_startup(dp):
    print("🤖 Bot started successfully!")
    print("🌍 Web server running")

    try:
        await tg_bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print("Webhook error:", e)


async def on_shutdown(dp):
    print("🛑 Bot stopped!")


if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()

    try:
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
    except Exception as e:
        print("💀 BOT CRASH:", e)
