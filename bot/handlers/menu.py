from aiogram import types
from bot.loader import dp
from bot.keyboards.main_menu import main_menu
from bot.services.message_manager import set_message

# 🔥 ADD THIS
from bot.services.rate_limiter import is_allowed
from bot.services.anti_spam import is_spamming
from bot.services.security_service import add_strike
from bot.config import OWNER_ID


@dp.callback_query_handler()
async def handle_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # 👑 OWNER BYPASS
    if user_id != OWNER_ID:

        # 🚫 anti spam
        if is_spamming(user_id):
            banned = add_strike(user_id)
            if banned:
                await callback.message.answer("🚫 You are banned for spam")
            else:
                await callback.message.answer("⚠️ Stop spamming!")
            return

        # ⏱ rate limit
        if not is_allowed(user_id):
            await callback.answer("⏳ Slow down bro...", show_alert=True)
            return

    data = callback.data

    try:
        await callback.message.delete()
    except:
        pass

    # 💀 MAIN MENU ROUTER
    if data == "menu":
        msg = await callback.message.answer(
            "🚀 Choose an option:",
            reply_markup=main_menu()
        )
        set_message(user_id, msg.message_id)

    elif data == "start_scan":
        msg = await callback.message.answer(
            "📂 Send proxy list (ip:port)"
        )
        set_message(user_id, msg.message_id)

    elif data == "upload":
        msg = await callback.message.answer(
            "📂 Send .txt file with proxies"
        )
        set_message(user_id, msg.message_id)

    elif data == "live":
        msg = await callback.message.answer(
            "🌍 Fetching proxies..."
        )
        set_message(user_id, msg.message_id)

    elif data == "settings":
        msg = await callback.message.answer(
            "⚙️ Settings coming soon..."
        )
        set_message(user_id, msg.message_id)

    elif data == "cancel":
        msg = await callback.message.answer(
            "🚀 Back to menu",
            reply_markup=main_menu()
        )
        set_message(user_id, msg.message_id)

    await callback.answer()
