from aiogram import types
from bot.loader import dp
from bot.services.scanner_service import run_scan
from bot.states.user_state import get_state, reset_state
from bot.services.task_manager import cancel_task


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_file(message: types.Message):
    user_id = message.from_user.id

    # ❌ block if not in upload mode
    if get_state(user_id) != "WAITING_FILE":
        return

    file = await message.document.get_file()
    file_path = file.file_path

    downloaded = await message.bot.download_file(file_path)
    content = downloaded.read().decode()

    proxies = content.split("\n")

    msg = await message.answer("🚀 Scanning file...")

    results = await run_scan(proxies)

    alive = [p for p, ok in results if ok]
    dead = [p for p, ok in results if not ok]

    await msg.edit_text(
        f"✅ File Scan Complete\n\n🟢 Alive: {len(alive)}\n🔴 Dead: {len(dead)}"
    )

    # reset
    reset_state(user_id)
    cancel_task(user_id)
