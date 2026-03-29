import threading
import logging

# 🤖 aiogram
from aiogram import executor
from bot.loader import dp

# 🌐 web (cron)
from bot.web import app

# 🔥 IMPORT HANDLERS (VERY IMPORTANT)
import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner


# 🔧 Logging
logging.basicConfig(level=logging.ERROR)


# 🌐 run web server
def run_web():
    app.run(host="0.0.0.0", port=10000)


# 🚀 startup
async def on_startup(dp):
    print("🤖 Bot started successfully!")
    print("🌍 Web server running (cron ready)")


# 🛑 shutdown
async def on_shutdown(dp):
    print("🛑 Bot stopped!")


if __name__ == "__main__":
    # 🌐 start web in background
    threading.Thread(target=run_web, daemon=True).start()

    # 🤖 start bot
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
