import threading
import logging

# 🤖 aiogram
from aiogram import executor
from bot.loader import dp, bot as tg_bot

# 🌐 web (cron / keep alive)
from bot.web import app

# 🔥 IMPORT HANDLERS (IMPORTANT)
import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner
import bot.handlers.live
import bot.handlers.owner


# 🔧 Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# 🌐 RUN WEB SERVER (SAFE)
def run_web():
    try:
        app.run(
            host="0.0.0.0",
            port=10000,
            debug=False,
            use_reloader=False  # 💀 IMPORTANT (avoid double run)
        )
    except Exception as e:
        print(f"🌐 Web error: {e}")


# 🚀 STARTUP
async def on_startup(dp):
    print("🤖 Bot started successfully!")
    print("🌍 Web server running")

    try:
        # 💀 FULL TELEGRAM RESET (IMPORTANT)
        await tg_bot.delete_webhook(drop_pending_updates=True)
        await tg_bot.get_updates(offset=-1)
    except Exception as e:
        print("Webhook error:", e)


# 🛑 SHUTDOWN
async def on_shutdown(dp):
    print("🛑 Bot stopped!")


# 🚀 MAIN RUN
if __name__ == "__main__":
    # 🌐 start web in background
    threading.Thread(target=run_web, daemon=True).start()

    try:
        # 🤖 start bot polling
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
    except Exception as e:
        print("💀 BOT CRASH:", e)
