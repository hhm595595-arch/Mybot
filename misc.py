"""Group-level toggle commands (قفل_ / فتح_) and other misc commands"""

from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

from database import db
from utils.helpers import is_admin

TOGGLE_MAP = {
    "قفل_الروابط": ("link_protection", True, "✅ تم تفعيل حماية الروابط"),
    "فتح_الروابط": ("link_protection", False, "❌ تم تعطيل حماية الروابط"),
    "قفل_التكرار": ("anti_flood", True, "✅ تم تفعيل منع التكرار"),
    "فتح_التكرار": ("anti_flood", False, "❌ تم تعطيل منع التكرار"),
    "قفل_الترحيب": ("welcome", False, "❌ تم تعطيل الترحيب"),
    "فتح_الترحيب": ("welcome", True, "✅ تم تفعيل الترحيب"),
    "قفل_الكلمات": ("bad_words_filter", True, "✅ تم تفعيل فلترة الكلمات"),
    "فتح_الكلمات": ("bad_words_filter", False, "❌ تم تعطيل فلترة الكلمات"),
    "قفل_التوجيه": ("forward_protection", True, "✅ تم تفعيل منع التوجيه من القنوات"),
    "فتح_التوجيه": ("forward_protection", False, "❌ تم تعطيل منع التوجيه"),
    "قفل_الكابتشا": ("captcha", True, "✅ تم تفعيل التحقق البشري"),
    "فتح_الكابتشا": ("captcha", False, "❌ تم تعطيل التحقق البشري"),
    "قفل_الردود": ("auto_reply", False, "❌ تم تعطيل الردود التلقائية"),
    "فتح_الردود": ("auto_reply", True, "✅ تم تفعيل الردود التلقائية"),
    "قفل_الميديا": ("media_protection", True, "✅ تم تفعيل حماية الميديا"),
    "فتح_الميديا": ("media_protection", False, "❌ تم تعطيل حماية الميديا"),
    "قفل_البوتات": ("bot_protection", True, "✅ تم تفعيل حظر البوتات تلقائياً"),
    "فتح_البوتات": ("bot_protection", False, "❌ تم تعطيل حظر البوتات"),
    "قفل_الرتب": ("ranks_enabled", False, "❌ تم تعطيل نظام الرتب المخصصة"),
    "فتح_الرتب": ("ranks_enabled", True, "✅ تم تفعيل نظام الرتب المخصصة"),
    "تعيين_القوانين": None,
    "رتبة": None,
    "ترقيه": None,
    "ترقية": None,
    "تحويل": None,
    "اعط": None,
    "خذ": None,
}


