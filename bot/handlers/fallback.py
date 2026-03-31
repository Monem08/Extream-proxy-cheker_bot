from aiogram import types
from bot.loader import dp

from bot.handlers.menu import handle_menu_action
from bot.handlers.live import handle_live_action
from bot.handlers.owner import handle_owner_action
from bot.handlers.info import handle_info_action


@dp.callback_query_handler()
async def callback_router(callback: types.CallbackQuery):
    try:
        raw = callback.data or ""
        parts = raw.split(":")
        if len(parts) < 2:
            await callback.answer("⚠️ Invalid action", show_alert=True)
            return

        module, action = parts[0], parts[1]
        optional_data = parts[2] if len(parts) > 2 else None

        if module == "menu":
            if action == "info":
                await handle_info_action(callback)
            else:
                await handle_menu_action(callback, action, optional_data)
        elif module == "scan":
            if action == "start":
                await handle_menu_action(callback, "scan_start")
            elif action == "stop":
                await handle_menu_action(callback, "cancel")
            else:
                await callback.answer("⚠️ Invalid action", show_alert=True)
                return
        elif module == "proxy":
            if action == "upload":
                await handle_menu_action(callback, "upload")
            elif action == "live":
                await handle_live_action(callback)
            else:
                await callback.answer("⚠️ Invalid action", show_alert=True)
                return
        elif module == "owner":
            await handle_owner_action(callback, action)
        else:
            await callback.answer("⚠️ Invalid action", show_alert=True)
            return

        await callback.answer()
    except Exception:
        await callback.answer("⚠️ Unexpected error", show_alert=True)
