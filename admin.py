from datetime import datetime, timedelta
import asyncio

from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from aiogram.enums import ChatMemberStatus

from database import db
from utils.helpers import is_admin, format_date


def GroupAdminRouter() -> Router:
    router = Router(name="group_admin")

    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.reply_to_message, 
        F.text.func(lambda text: text and text.strip().split()[0].lower() in (
            "حظر", "ban", "/حظر", "/ban", "طرد", "kick", "/طرد", "/kick",
            "انذار", "warn", "/انذار", "/warn", "الغاء_انذار", "unwarn", "/الغاء_انذار", "/unwarn",
            "كتم", "mute", "/كتم", "/mute", "الغاء_الكتم", "unmute", "/الغاء_الكتم", "/unmute",
            "كشف", "info", "/كشف", "/info"
        ) or text.strip().lower() in (
            "كتم 5", "كتم ٥", "كتم 30", "كتم ٣٠", "كتم يوم", "كتم 1 يوم", "كتم يوم كامل"
        ))
    )
    async def admin_commands(msg: Message):
        chat = msg.chat
        user = msg.from_user
        target = msg.reply_to_message.from_user

        if not user or not target or user.is_bot:
            return
        if not await is_admin(chat, user.id):
            return
        if target.is_bot or target.id == user.id or target.id == msg.bot.id:
            return
        if await is_admin(chat, target.id):
            await msg.reply("❌ <b>لا يمكن تنفيذ الأمر على مشرف.</b>")
            return

        text = msg.text.strip().lower()
        cmd = text.split()[0] if text else ""
        reason = msg.text[len(cmd):].strip() if len(msg.text) > len(cmd) else ""

        target_id = target.id

        # ── Ban ──
        if cmd in ("حظر", "ban", "/حظر", "/ban"):
            try:
                await chat.ban(target_id)
                await db.reset_warns(chat_id, target_id)
                await msg.reply(
                    f"🚫 <b>تم حظر</b> {target.full_name}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"👤 بواسطة: {user.full_name}\n"
                    f"📅 {format_date()}"
                )
            except Exception as e:
                await msg.reply(f"❌ <b>فشل الحظر:</b> {e}")

        # ── Kick ──
        elif cmd in ("طرد", "kick", "/طرد", "/kick"):
            try:
                await chat.unban(target_id)
                await db.reset_warns(chat_id, target_id)
                await msg.reply(
                    f"👢 <b>تم طرد</b> {target.full_name}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"👤 بواسطة: {user.full_name}\n"
                    f"📅 {format_date()}"
                )
            except Exception as e:
                await msg.reply(f"❌ <b>فشل الطرد:</b> {e}")

        # ── Warn ──
        elif cmd in ("انذار", "warn", "/انذار", "/warn"):
            warns = await db.add_warn(chat_id, target_id, reason)
            warn_limit = await db.get_warn_limit(chat_id)
            remaining = warn_limit - warns

            if remaining <= 0:
                try:
                    await chat.ban(target_id)
                    await db.reset_warns(chat_id, target_id)
                    await msg.reply(
                        f"🚫 <b>تم حظر</b> {target.full_name}\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"⚠️ السبب: بلوغ {warn_limit} إنذارات\n"
                        f"📅 {format_date()}"
                    )
                except Exception as e:
                    await msg.reply(f"❌ <b>فشل الحظر:</b> {e}")
            else:
                txt = (
                    f"⚠️ <b>إنذار {warns}/{warn_limit}</b>\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"👤 العضو: {target.full_name}\n"
                    f"🆔 <code>{target_id}</code>\n"
                    f"👮 بواسطة: {user.full_name}\n"
                    f"📊 المتبقي: {remaining} إنذار(ات)"
                )
                if reason:
                    txt += f"\n📝 السبب: <i>{reason}</i>"
                await msg.reply(txt)

        # ── Unwarn ──
        elif cmd in ("الغاء_انذار", "unwarn", "/الغاء_انذار", "/unwarn"):
            warns = await db.remove_warn(chat_id, target_id)
            await msg.reply(
                f"✅ <b>تم إلغاء إنذار</b> من {target.full_name}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"📊 الآن لديه: {warns} إنذار(ات)"
            )

        # ── Mute (1 hour) ──
        elif cmd in ("كتم", "mute", "/كتم", "/mute"):
            try:
                permissions = ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                )
                until = datetime.now() + timedelta(hours=1)
                await chat.restrict(target_id, permissions, until_date=until)
                await msg.reply(
                    f"🔇 <b>تم كتم</b> {target.full_name}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"⏳ المدة: ساعة واحدة\n"
                    f"👤 بواسطة: {user.full_name}"
                )
            except Exception as e:
                await msg.reply(f"❌ <b>فشل الكتم:</b> {e}")

        # ── Unmute ──
        elif cmd in ("الغاء_الكتم", "unmute", "/الغاء_الكتم", "/unmute"):
            try:
                permissions = ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                )
                await chat.restrict(target_id, permissions)
                await msg.reply(
                    f"🔊 <b>تم إلغاء الكتم</b> عن {target.full_name}\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"👤 بواسطة: {user.full_name}"
                )
            except Exception as e:
                await msg.reply(f"❌ <b>فشل إلغاء الكتم:</b> {e}")

        # ── Mute 5 min ──
        elif cmd in ("كتم 5", "كتم ٥"):
            try:
                permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
                until = datetime.now() + timedelta(minutes=5)
                await chat.restrict(target_id, permissions, until_date=until)
                await msg.reply(f"🔇 <b>تم كتم</b> {target.full_name} لمدة 5 دقائق")
            except Exception as e:
                await msg.reply(f"❌ {e}")

        # ── Mute 30 min ──
        elif cmd in ("كتم 30", "كتم ٣٠"):
            try:
                permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
                until = datetime.now() + timedelta(minutes=30)
                await chat.restrict(target_id, permissions, until_date=until)
                await msg.reply(f"🔇 <b>تم كتم</b> {target.full_name} لمدة 30 دقيقة")
            except Exception as e:
                await msg.reply(f"❌ {e}")

        # ── Mute 1 day ──
        elif cmd in ("كتم يوم", "كتم 1 يوم", "كتم يوم كامل"):
            try:
                permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
                until = datetime.now() + timedelta(days=1)
                await chat.restrict(target_id, permissions, until_date=until)
                await msg.reply(f"🔇 <b>تم كتم</b> {target.full_name} لمدة يوم كامل")
            except Exception as e:
                await msg.reply(f"❌ {e}")

        # ── Info ──
        elif cmd in ("كشف", "info", "/كشف", "/info"):
            await show_user_info(msg, chat, target)

    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.text.func(lambda text: text and (
            text.strip().lower().startswith("تثبيت") or 
            text.strip().lower() in ("pin", "/pin", "الغاء_التثبيت", "unpin", "/unpin") or
            text.strip().lower().startswith("بطيء") or 
            text.strip().lower() in ("الغاء_البطيء", "الغاء البطيء", "قفل_المجموعة", "قفل الجروب", "قفل_الجروب", "lock", "فتح_المجموعة", "فتح الجروب", "فتح_الجروب", "unlock") or
            text.strip().lower().startswith("تنظيف") or 
            text.strip().lower().startswith("مسح")
        ))
    )
    async def admin_direct_commands(msg: Message):
        chat = msg.chat
        user = msg.from_user
        if not user or user.is_bot:
            return
        if not await is_admin(chat, user.id):
            return

        text = msg.text.strip().lower()
        chat_id = chat.id

        # ── Pin ──
        if text.startswith("تثبيت") or text in ("pin", "/pin"):
            if not msg.reply_to_message:
                await msg.reply("❌ بالرد على الرسالة: <b>تثبيت</b>")
                return
            try:
                await msg.reply_to_message.pin()
                await msg.reply(f"📌 <b>تم تثبيت الرسالة</b> ✅")
            except Exception as e:
                await msg.reply(f"❌ <b>فشل التثبيت:</b> {e}")

        # ── Unpin ──
        elif text.startswith("الغاء_التثبيت") or text in ("unpin", "/unpin"):
            try:
                if msg.reply_to_message:
                    await msg.reply_to_message.unpin()
                else:
                    await chat.unpin()
                await msg.reply(f"📌 <b>تم إلغاء تثبيت الرسالة</b> ✅")
            except Exception as e:
                await msg.reply(f"❌ <b>فشل إلغاء التثبيت:</b> {e}")

        # ── Slow mode ──
        elif text.startswith("بطيء"):
            parts = text.split()
            seconds = 10
            if len(parts) > 1 and parts[1].isdigit():
                seconds = int(parts[1])
            try:
                await chat.set_slow_mode_delay(seconds)
                await msg.reply(
                    f"🐌 <b>تم تفعيل الوضع البطيء</b>\n"
                    f"⏱ المهلة: {seconds} ثانية بين الرسائل"
                )
            except Exception as e:
                await msg.reply(f"❌ <b>فشل:</b> {e}")

        # ── Remove slow mode ──
        elif text in ("الغاء_البطيء", "الغاء البطيء"):
            try:
                await chat.set_slow_mode_delay(0)
                await msg.reply(f"🐌 <b>تم إلغاء الوضع البطيء</b> ✅")
            except Exception as e:
                await msg.reply(f"❌ <b>فشل:</b> {e}")

        # ── Lock group (restrict all) ──
        elif text in ("قفل_المجموعة", "قفل الجروب", "قفل_الجروب", "lock"):
            try:
                permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
                await chat.set_permissions(permissions)
                await msg.reply(f"🔒 <b>تم قفل المجموعة</b>\nالكل ممنوع من الإرسال")
            except Exception as e:
                await msg.reply(f"❌ <b>فشل:</b> {e}")

        # ── Unlock group ──
        elif text in ("فتح_المجموعة", "فتح الجروب", "فتح_الجروب", "unlock"):
            try:
                permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
                await chat.set_permissions(permissions)
                await msg.reply(f"🔓 <b>تم فتح المجموعة</b>\nالكل مسموح له بالإرسال")
            except Exception as e:
                await msg.reply(f"❌ <b>فشل:</b> {e}")

        # ── Clean messages ──
        elif text.startswith("تنظيف") or text.startswith("مسح"):
            if not msg.reply_to_message:
                await msg.reply("❌ بالرد على رسالة: <b>تنظيف [عدد]</b>")
                return
            parts = text.split()
            count = 100
            if len(parts) > 1 and parts[1].isdigit():
                count = min(int(parts[1]), 500)
            try:
                deleted = 0
                async for old_msg in chat.iterate_history(limit=count):
                    if old_msg.date >= msg.reply_to_message.date:
                        await old_msg.delete()
                        deleted += 1
                        await asyncio.sleep(0.05)
                await msg.reply(f"🧹 <b>تم تنظيف {deleted} رسالة</b> ✅")
            except Exception as e:
                await msg.reply(f"❌ <b>فشل التنظيف:</b> {e}")

    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.text.func(lambda text: text and text.strip().split()[0].lower() in ("نداء", "الكل", "@all", "all"))
    )
    async def tag_all_handler(msg: Message):
        chat = msg.chat
        user = msg.from_user
        if not await is_admin(chat, user.id):
            return

        text = msg.text.strip()
        cmd = text.split()[0]
        reason = text[len(cmd):].strip()

        try:
            active_users = await db.get_top_messages(chat.id, 50)
            if not active_users:
                await msg.reply("❌ لا يوجد أعضاء نشطين لندائهم.")
                return
                
            tags = []
            for u in active_users:
                try:
                    member = await chat.get_member(u["user_id"])
                    name = member.user.first_name or "عضو"
                except Exception:
                    name = "عضو"
                tags.append(f"<a href='tg://user?id={u['user_id']}'>@{name}</a>")
            
            # Split tags into groups of 10 to avoid too long messages
            chunks = [tags[i:i + 10] for i in range(0, len(tags), 10)]
            
            broadcast_msg = reason if reason else "📢 نداء لجميع الأعضاء، تواجدوا الآن!"
            
            for chunk in chunks:
                mention_text = " ".join(chunk)
                await msg.answer(f"{mention_text}\n{broadcast_msg}")
                
        except Exception as e:
            await msg.reply(f"❌ حدث خطأ أثناء النداء: {e}")

    return router