def GroupMiscRouter() -> Router:
    router = Router(name="group_misc")

    @router.message(
        F.chat.type.in_({"group", "supergroup"}), 
        F.text.func(lambda text: text and (
            text.strip().lower() in ("تفعيل", "/تفعيل", "تعطيل", "/تعطيل", "الغاء_التفعيل", "الرتب", "النشطاء", "توب", "ترند", "top", "توب_انذار", "الانذارات", "top_warned", "يومية", "يومي", "daily", "claim", "رصيدي", "رصيد", "balance", "bal", "الاغنياء", "اغنياء", "richest", "الاعدادات", "الاعدادات المتطورة", "اعدادات", "settings", "advanced", "فحص_البوت", "فحص البوت", "فحص") or
            any(text.strip().lower().startswith(cmd.lower()) for cmd in TOGGLE_MAP) or
            text.strip().lower().startswith(("تعيين_القوانين", "تعيين القوانين", "رتبة", "ترقيه", "ترقية", "rank", "تحويل", "حول", "اعط", "give", "خذ", "take"))
        ))
    )
    async def handle_toggle_and_commands(msg: Message):
        text = msg.text.strip()
        user = msg.from_user
        chat = msg.chat
        if not user or user.is_bot:
            return

        chat_id = chat.id
        lower = text.lower()

        # --- Check if group is active ---
        is_active = await db.is_group_active(chat_id)

        # ── Diagnostics (فحص البوت) ──
        if lower in ("فحص_البوت", "فحص البوت", "فحص"):
            bot_member = await msg.chat.get_member(msg.bot.id)
            is_bot_admin = bot_member.status in ("administrator", "creator")
            
            permissions_text = "❌ غير مشرف (لا يمكنني العمل بشكل صحيح)"
            if is_bot_admin:
                perms = []
                if bot_member.can_delete_messages: perms.append("حذف رسائل")
                if bot_member.can_restrict_members: perms.append("تقييد أعضاء")
                if bot_member.can_pin_messages: perms.append("تثبيت رسائل")
                if bot_member.can_promote_members: perms.append("رفع مشرفين")
                permissions_text = f"✅ مشرف\nالصلاحيات: {', '.join(perms) if perms else 'بدون صلاحيات'}"

            db_status = "✅ متصلة" if await db.get_setting(chat_id, "auto_reply") is not None else "❌ خطأ في القراءة"
            group_status = "✅ مفعل" if is_active else "❌ غير مفعل (أرسل تفعيل)"
            
            auto_reply_setting = await db.get_setting(chat_id, "auto_reply")
            auto_reply_text = "✅ تعمل" if auto_reply_setting else "❌ معطلة من الإعدادات"

            await msg.reply(
                f"🔍 <b>تقرير فحص البوت الشامل:</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"🤖 <b>صلاحيات البوت:</b> {permissions_text}\n"
                f"⚙️ <b>حالة الجروب:</b> {group_status}\n"
                f"💬 <b>الردود التلقائية:</b> {auto_reply_text}\n"
                f"💾 <b>قاعدة البيانات:</b> {db_status}\n"
                f"━━━━━━━━━━━━━━\n"
                f"💡 <i>ملاحظة: إذا كانت كل الحالات ✅ ولا يرد على (ا)، فتأكد أن Privacy Mode معطل في BotFather.</i>"
            )
            return

        # --- Activation / Deactivation commands ---
        if lower in ("تفعيل", "تفعيل", "/تفعيل"):
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            owners = await get_owner_name(chat)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await db.activate_group(chat_id, user.id, user.id, now)
            await db.track_admin(chat_id, user.id)
            await msg.reply(
                f"✅ <b>تم تفعيل الجروب!</b> 🎉\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"📛 اسم الجروب: {chat.title}\n"
                f"🕐 وقت التفعيل: {now}\n"
                f"👤 المالك: {owners}\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"🛡️ <b>الحماية والردود مفعلة الآن!</b>"
            )
            return

        if lower in ("تعطيل", "تعطيل", "/تعطيل", "الغاء_التفعيل"):
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            await db.deactivate_group(chat_id)
            await msg.reply(
                f"🔴 <b>تم إلغاء تفعيل الجروب</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"📛 {chat.title}\n"
                f"━━━━━━━━━━━━━━\n"
                f"📌 أرسل <b>تفعيل</b> لإعادة التفعيل"
            )
            return

        # --- Check if group is active ---
        is_active = await db.is_group_active(chat_id)
        if not is_active:
            # Only respond to admins with a hint
            if await is_admin(chat, user.id):
                await msg.reply(
                    "❌ <b>الجروب غير مفعل!</b>\n"
                    "أرسل <b>تفعيل</b> لتفعيل الحماية والردود."
                )
            return

        # --- Night mode check ---
        night = await db.get_night_mode(chat_id)
        if night["enabled"]:
            current_hour = datetime.now().hour
            start = night["start"]
            end = night["end"]
            is_night = False
            if start > end:  # e.g., 22 to 7
                is_night = current_hour >= start or current_hour < end
            else:  # e.g., 0 to 6
                is_night = start <= current_hour < end
            if is_night and not await is_admin(chat, user.id):
                await msg.reply("🌙 <b>الوضع الليلي مفعل.</b> ممنوع الإرسال الآن.")
                try:
                    await msg.delete()
                except Exception:
                    pass
                return

        # --- Toggle settings (قفل_ / فتح_) ---
        for cmd in TOGGLE_MAP:
            entry = TOGGLE_MAP[cmd]
            if entry is None:
                continue
            if lower.startswith(cmd.lower()):
                if not await is_admin(chat, user.id):
                    await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                    return
                db_key, db_val, success_text = entry
                await db.set_setting(chat_id, db_key, db_val)
                await msg.reply(
                    f"{success_text}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"👤 بواسطة: {user.full_name}"
                )
                return

        # --- Set rules ---
        if lower.startswith("تعيين_القوانين") or lower.startswith("تعيين القوانين"):
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                await msg.reply("❌ استخدم: تعيين_القوانين + النص")
                return
            await db.set_rules(chat_id, parts[1])
            await msg.reply(f"✅ تم تعيين القوانين بنجاح!")
            return

        # --- Custom rank ---
        if lower.startswith("رتبة") or lower.startswith("ترقيه") or lower.startswith("ترقية") or lower.startswith("rank"):
            ranks_enabled = await db.get_setting(chat_id, "ranks_enabled")
            if ranks_enabled == 0:
                return
                
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            if not msg.reply_to_message:
                await msg.reply("❌ بالرد على العضو: ترقيه [اسم الرتبة]")
                return
            target = msg.reply_to_message.from_user
            parts = text.split(maxsplit=1)
            rank_name = parts[1] if len(parts) > 1 else ""
            if not rank_name:
                await msg.reply("❌ اكتب اسم الرتبة بعد الأمر!")
                return
                
            await db.set_custom_rank(chat_id, target.id, rank_name)
            await msg.reply(
                f"🎉 <b>تم الترقية بنجاح!</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 العضو: {target.full_name}\n"
                f"🏅 الرتبة: <b>{rank_name}</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"✨ تستاهل كل خير يا وحش! 🌟"
            )
            return

        # --- Transfer ---
        if lower.startswith("تحويل") or lower.startswith("حول"):
            if not msg.reply_to_message:
                await msg.reply("❌ بالرد على العضو: تحويل المبلغ")
                return
            parts = text.split()
            if len(parts) < 2 or not parts[1].isdigit():
                await msg.reply("❌ استخدم: تحويل 100 (بالرد على العضو)")
                return
            amount = int(parts[1])
            target = msg.reply_to_message.from_user
            sender_bal = await db.get_balance(chat_id, user.id)
            if sender_bal < amount:
                await msg.reply("❌ رصيدك غير كافٍ!")
                return
            await db.add_balance(chat_id, user.id, -amount)
            await db.add_balance(chat_id, target.id, amount)
            await msg.reply(f"✅ تم تحويل {amount:,} نقطة إلى {target.full_name}")
            return

        # --- Give (admin) ---
        if lower.startswith("اعط") or lower.startswith("give"):
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            if not msg.reply_to_message:
                await msg.reply("❌ بالرد على العضو: اعط المبلغ")
                return
            parts = text.split()
            if len(parts) < 2 or not parts[1].isdigit():
                await msg.reply("❌ استخدم: اعط 100 (بالرد على العضو)")
                return
            amount = int(parts[1])
            target = msg.reply_to_message.from_user
            await db.add_balance(chat_id, target.id, amount)
            await msg.reply(f"✅ تم إضافة {amount:,} نقطة إلى {target.full_name}")
            return

        # --- Take (admin) ---
        if lower.startswith("خذ") or lower.startswith("take"):
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            if not msg.reply_to_message:
                await msg.reply("❌ بالرد على العضو: خذ المبلغ")
                return
            parts = text.split()
            if len(parts) < 2 or not parts[1].isdigit():
                await msg.reply("❌ استخدم: خذ 100 (بالرد على العضو)")
                return
            amount = int(parts[1])
            target = msg.reply_to_message.from_user
            await db.add_balance(chat_id, target.id, -amount)
            await msg.reply(f"✅ تم خصم {amount:,} نقطة من {target.full_name}")
            return

        # --- Top members (ترند) ---
        if lower in ("الرتب", "النشطاء", "توب", "ترند", "top"):
            users = await db.get_top_messages(chat_id, 20)
            lines = ["• توب لأكثر 20 متفاعلين في القروب\n"]
            for i, u in enumerate(users, 1):
                try:
                    member = await chat.get_member(u["user_id"])
                    name = member.user.first_name
                    if not name:
                        name = "عضو"
                except Exception:
                    name = f"ID: {u['user_id']}"
                    
                medal = ""
                if i == 1: medal = "🥇"
                elif i == 2: medal = "🥈"
                elif i == 3: medal = "🥉"
                
                link = f"<a href='tg://user?id={u['user_id']}'>{name}</a>"
                lines.append(f"{i}){medal}  {u['messages']}  l {link}")
                
            await msg.reply("\n".join(lines))
            return

        # --- Top warned ---
        if lower in ("توب_انذار", "الانذارات", "top_warned"):
            users = await db.get_top_warns(chat_id, 10)
            lines = ["📊 <b>ترتيب الإنذارات</b>\n━━━━━━━━━━━━━━"]
            for i, u in enumerate(users, 1):
                try:
                    member = await chat.get_member(u["user_id"])
                    name = member.user.full_name
                except Exception:
                    name = f"ID: {u['user_id']}"
                lines.append(f"{i}. {name} ─ {u['warns']} إنذار(ات)")
            lines.append("━━━━━━━━━━━━━━")
            await msg.reply("\n".join(lines))
            return

        # --- Daily claim (in group) ---
        if lower in ("يومية", "يومي", "daily", "claim"):
            from datetime import date
            today = date.today().isoformat()
            last = await db.get_last_daily(user.id, chat_id)
            if last == today:
                await msg.reply("❌ لقد استلمت راتبك اليومي مسبقاً!")
                return
            import random
            amount = random.randint(50, 150)
            await db.set_last_daily(user.id, chat_id, today)
            current = await db.get_balance(chat_id, user.id)
            await db.set_balance(chat_id, user.id, current + amount)
            await msg.reply(
                f"🎁 <b>الراتب اليومي!</b>\n"
                f"💰 حصلت على: <b>+{amount}</b> نقطة\n"
                f"💵 رصيدك: <b>{current + amount:,}</b> نقطة"
            )
            return

        # --- Balance ---
        if lower in ("رصيدي", "رصيد", "balance", "bal"):
            bal = await db.get_balance(chat_id, user.id)
            warns = await db.get_warns(chat_id, user.id)
            await msg.reply(
                f"💰 <b>رصيدك</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 {user.full_name}\n"
                f"💵 الرصيد: <b>{bal:,}</b> نقطة\n"
                f"⚠️ الإنذارات: {warns}\n"
                f"━━━━━━━━━━━━━━"
            )
            return

        # --- Richest ---
        if lower in ("الاغنياء", "اغنياء", "richest"):
            users = await db.get_richest(chat_id, 10)
            lines = ["🏆 <b>ترتيب الأغنياء</b>\n━━━━━━━━━━━━━━"]
            for i, u in enumerate(users, 1):
                try:
                    member = await chat.get_member(u["user_id"])
                    name = member.user.full_name
                except Exception:
                    name = f"ID: {u['user_id']}"
                lines.append(f"{i}. {name} ─ <b>{u['balance']:,}</b> نقطة")
            lines.append("━━━━━━━━━━━━━━")
            await msg.reply("\n".join(lines))
            return

        # --- Settings display in group ---
        if lower in ("الاعدادات", "الاعدادات المتطورة", "اعدادات", "settings", "advanced"):
            from handlers.private.settings import SETTINGS_LABELS
            if not await is_admin(chat, user.id):
                await msg.reply("❌ هذا الأمر للمشرفين فقط.")
                return
            is_active = await db.is_group_active(chat_id)
            night = await db.get_night_mode(chat_id)
            warn_limit = await db.get_warn_limit(chat_id)
            activation = await db.get_activation_info(chat_id)
            status = "✅ مفعل" if is_active else "❌ غير مفعل"
            lines = [
                f"⚙️ <b>الإعدادات المتطورة</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📊 حالة الجروب: {status}"
            ]
            if activation and activation.get("activated_at"):
                lines.append(f"🕐 آخر تفعيل: {activation['activated_at']}")
            lines.append("━━━━━━━━━━━━━━━━━━━")
            for key, label in SETTINGS_LABELS.items():
                if key == "night_mode":
                    val = night["enabled"]
                    extra = ""
                    if val:
                        extra = f" ({night['start']}:00 - {night['end']}:00)"
                    status_emoji = "✅" if val else "❌"
                    lines.append(f"{status_emoji} {label}{extra}")
                else:
                    val = await db.get_setting(chat_id, key)
                    status_emoji = "✅" if val else "❌"
                    lines.append(f"{status_emoji} {label}")
            lines.append(f"\n🛡️ حد الإنذارات: <b>{warn_limit}</b>")
            lines.append("━━━━━━━━━━━━━━━━━━━")
            lines.append("🔧 استخدم قفل_ / فتح_ لتغيير الإعدادات")
            await msg.reply("\n".join(lines))
            return

    return router


async def get_owner_name(chat):
    try:
        admins = await chat.get_administrators()
        for admin in admins:
            if admin.status == ChatMemberStatus.CREATOR:
                return admin.user.full_name
    except Exception:
        pass
    return "غير معروف"
