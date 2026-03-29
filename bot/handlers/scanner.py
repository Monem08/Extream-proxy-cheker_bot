from aiogram import types
from bot.loader import dp
from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import cancel_task
from bot.services.message_manager import delete_message


@dp.message_handler(lambda m: ":" in m.text)
async def scan_proxies(message: types.Message):
    user_id = message.from_user.id

    # ❌ block invalid action
    if get_state(user_id) != "WAITING_PROXY":
        await message.answer("❌ Invalid action")
        return

    # 💀 delete previous "Send proxy list" message
    delete_message(user_id)

    proxies = message.text.split("\n")

    msg = await message.answer("🚀 Scanning...")

    results = await run_scan(proxies)

    alive = [p for p, ok in results if ok]
    dead = [p for p, ok in results if not ok]

    await msg.edit_text(
        f"✅ Scan Complete\n\n🟢 Alive: {len(alive)}\n🔴 Dead: {len(dead)}"
    )

    # reset system
    reset_state(user_id)
    cancel_task(user_id)
