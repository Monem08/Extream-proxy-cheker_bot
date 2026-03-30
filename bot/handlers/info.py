from aiogram import types
from bot.loader import dp

from bot.services.role_service import get_role
from bot.services.admin_storage import get_totals

from bot.services.message_manager import delete_message, save_message
from bot.keyboards.cancel_kb import cancel_kb

from bot.handlers.callback_utils import safe_answer


@dp.callback_query_handler(lambda c: c.data == "info")
async def info_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    try:
        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        if role == "owner":
            totals = get_totals()
            text = f"""👑 OWNER PANEL

📊 Stats
👥 Users: {totals['total_users']}
⚡ Scans: {totals['total_scans']}

⚙️ Controls:
- /broadcast → send message to all users
- /ban <user_id> → ban user
- /unban <user_id> → unban user
- /addpremium <user_id> → give premium
- /removepremium <user_id> → remove premium"""
        else:
            text = """👤 USER PANEL

🚀 Proxy Scan
🌍 Live Proxies"""

        msg = await callback.message.answer(text, reply_markup=cancel_kb())
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to load info panel")
    finally:
        await safe_answer(callback)
