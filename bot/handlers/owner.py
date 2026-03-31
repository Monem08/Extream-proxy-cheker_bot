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


@dp.message_handler(commands=["broadcast"])
async def cmd_broadcast(message: types.Message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        await message.answer("❌ Access Denied")
        return

    payload = message.get_args().strip()
    if not payload:
        await message.answer("Usage: /broadcast <message>")
        return

    sent = 0
    for uid in get_all_users():
        try:
            await message.bot.send_message(uid, payload)
            sent += 1
        except Exception:
            pass

    await message.answer(f"✅ Broadcast sent to {sent} users")


@dp.message_handler(commands=["ban"])
async def cmd_ban(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    arg = message.get_args().strip()
    if not arg.isdigit():
        await message.answer("Usage: /ban <user_id>")
        return

    ban_user(int(arg))
    await message.answer("✅ User banned")


@dp.message_handler(commands=["unban"])
async def cmd_unban(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    arg = message.get_args().strip()
    if not arg.isdigit():
        await message.answer("Usage: /unban <user_id>")
        return

    unban_user(int(arg))
    await message.answer("✅ User unbanned")


@dp.message_handler(commands=["addpremium"])
async def cmd_add_premium(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    arg = message.get_args().strip()
    if not arg.isdigit():
        await message.answer("Usage: /addpremium <user_id>")
        return

    add_premium(int(arg))
    await message.answer("✅ Premium added")


@dp.message_handler(commands=["removepremium"])
async def cmd_remove_premium(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    arg = message.get_args().strip()
    if not arg.isdigit():
        await message.answer("Usage: /removepremium <user_id>")
        return

    remove_premium(int(arg))
    await message.answer("✅ Premium removed")


@dp.message_handler(commands=["redeem"])
async def cmd_redeem(message: types.Message):
    code = message.get_args().strip()
    if not code:
        await message.answer("Usage: /redeem <code>")
        return

    ok, text = await redeem(message.from_user.id, code)
    await message.answer("✅ " + text if ok else f"❌ {text}")


@dp.message_handler(commands=["createcode"])
async def cmd_create_code(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    parts = message.get_args().split()
    if len(parts) != 4:
        await message.answer("Usage: /createcode <code> <points> <credits> <limit>")
        return

    code, points, credits, limit = parts
    if not (points.lstrip("-").isdigit() and credits.lstrip("-").isdigit() and limit.isdigit()):
        await message.answer("❌ Invalid numbers")
        return

    await create_redeem_code(code, int(points), int(credits), int(limit))
    await message.answer("✅ Code created")


@dp.message_handler(commands=["addgroup"])
async def cmd_add_group(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    arg = message.get_args().strip()
    if not arg.lstrip("-").isdigit():
        await message.answer("Usage: /addgroup <group_id>")
        return

    await add_force_group(int(arg))
    await message.answer("✅ Force group added")


@dp.message_handler(commands=["removegroup"])
async def cmd_remove_group(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    arg = message.get_args().strip()
    if not arg.lstrip("-").isdigit():
        await message.answer("Usage: /removegroup <group_id>")
        return

    await remove_force_group(int(arg))
    await message.answer("✅ Force group removed")


@dp.message_handler(commands=["groups"])
async def cmd_groups(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

    groups = await get_force_groups()
    if not groups:
        await message.answer("No force groups set.")
        return

    await message.answer("Force groups:\n" + "\n".join(str(g) for g in groups))