async def show_user_info(msg: Message, chat, target_user):
    uid = target_user.id
    name = target_user.full_name
    username = f"@{target_user.username}" if target_user.username else "لا يوجد"
    profile_link = f"tg://user?id={uid}"

    warns = await db.get_warns(chat.id, uid)
    balance = await db.get_balance(chat.id, uid)
    messages = await db.get_messages_count(chat.id, uid)
    join_date = await db.get_join_date(chat.id, uid) or "غير متوفر"
    custom_rank = await db.get_custom_rank(chat.id, uid)
    captcha_passed = await db.has_passed_captcha(chat.id, uid)

    captcha_status = "✅ اجتاز" if captcha_passed else "❌ لم يجتاز"
    rank_display = f"🏅 {custom_rank}" if custom_rank else "—"

    txt = (
        f"ℹ️ <b>معلومات العضو</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📛 <b>الاسم:</b> {name}\n"
        f"🆔 <b>الأيدي:</b> <code>{uid}</code>\n"
        f"🔗 <b>اليوزر:</b> {username}\n"
        f"🔗 <b>الرابط:</b> <a href='{profile_link}'>اضغط هنا</a>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>تاريخ الانضمام:</b> {join_date}\n"
        f"💬 <b>الرسائل:</b> {messages:,}\n"
        f"💰 <b>الرصيد:</b> {balance:,} نقطة\n"
        f"⚠️ <b>الإنذارات:</b> {warns}\n"
        f"🏅 <b>الرتبة:</b> {rank_display}\n"
        f"🔐 <b>الكابتشا:</b> {captcha_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        photos = await msg.bot.get_user_profile_photos(uid, limit=1)
        if photos.photos:
            photo = photos.photos[0][-1].file_id
            await msg.reply_photo(photo=photo, caption=txt)
        else:
            await msg.reply(txt)
    except Exception:
        await msg.reply(txt)
