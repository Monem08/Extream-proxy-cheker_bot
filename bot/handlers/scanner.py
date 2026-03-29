from aiogram import types
from aiogram.types import InputFile
from bot.loader import dp
from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import cancel_task
from bot.services.message_manager import delete_message
import tempfile


@dp.message_handler(lambda m: ":" in m.text)
async def scan_proxies(message: types.Message):
    user_id = message.from_user.id

    # ❌ block invalid action
    if get_state(user_id) != "WAITING_PROXY":
        await message.answer("❌ Invalid action")
        return

    # 💀 delete previous UI message
    delete_message(user_id)

    proxies = message.text.split("\n")

    msg = await message.answer("🚀 Scanning...")

    # ⚡ scan
    results = await run_scan(proxies)

    # ✅ process results (IMPORTANT FIX)
    alive = [(p, s) for p, ok, s in results if ok and s is not None]
    fast = [p for p, s in alive if s < 1000]
    dead = [p for p, ok, s in results if not ok]

    # ✅ summary (use FAST not alive)
    await msg.edit_text(
        f"✅ Scan Complete\n\n🟢 Alive: {len(fast)}\n🔴 Dead: {len(dead)}"
    )

    # 📤 create + send file
    if fast:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as f:
            f.write("\n".join(fast))  # ⚠️ FIX
            file_name = f.name

        await message.answer_document(
            InputFile(file_name),
            caption="🟢 Alive proxies list"
        )

    # 🔄 reset system
    reset_state(user_id)
    cancel_task(user_id)
