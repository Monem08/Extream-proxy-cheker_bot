from aiogram import types
from bot.loader import dp

from bot.services.live_proxy_service import fetch_proxies
from bot.services.scanner_service import run_scan
from bot.keyboards.cancel_kb import cancel_kb

from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role

# 💀 NEW
from bot.services.message_manager import delete_message, save_message
from bot.services.ban_service import is_banned
from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike


@dp.callback_query_handler(lambda c: c.data == "live")
async def live_proxy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    # 🚫 BAN
    if is_banned(user_id):
        msg = await callback.message.answer("🚫 You are banned")
        await save_message(user_id, msg)
        return

    # 🚧 MAINTENANCE
    if is_maintenance() and role not in ["owner", "admin"]:
        await callback.answer("🚧 Bot Under Maintenance", show_alert=True)
        return

    # 💀 ANTI-SPAM
    if is_spamming(user_id):
        banned = add_strike(user_id)
        msg = await callback.message.answer(
            "🚫 You are banned" if banned else "⚠️ Stop spamming!"
        )
        await save_message(user_id, msg)
        return

    # ⏱ RATE LIMIT
    if not is_allowed(user_id):
        await callback.answer("⏳ Slow down bro...", show_alert=True)
        return

    await callback.answer()

    # 💀 DELETE OLD UI
    await delete_message(user_id)

    try:
        await callback.message.delete()
    except:
        pass

    # 🌍 FETCH START
    msg = await callback.message.answer("🌍 Fetching proxies...", reply_markup=cancel_kb())
    await save_message(user_id, msg)

    try:
        proxies = await fetch_proxies()

        if not proxies:
            fail_msg = await msg.edit_text(
                "❌ Failed to fetch proxies",
                reply_markup=cancel_kb()
            )
            await save_message(user_id, fail_msg)
            return

        # ⚡ LIMIT + SCAN
        results = await run_scan(proxies[:50])

        alive = [p for p, ok in results if ok]

        if not alive:
            text = "❌ No alive proxies"
        else:
            text = f"""🌍 Live Proxies

🟢 Alive: {len(alive)}

""" + "\n".join(alive[:10])

        result_msg = await msg.edit_text(
            text,
            reply_markup=cancel_kb()
        )

        await save_message(user_id, result_msg)

    except Exception as e:
        print("LIVE ERROR:", e)

        err = await callback.message.answer(
            "⚠️ Live proxy fetch failed",
            reply_markup=cancel_kb()
        )
        await save_message(user_id, err)
