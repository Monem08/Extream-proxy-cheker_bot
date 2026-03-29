from aiogram import types
from bot.loader import dp

from bot.services.live_proxy_service import fetch_proxies
from bot.services.scanner_service import run_scan
from bot.keyboards.cancel_kb import cancel_kb

from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role


@dp.callback_query_handler(lambda c: c.data == "live")
async def live_proxy(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    role = get_role(user_id)

    # 💀 MAINTENANCE
    if is_maintenance() and role not in ["owner", "admin"]:
        await callback.answer("🚧 Bot Under Maintenance", show_alert=True)
        return

    await callback.answer()

    try:
        await callback.message.delete()
    except:
        pass

    msg = await callback.message.answer("🌍 Fetching...")

    proxies = await fetch_proxies()

    if not proxies:
        await msg.edit_text("❌ Failed", reply_markup=cancel_kb())
        return

    results = await run_scan(proxies[:50])

    alive = [p for p, ok in results if ok]

    text = f"🟢 Alive: {len(alive)}\n\n" + "\n".join(alive[:10]) if alive else "❌ None"

    await msg.edit_text(text, reply_markup=cancel_kb())
