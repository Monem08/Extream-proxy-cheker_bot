from aiogram import types
from bot.loader import dp
from bot.services.scanner_service import run_scan
import aiohttp


@dp.callback_query_handler(lambda c: c.data == "live")
async def live_proxy(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()

    msg = await callback.message.answer("🌍 Fetching proxies...")

    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()

    proxies = text.split("\n")[:100]

    await msg.edit_text("🚀 Scanning live proxies...")

    results = await run_scan(proxies)

    alive = [p for p, ok in results if ok]

    await msg.edit_text(
        f"🌍 Live Scan Done\n\n🟢 Alive: {len(alive)}"
    )
