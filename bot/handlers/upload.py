from aiogram import types
from bot.loader import dp
from bot.services.scanner_service import run_scan
from bot.keyboards.cancel_kb import cancel_kb


@dp.callback_query_handler(lambda c: c.data == "upload")
async def upload_proxy(callback: types.CallbackQuery):
    await callback.answer()

    await callback.message.delete()

    await callback.message.answer(
        "📂 Send .txt file with proxies",
        reply_markup=cancel_kb()
    )


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_file(message: types.Message):
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
        f"✅ Done\n\n🟢 Alive: {len(alive)}\n🔴 Dead: {len(dead)}"
    )
