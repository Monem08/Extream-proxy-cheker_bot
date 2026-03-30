import logging
import threading
import os

from aiogram import executor
from bot.loader import dp, bot as tg_bot

# 🌐 web
from bot.web import app

# 🔥 handlers
import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner
import bot.handlers.live
import bot.handlers.owner
import bot.handlers.upload
import bot.handlers.info


# 🔧 logging
logging.basicConfig(level=logging.INFO)


# 🌐 run web (IMPORTANT)
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


# 🚀 startup
async def on_startup(dp):
    print("🤖 Bot started")

    try:
        await tg_bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(e)


# 🚀 main
if __name__ == "__main__":

    # 🌐 web thread (MUST for Render)
    threading.Thread(target=run_web, daemon=True).start()

    # 🤖 bot
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
