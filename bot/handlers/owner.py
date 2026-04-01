import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.loader import dp

from bot.services.role_service import get_role, is_owner
from bot.services.maintenance_service import set_maintenance, is_maintenance
from bot.services.admin_storage import (
    get_totals,
    ban_user,
    unban_user,
    add_premium,
    remove_premium,
    get_all_users,
)

from bot.services.message_manager import edit_or_send
from bot.keyboards.main_menu import main_menu

from bot.services.redeem_service import redeem, create_redeem_code
from bot.services.group_service import add_force_group, remove_force_group, get_force_groups

logger = logging.getLogger(__name__)


def owner_panel_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Stats", callback_data="owner:stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="owner:broadcast"),
    )
    kb.add(
        InlineKeyboardButton("🚫 Ban", callback_data="owner:ban"),
        InlineKeyboardButton("💎 Premium", callback_data="owner:premium"),
    )
    kb.add(InlineKeyboardButton("⚙️ Maintenance", callback_data="owner:maintenance"))
    kb.add(InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel"))
    return kb


def owner_panel_text():
    totals = get_totals()
    return (
        "👑 Owner Panel\n\n"
        f"👥 Users: {totals['total_users']}\n"
        f"⚡ Scans: {totals['total_scans']}\n\n"
        "🛠 Commands\n"
        "/broadcast, /ban, /unban\n"
        "/addpremium, /removepremium"
    )


async def handle_owner_action(callback: types.CallbackQuery, action: str):
    user_id = callback.from_user.id
    try:
        role = get_role(user_id)
        if role != "owner":
            await callback.answer("❌ Access denied", show_alert=True)
            return

        if action == "panel":
            await edit_or_send(user_id, callback.message, owner_panel_text(), owner_panel_kb())
            return

        if action in {"stats", "broadcast", "ban", "premium"}:
            action_text = {
                "stats": owner_panel_text(),
                "broadcast": "📢 Use: /broadcast <message>",
                "ban": "🚫 Use: /ban <id> or /unban <id>",
                "premium": "💎 Use: /addpremium <id> or /removepremium <id>",
            }
            await edit_or_send(user_id, callback.message, action_text[action], owner_panel_kb())
            return

        if action == "maintenance":
            new_state = not is_maintenance()
            set_maintenance(new_state)
            status = "ON 🔒" if new_state else "OFF ✅"
            await edit_or_send(user_id, callback.message, f"⚙️ Maintenance: {status}", main_menu(role))
            return

        await callback.answer("⚠️ Invalid action", show_alert=True)
    except Exception:
        logger.exception("Owner callback failed for user %s", user_id)
        if callback.message:
            await edit_or_send(user_id, callback.message, "⚠️ Owner action failed")


@dp.message_handler(commands=["broadcast"])
async def cmd_broadcast(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        payload = message.get_args().strip()
        if not payload:
            await edit_or_send(user_id, message, "Usage: /broadcast <message>")
            return

        sent = 0
        for uid in get_all_users():
            try:
                await message.bot.send_message(uid, payload)
                sent += 1
            except Exception:
                pass

        await edit_or_send(user_id, message, f"✅ Broadcast sent to {sent} users")
    except Exception:
        logger.exception("cmd_broadcast failed")


@dp.message_handler(commands=["ban"])
async def cmd_ban(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        arg = message.get_args().strip()
        if not arg.isdigit():
            await edit_or_send(user_id, message, "Usage: /ban <user_id>")
            return

        ban_user(int(arg))
        await edit_or_send(user_id, message, "✅ User banned")
    except Exception:
        logger.exception("cmd_ban failed")


@dp.message_handler(commands=["unban"])
async def cmd_unban(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        arg = message.get_args().strip()
        if not arg.isdigit():
            await edit_or_send(user_id, message, "Usage: /unban <user_id>")
            return

        unban_user(int(arg))
        await edit_or_send(user_id, message, "✅ User unbanned")
    except Exception:
        logger.exception("cmd_unban failed")


@dp.message_handler(commands=["addpremium"])
async def cmd_add_premium(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        arg = message.get_args().strip()
        if not arg.isdigit():
            await edit_or_send(user_id, message, "Usage: /addpremium <user_id>")
            return

        add_premium(int(arg))
        await edit_or_send(user_id, message, "✅ Premium added")
    except Exception:
        logger.exception("cmd_add_premium failed")


@dp.message_handler(commands=["removepremium"])
async def cmd_remove_premium(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        arg = message.get_args().strip()
        if not arg.isdigit():
            await edit_or_send(user_id, message, "Usage: /removepremium <user_id>")
            return

        remove_premium(int(arg))
        await edit_or_send(user_id, message, "✅ Premium removed")
    except Exception:
        logger.exception("cmd_remove_premium failed")


@dp.message_handler(commands=["redeem"])
async def cmd_redeem(message: types.Message):
    try:
        user_id = message.from_user.id
        code = message.get_args().strip()
        if not code:
            await edit_or_send(user_id, message, "Usage: /redeem <code>")
            return

        ok, text = await redeem(user_id, code)
        await edit_or_send(user_id, message, "✅ " + text if ok else f"❌ {text}")
    except Exception:
        logger.exception("cmd_redeem failed")


@dp.message_handler(commands=["createcode"])
async def cmd_create_code(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        parts = message.get_args().split()
        if len(parts) != 4:
            await edit_or_send(user_id, message, "Usage: /createcode <code> <points> <credits> <limit>")
            return

        code, points, credits, limit = parts
        if not (points.lstrip("-").isdigit() and credits.lstrip("-").isdigit() and limit.isdigit()):
            await edit_or_send(user_id, message, "❌ Invalid numbers")
            return

        await create_redeem_code(code, int(points), int(credits), int(limit))
        await edit_or_send(user_id, message, "✅ Code created")
    except Exception:
        logger.exception("cmd_create_code failed")


@dp.message_handler(commands=["addgroup"])
async def cmd_add_group(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        arg = message.get_args().strip()
        if not arg.lstrip("-").isdigit():
            await edit_or_send(user_id, message, "Usage: /addgroup <group_id>")
            return

        await add_force_group(int(arg))
        await edit_or_send(user_id, message, "✅ Force group added")
    except Exception:
        logger.exception("cmd_add_group failed")


@dp.message_handler(commands=["removegroup"])
async def cmd_remove_group(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        arg = message.get_args().strip()
        if not arg.lstrip("-").isdigit():
            await edit_or_send(user_id, message, "Usage: /removegroup <group_id>")
            return

        await remove_force_group(int(arg))
        await edit_or_send(user_id, message, "✅ Force group removed")
    except Exception:
        logger.exception("cmd_remove_group failed")


@dp.message_handler(commands=["groups"])
async def cmd_groups(message: types.Message):
    try:
        user_id = message.from_user.id
        if not is_owner(user_id):
            await edit_or_send(user_id, message, "❌ Access Denied")
            return

        groups = await get_force_groups()
        if not groups:
            await edit_or_send(user_id, message, "No force groups set.")
            return

        await edit_or_send(user_id, message, "Force groups:\n" + "\n".join(str(g) for g in groups))
    except Exception:
        logger.exception("cmd_groups failed")
