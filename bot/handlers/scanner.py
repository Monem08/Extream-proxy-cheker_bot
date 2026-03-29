from aiogram import types
from aiogram.types import InputFile
from bot.loader import dp

from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import cancel_task
from bot.services.message_manager import delete_message
from bot.services.ban_service import is_banned

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role

import tempfile


@dp.message_handler(lambda m: ":" in m.text and not m.text.startswith("/"))
async def scan_proxies(message: types.Message):
    user_id = message.from_user.id

    # 🚫 BAN
    if is_banned(user_id):
        await message.answer("🚫 You are banned")
        return

    # 💀 MAINTENANCE
    role = get_role(user_id)
    if is_maintenance() and role not in ["owner", "admin"]:
        await message.answer("🚧 Bot Under Maintenance\n⏳ Try later")
        return

    # 💀 ANTI-SPAM
    if is_spamming(user_id):
        banned = add_strike(user_id)
        await message.answer("🚫 You are banned" if banned else "⚠️ Stop spamming!")
        return

    # ⏱ RATE LIMIT
    if not is_allowed(user_id):
        await message.answer("⏳ Slow down bro...")
        return

    # ❌ STATE
    if get_state(user_id) != "WAITING_PROXY":
        await message.answer("❌ Invalid action")
        return

    await delete_message(user_id)

    proxies = [p.strip() for p in message.text.split("\n") if ":" in p]

    msg = await message.answer("🚀 Scanning...")

    results = await run_scan(proxies)

    alive = [(p, s) for p, ok, s in results if ok and s]
    fast = [p for p, s in alive if s < 1000]
    dead = [p for p, ok, s in results if not ok]

    await msg.edit_text(f"✅ Done\n🟢 {len(fast)}\n🔴 {len(dead)}")

    if fast:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("\n".join(fast))
            file_name = f.name

        await message.answer_document(InputFile(file_name))

    reset_state(user_id)
    cancel_task(user_id)
