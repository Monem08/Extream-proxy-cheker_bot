from aiogram import executor
from bot.loader import dp
import bot.handlers.start
import bot.handlers.menu
import bot.handlers.scanner

from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive 😈"


def run_bot():
    executor.start_polling(dp, skip_updates=True)


def start_bot():
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)


if __name__ == "__main__":
    start_bot()
