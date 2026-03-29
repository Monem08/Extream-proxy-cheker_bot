import threading
import logging

# 🤖 aiogram
from aiogram import executor
from bot.loader import dp, bot as tg_bot  # 🔥 FIXED

# 🌐 web (cron)
from bot.web import app

# 🔥 IMPORT HANDLERS (IMPORTANT)
import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner
import bot.handlers.live
import bot.handlers.owner


# 🔧 Logging (clean)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# 🌐 run web server
def run_web():
    app.run(host="0.0.0.0", port=10000)


# 🔥 safe thread start
def start_web():
    try:
        run_web()
    except Exception as e:
        print(f"🌐 Web error: {e}")


# 🚀 startup
async def on_startup(dp):
    print("🤖 Bot started successfully!")
    print("🌍 Web server running")

    # 💀 FIXED (NO MORE ERROR)
    await tg_bot.delete_webhook(drop_pending_updates=True)


# 🛑 shutdown
async def on_shutdown(dp):
    print("🛑 Bot stopped!")


if __name__ == "__main__":
    # 🌐 start web server in background
    threading.Thread(target=start_web, daemon=True).start()

    # 🤖 start bot
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
