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

main
from bot.services.message_manager import save_message, delete_message
from bot.
 
from bot.handlers.callback_utils import safe_answer
 


def owner_panel_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Stats", callback_data="owner_stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="owner_broadcast"),
    )
    kb.add(
        InlineKeyboardButton("🚫 Ban", callback_data="owner_ban"),
        InlineKeyboardButton("💎 Premium", callback_data="owner_premium"),
    )
    kb.add(InlineKeyboardButton("⚙️ Maintenance", callback_data="maintenance"))
    kb.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    return kb


def owner_panel_text():
    totals = get_totals()
    return f"""👑 OWNER PANEL

📊 Stats
👥 Users: {totals['total_users']}
⚡ Scans: {totals['t
        msg = await callback.message.answer(f"⚙️ Maintenance Mode: {status}", reply_markup=cancel_kb())
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to update maintenance mode")
    finally:
        await safe_answer(callback)


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

        if role not in ["owner", "admin"]:
            await safe_answer(callback, "❌ Not allowed", show_alert=True)
            return

        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        text = """👑 ADMIN PANEL
 main


@dp.message_handler(commands=["ban"])
async def cmd_ban(message: types.Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Access Denied")
        return

 codex/fix-telegram-bot-errors-and-stabilize-z3bilc
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
=======
        msg = await callback.message.answer(text, reply_markup=cancel_kb())
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to open admin panel")
    finally:
        await safe_answer(callback)


@dp.callback_query_handler(lambda c: c.data == "cancel_admin")
async def cancel_admin(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)

    try:
        await delete_message(user_id, callback.bot)

        try:
            await callback.message.delete()
        except Exception:
            pass

        msg = await callback.message.answer("🔙 Back to menu", reply_markup=main_menu(role))
        await save_message(user_id, msg)

    except Exception:
        await callback.message.answer("⚠️ Failed to return to menu")
    finally:
   main
