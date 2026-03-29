from aiogram import types
from bot.loader import dp
from bot.services.live_proxy_service import fetch_proxies
from bot.services.scanner_service import run_scan
from bot.keyboards.cancel_kb import cancel_kb


@dp.callback_query_handler(lambda c: c.data == "live")
async def live_proxy(callback: types.CallbackQuery):
    await callback.answer()

    try:
        await callback.message.delete()
    except:
        pass

    msg = await callback.message.answer("🌍 Fetching proxies...")

    proxies = await fetch_proxies()

    if not proxies:
        await msg.edit_text("❌ Failed to fetch proxies", reply_markup=cancel_kb())
        return

    results = await run_scan(proxies[:50])

    alive = [p for p, ok in results if ok]

    text = "🌍 Live Proxies\n\n"

    if not alive:
        text += "❌ No alive proxies"
    else:
        text += f"🟢 Alive: {len(alive)}\n\n"
        text += "\n".join(alive[:10])

    await msg.edit_text(text, reply_markup=cancel_kb())
