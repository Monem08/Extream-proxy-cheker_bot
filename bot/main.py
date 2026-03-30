import threading
import logging
import os

# 🤖 aiogram
from aiogram import executor
from bot.loader import dp, bot as tg_bot

# 🌐 web (keep alive)
from bot.web import app

# 🔥 IMPORT HANDLERS
import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner
import bot.handlers.live
import bot.handlers.owner
import bot.handlers.upload
import bot.handlers.info


# 🔧 Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# 🌐 RUN WEB SERVER (SAFE)
def run_web():
    try:
        port = int(os.environ.get("PORT", 10000))  # ✅ Render dynamic port
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False  # 💀 VERY IMPORTANT
        )
    except Exception as e:
        print(f"🌐 Web error: {e}")


# 🚀 STARTUP
async def on_startup(dp):
    print("🤖 Bot started successfully!")
    print("🌍 Web server running")

    try:
        # 💀 RESET TELEGRAM STATE
        await tg_bot.delete_webhook(drop_pending_updates=True)

        # ❌ REMOVE THIS (CAUSE BUG)
        # await tg_bot.get_updates(offset=-1)

    except Exception as e:
        print("Startup error:", e)


# 🛑 SHUTDOWN
async def on_shutdown(dp):
    print("🛑 Bot stopped!")


# 🚀 MAIN RUN
if __name__ == "__main__":

    # 🌐 start web server (thread)
    threading.Thread(target=run_web, daemon=True).start()

    try:
        # 🤖 start polling (ONLY ONE INSTANCE)
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
    except Exception as e:
        print("💀 BOT CRASH:", e)
