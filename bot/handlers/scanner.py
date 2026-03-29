from aiogram import types
from aiogram.types import InputFile
from bot.loader import dp
from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import cancel_task
from bot.services.message_manager import delete_message
from bot.services.ban_service import is_banned

# 🔥 NEW IMPORT
from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike

import tempfile


@dp.message_handler(lambda m: ":" in m.text and not m.text.startswith("/"))
async def scan_proxies(message: types.Message):
    user_id = message.from_user.id

    # 🚫 BAN CHECK
    if is_banned(user_id):
        await message.answer("🚫 You are banned")
        return

    # 💀 ANTI-SPAM SYSTEM
    if is_spamming(user_id):
        banned = add_strike(user_id)
        if banned:
            await message.answer("🚫 You are banned for spam")
        else:
            await message.answer("⚠️ Stop spamming!")
        return

    # ⏱ RATE LIMIT
    if not is_allowed(user_id):
        await message.answer("⏳ Slow down bro...")
        return

    # ❌ STATE CHECK
    if get_state(user_id) != "WAITING_PROXY":
        await message.answer("❌ Invalid action")
        return

    # 💀 DELETE OLD UI
    await delete_message(user_id)

    # ✅ CLEAN PROXY LIST
    proxies = [p.strip() for p in message.text.split("\n") if ":" in p]

    msg = await message.answer("🚀 Scanning...")

    # ⚡ SCAN
    results = await run_scan(proxies)

    # ✅ PROCESS
    alive = [(p, s) for p, ok, s in results if ok and s is not None]
    fast = [p for p, s in alive if s < 1000]
    dead = [p for p, ok, s in results if not ok]

    # 📊 RESULT
    await msg.edit_text(
        f"✅ Scan Complete\n\n🟢 Alive: {len(fast)}\n🔴 Dead: {len(dead)}"
    )

    # 📤 SEND FILE
    if fast:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("\n".join(fast))
            file_name = f.name

        await message.answer_document(
            InputFile(file_name),
            caption="🟢 Alive proxies list"
        )

    # 🔄 RESET
    reset_state(user_id)
    cancel_task(user_id)
