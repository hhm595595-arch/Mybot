from aiogram import Router, F
from aiogram.types import Message
from config import OWNER_ID
from database import db
import asyncio

def OwnerRouter() -> Router:
    router = Router(name="owner_router")

    @router.message(F.text.startswith("/اذاعة ") | F.text.startswith("اذاعة "), F.from_user.id == OWNER_ID)
    async def broadcast_cmd(msg: Message):
        parts = msg.text.split(maxsplit=1)
        if len(parts) < 2:
            await msg.reply("❌ اكتب الرسالة بعد الأمر: /اذاعة [الرسالة]")
            return
            
        broadcast_text = parts[1]
        
        active_groups = await db.get_all_active_groups()
        private_users = await db.get_all_private_users()
        
        status_msg = await msg.reply(f"📢 <b>جاري الإذاعة...</b>\n\n🎯 <b>المجموعات:</b> {len(active_groups)}\n👤 <b>الأشخاص:</b> {len(private_users)}")
        
        success = 0
        failed = 0
        
        for group in active_groups:
            try:
                await msg.bot.send_message(group["chat_id"], f"📢 <b>إعلان عام:</b>\n━━━━━━━━━━━━━━\n{broadcast_text}")
                success += 1
                await asyncio.sleep(0.05)
            except Exception:
                failed += 1
                
        for user in private_users:
            try:
                await msg.bot.send_message(user["user_id"], f"📢 <b>رسالة من المطور:</b>\n━━━━━━━━━━━━━━\n{broadcast_text}")
                success += 1
                await asyncio.sleep(0.05)
            except Exception:
                failed += 1
                
        await status_msg.edit_text(f"✅ <b>تم الإرسال بنجاح!</b>\n\n🟢 نجح: {success}\n🔴 فشل: {failed}")

    @router.message(F.text.in_(["/panel", "لوحة", "المطور", "/admin"]), F.from_user.id == OWNER_ID)
    async def owner_panel_cmd(msg: Message):
        stats = await db.get_bot_stats()
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 إذاعة للمجموعات", callback_data="owner_broadcast_groups")],
            [InlineKeyboardButton(text="📢 إذاعة للخاص", callback_data="owner_broadcast_private")],
            [InlineKeyboardButton(text="📊 تحديث الإحصائيات", callback_data="owner_refresh_stats")]
        ])
        
        await msg.answer(
            f"👑 <b>لوحة تحكم المالك</b> 👑\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 <b>إجمالي المستخدمين بالخاص:</b> {stats['users']}\n"
            f"👥 <b>إجمالي المجموعات:</b> {stats['groups']}\n"
            f"🟢 <b>المجموعات المفعلة:</b> {stats['active_groups']}\n"
            f"━━━━━━━━━━━━━━\n"
            f"اختر أحد الأوامر من الأسفل 👇",
            reply_markup=kb
        )

    @router.callback_query(F.data.startswith("owner_"), F.from_user.id == OWNER_ID)
    async def owner_panel_callback(cq, state=None):
        action = cq.data
        if action == "owner_refresh_stats":
            stats = await db.get_bot_stats()
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 إذاعة للمجموعات", callback_data="owner_broadcast_groups")],
                [InlineKeyboardButton(text="📢 إذاعة للخاص", callback_data="owner_broadcast_private")],
                [InlineKeyboardButton(text="📊 تحديث الإحصائيات", callback_data="owner_refresh_stats")]
            ])
            
            await cq.message.edit_text(
                f"👑 <b>لوحة تحكم المالك</b> 👑\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 <b>إجمالي المستخدمين بالخاص:</b> {stats['users']}\n"
                f"👥 <b>إجمالي المجموعات:</b> {stats['groups']}\n"
                f"🟢 <b>المجموعات المفعلة:</b> {stats['active_groups']}\n"
                f"━━━━━━━━━━━━━━\n"
                f"اختر أحد الأوامر من الأسفل 👇",
                reply_markup=kb
            )
            await cq.answer("تم تحديث الإحصائيات!")
            
        elif action == "owner_broadcast_groups":
            await cq.answer("قم بكتابة: اذاعة [الرسالة] ليتم إرسالها لجميع المجموعات والأفراد", show_alert=True)
            
        elif action == "owner_broadcast_private":
            await cq.answer("قم بكتابة: اذاعة [الرسالة] ليتم إرسالها لجميع المجموعات والأفراد", show_alert=True)

    return router
