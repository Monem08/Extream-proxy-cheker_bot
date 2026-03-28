from aiogram import types
from bot.loader import dp
from bot.services.scanner_service import run_scan


@dp.message_handler(lambda m: ":" in m.text)
async def scan_proxies(message: types.Message):
    proxies = message.text.split("\n")

    msg = await message.answer("🚀 Scanning...")

    results = await run_scan(proxies)

    alive = [p for p, ok in results if ok]
    dead = [p for p, ok in results if not ok]

    text = f"""
✅ Scan Complete

🟢 Alive: {len(alive)}
🔴 Dead: {len(dead)}
"""

    await msg.edit_text(text)
