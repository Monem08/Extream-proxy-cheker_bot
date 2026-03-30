import logging

# 🤖 aiogram
from aiogram import executor
from bot.loader import dp, bot as tg_bot

# 🔥 IMPORT HANDLERS (IMPORTANT)
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


# 🚀 STARTUP
async def on_startup(dp):
    print("🤖 Bot started successfully!")

    try:
        # 💀 RESET TELEGRAM STATE (IMPORTANT)
        await tg_bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print("Startup error:", e)


# 🛑 SHUTDOWN
async def on_shutdown(dp):
    print("🛑 Bot stopped!")


# 🚀 MAIN RUN
if __name__ == "__main__":
    try:
        executor.start_polling(
            dp,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
    except Exception as e:
        print("💀 BOT CRASH:", e)
