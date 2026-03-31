from aiogram import types
from aiogram.types import InputFile
from bot.loader import dp

from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import cancel_task
from bot.services.message_manager import delete_message, save_message
from bot.services.ban_service import is_banned

from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.services.maintenance_service import is_maintenance
from bot.services.role_service import get_role

from bot.keyboards.cancel_kb import cancel_kb
from bot.services.admin_storage import increment_scans
from bot.database.db import log_action

import tempfile


# 💀 SAFE FILTER (ONLY WORK WHEN WAITING)
@dp.message_handler(lambda m: m.text and ":" in m.text, state="*")
async def scan_proxies(message: types.Message):
    user_id = message.from_user.id

    # 🚫 BAN
    if is_banned(user_id):
        msg = await message.answer("🚫 You are banned")
        await save_message(user_id, msg)
        return

    # 🚧 MAINTENANCE
    role = get_role(user_id)
    if is_maintenance() and role != "owner":
        msg = await message.answer("🚧 Bot Under Maintenance\n⏳ Try later")
        await save_message(user_id, msg)
        return

    # 💀 ANTI-SPAM
    if is_spamming(user_id):
        banned = add_strike(user_id)
        msg = await message.answer(
            "🚫 You are banned" if banned else "⚠️ Stop spamming!"
        )
        await save_message(user_id, msg)
        return

    # ⏱ RATE LIMIT
    if not is_allowed(user_id):
        await message.answer("⏳ Slow down bro...")
        return

    # ❌ STATE CHECK (IMPORTANT FIX 💀)
    if get_state(user_id) != "WAITING_PROXY":
        return  # silent ignore (no spam reply)

    # 💀 DELETE OLD UI
    await delete_message(user_id)

    # ✅ CLEAN PROXY LIST
    proxies = [p.strip() for p in message.text.split("\n") if ":" in p]

    if not proxies:
        msg = await message.answer("❌ No valid proxies found", reply_markup=cancel_kb())
        await save_message(user_id, msg)
        return

    # 🚀 SCAN START
    msg = await message.answer("🚀 Scanning...", reply_markup=cancel_kb())
    await save_message(user_id, msg)

    try:
        results = await run_scan(proxies)
        increment_scans()
        await log_action(user_id, "scan_proxies")

        alive = [(p, s) for p, ok, s in results if ok and s]
        fast = [p for p, s in alive if s < 1000]
        dead = [p for p, ok, s in results if not ok]

        result_msg = await msg.edit_text(
            f"""✅ Scan Complete

🟢 Alive: {len(fast)}
🔴 Dead: {len(dead)}""",
            reply_markup=cancel_kb()
        )

        await save_message(user_id, result_msg)

        # 📤 SEND FILE
        if fast:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
                f.write("\n".join(fast))
                file_name = f.name

            file_msg = await message.answer_document(
                InputFile(file_name),
                caption="🟢 Alive proxies list",
                reply_markup=cancel_kb()
            )

            await save_message(user_id, file_msg)

    except Exception as e:
        print("SCAN ERROR:", e)

        err = await message.answer("⚠️ Scan failed", reply_markup=cancel_kb())
        await save_message(user_id, err)

    # 🔄 RESET
    reset_state(user_id)
    cancel_task(user_id)
