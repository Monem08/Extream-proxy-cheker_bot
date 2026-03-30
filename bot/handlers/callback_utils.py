from aiogram import types


async def safe_answer(callback: types.CallbackQuery, text: str = None, show_alert: bool = False) -> None:
    """Answer callback query safely to stop Telegram loading spinner."""
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except Exception:
        pass
