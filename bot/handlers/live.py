from aiogram import types
from bot.loader import dp
from bot.services.live_proxy_service import fetch_proxies
from bot.services.scanner_service import run_scan
from bot.keyboards.cancel_kb import cancel_kb

# 🔥 SECURITY
from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.config import OWNER_ID


@dp.callback_query_handler(lambda c: c.data == "live")
async def live_proxy(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # 👑 OWNER BYPASS
    if user_id != OWNER_ID:

        if is_spamming(user_id):
            banned = add_strike(user_id)
            if banned:
                await callback.message.answer("🚫 You are banned for spam")
            else:
                await callback.message.answer("⚠️ Stop spamming!")
            return

        if not is_allowed(user_id):
            await callback.answer("⏳ Slow down bro...", show_alert=True)
            return

    await callback.answer()

    try:
        await callback.message.delete()
    except:
        pass

    msg = await callback.message.answer("🌍 Fetching proxies...")

    try:
        proxies = await fetch_proxies()

        if not proxies:
            await msg.edit_text("❌ Failed to fetch proxies", reply_markup=cancel_kb())
            return

        results = await run_scan(proxies[:50])

        # 💀 FIXED FORMAT
        alive = [(p, s) for p, ok, s in results if ok and s is not None]
        fast = [p for p, s in alive if s < 1000]

        text = "🌍 Live Proxies\n\n"

        if not fast:
            text += "❌ No fast proxies"
        else:
            text += f"⚡ Fast Alive: {len(fast)}\n\n"
            text += "\n".join(fast[:10])

        await msg.edit_text(text, reply_markup=cancel_kb())

    except Exception as e:
        print("LIVE ERROR:", e)
        await msg.edit_text("❌ Error while fetching proxies")
