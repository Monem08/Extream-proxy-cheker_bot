import logging
from typing import Callable, Dict

from aiogram import types

from bot.loader import dp
from bot.handlers.menu import handle_menu_action
from bot.handlers.live import handle_live_action
from bot.handlers.owner import handle_owner_action
from bot.handlers.info import handle_info_action

logger = logging.getLogger(__name__)

_ALLOWED: Dict[str, set[str]] = {
    "menu": {"home", "menu", "settings", "verify_join", "cancel", "info"},
    "scan": {"start", "stop"},
    "proxy": {"upload", "live"},
    "owner": {"panel", "stats", "broadcast", "ban", "premium", "maintenance"},
}


async def _safe_answer(callback: types.CallbackQuery, text: str, alert: bool = True) -> None:
    try:
        await callback.answer(text, show_alert=alert)
    except Exception:
        logger.debug("Failed callback answer")


@dp.callback_query_handler()
async def callback_router(callback: types.CallbackQuery):
    try:
        raw = (callback.data or "").strip()
        if not raw or ":" not in raw:
            await _safe_answer(callback, "⚠️ Invalid action")
            return

        module, action, *rest = raw.split(":")
        if module not in _ALLOWED or action not in _ALLOWED[module]:
            await _safe_answer(callback, "⚠️ Unknown action")
            return

        extra = rest[0] if rest else None

        if module == "menu":
            if action == "info":
                await handle_info_action(callback)
            else:
                await handle_menu_action(callback, action, extra)
        elif module == "scan":
            await handle_menu_action(callback, "scan_start" if action == "start" else "cancel")
        elif module == "proxy":
            if action == "upload":
                await handle_menu_action(callback, "upload")
            else:
                await handle_live_action(callback)
        elif module == "owner":
            await handle_owner_action(callback, action)

        await callback.answer()
    except Exception:
        logger.exception("Callback router crashed")
        await _safe_answer(callback, "⚠️ Unexpected error")
