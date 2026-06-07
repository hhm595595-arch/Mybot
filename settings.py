from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database import db
from utils.helpers import is_admin, format_date

class NightModeState(StatesGroup):
    waiting_for_times = State()

SETTINGS_LABELS = {
    "link_protection": "🔗 حماية الروابط",
    "anti_flood": "🔄 منع التكرار",
    "bad_words_filter": "🚫 فلترة الكلمات",
    "forward_protection": "📤 منع التوجيه",
    "welcome": "👋 الترحيب",
    "captcha": "🔐 التحقق البشري",
    "auto_reply": "💬 الردود التلقائية",
    "night_mode": "🌙 الوضع الليلي",
    "media_protection": "🎬 حماية الميديا",
    "bot_protection": "🤖 حظر البوتات",
    "long_msg_protection": "📏 منع الرسائل الطويلة",
    "ranks_enabled": "🏅 نظام الرتب",
}


def private_settings_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📋 جروباتي", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def build_group_settings_keyboard(chat_id: int, title: str) -> InlineKeyboardMarkup:
    import asyncio

    # We need to pass chat_id via callback, so encode it
    cid = str(chat_id)
    keyboard = [
        [InlineKeyboardButton(text="🔗 حماية الروابط", callback_data=f"gset:{cid}:link_protection"),
         InlineKeyboardButton(text="🔄 منع التكرار", callback_data=f"gset:{cid}:anti_flood")],
        [InlineKeyboardButton(text="🚫 فلترة الكلمات", callback_data=f"gset:{cid}:bad_words_filter"),
         InlineKeyboardButton(text="📤 منع التوجيه", callback_data=f"gset:{cid}:forward_protection")],
        [InlineKeyboardButton(text="👋 الترحيب", callback_data=f"gset:{cid}:welcome"),
         InlineKeyboardButton(text="🔐 التحقق البشري", callback_data=f"gset:{cid}:captcha")],
        [InlineKeyboardButton(text="💬 الردود التلقائية", callback_data=f"gset:{cid}:auto_reply"),
         InlineKeyboardButton(text="🌙 الوضع الليلي", callback_data=f"gset:{cid}:night_mode")],
        [InlineKeyboardButton(text="🎬 حماية الميديا", callback_data=f"gset:{cid}:media_protection"),
         InlineKeyboardButton(text="🤖 حظر البوتات", callback_data=f"gset:{cid}:bot_protection")],
        [InlineKeyboardButton(text="📏 منع الرسائل الطويلة", callback_data=f"gset:{cid}:long_msg_protection"),
         InlineKeyboardButton(text="🏅 نظام الرتب", callback_data=f"gset:{cid}:ranks_enabled")],
        [InlineKeyboardButton(text="🛡️ حد الإنذارات ➖", callback_data=f"gset:{cid}:warn_down"),
         InlineKeyboardButton(text="🛡️ حد الإنذارات ➕", callback_data=f"gset:{cid}:warn_up")],
        [InlineKeyboardButton(text="📦 تصدير الإعدادات", callback_data=f"gset:{cid}:export")],
        [InlineKeyboardButton(text="🔙 رجوع للقائمة", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def PrivateSettingsRouter() -> Router:
    router = Router(name="private_settings")

    @router.message(F.text == "⚙️ الإعدادات", F.chat.type == "private")
    async def settings_text(msg: Message, state: FSMContext):
        await state.clear()
        await msg.answer(
            "⚙️ <b>الإعدادات المتطورة</b>\n"
            "━━━━━━━━━━━━━━\n"
            "📋 اختر <b>جروباتي</b> من القائمة الرئيسية\n"
            "لإدارة إعدادات مجموعاتك."
        )

    @router.callback_query(F.data.startswith("gset:"))
    async def group_settings_callback(cq: CallbackQuery, state: FSMContext):
        await cq.answer()
        parts = cq.data.split(":")
        if len(parts) < 3:
            return
        chat_id = int(parts[1])
        action = parts[2]

        # Check if user is admin of that group
        try:
            member = await cq.bot.get_chat_member(chat_id, cq.from_user.id)
            if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
                await cq.message.edit_text("❌ أنت لست مشرفاً في هذه المجموعة.")
                return
        except Exception:
            await cq.message.edit_text("❌ لا يمكن التحقق من صلاحياتك. تأكد أن البوت في المجموعة.")
            return

        if action == "export":
            config = await db.export_group(chat_id)
            import json, os, tempfile
            json_str = json.dumps(config, ensure_ascii=False, indent=2)
            temp = os.path.join(tempfile.gettempdir(), f"rio_config_{chat_id}.json")
            with open(temp, "w", encoding="utf-8") as f:
                f.write(json_str)
                
            from aiogram.types import FSInputFile
            doc = FSInputFile(temp)
            title = await db.get_group_title(chat_id) or f"المجموعة {chat_id}"
            await cq.message.answer_document(
                document=doc,
                caption=f"📦 إعدادات <b>{title}</b>"
            )
            os.remove(temp)
            await cq.message.edit_text("✅ تم تصدير الإعدادات!")
            return

        if action == "warn_up":
            limit = await db.get_warn_limit(chat_id)
            if limit < 20:
                await db.set_warn_limit(chat_id, limit + 1)
        elif action == "warn_down":
            limit = await db.get_warn_limit(chat_id)
            if limit > 1:
                await db.set_warn_limit(chat_id, limit - 1)
        elif action == "night_mode":
            night = await db.get_night_mode(chat_id)
            if night["enabled"]:
                await db.set_night_mode(chat_id, False)
                await cq.answer("تم إطفاء الوضع الليلي", show_alert=True)
            else:
                title = await db.get_group_title(chat_id) or f"المجموعة {chat_id}"
                await state.set_state(NightModeState.waiting_for_times)
                await state.update_data(chat_id=chat_id, title=title)
                await cq.message.edit_text(
                    f"🌙 <b>إعداد الوضع الليلي لـ {title}</b>\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"يرجى كتابة أوقات الوضع الليلي بصيغة الأرقام (البداية النهاية)\n"
                    f"مثال: <code>21 8</code> (يعني من 9 مساءً إلى 8 صباحاً)\n"
                    f"أو أرسل <code>تخطي</code> لتفعيل الوضع باوقات افتراضية."
                )
                await cq.answer("جاري تفعيل الوضع الليلي...")
                return
        elif action in SETTINGS_LABELS:
            current = await db.get_setting(chat_id, action)
            new_val = 0 if current else 1
            await db.set_setting(chat_id, action, new_val)
            
            explanations = {
                "link_protection": "يمنع الأعضاء من إرسال الروابط.",
                "anti_flood": "يحمي الجروب من التكرار والسبام.",
                "bad_words_filter": "يحذف الشتائم والكلمات البذيئة.",
                "forward_protection": "يمنع تحويل الرسائل من قنوات للجروب.",
                "welcome": "يرحب بالأعضاء الجدد تلقائياً.",
                "captcha": "يختبر العضو الجديد بسؤال رياضيات لمنع البوتات الوهمية.",
                "auto_reply": "يتفاعل مع الأعضاء بردود تلقائية مضحكة.",
                "media_protection": "يمنع إرسال الميديا بشكل متكرر (سبام الميديا).",
                "bot_protection": "يطرد أي بوت جديد يتم إضافته للجروب.",
                "long_msg_protection": "يمنع الجرائد والرسائل الطويلة المزعجة.",
                "ranks_enabled": "يفعل أو يعطل نظام الرتب للأعضاء."
            }
            status_text = "تفعيل" if new_val else "إيقاف"
            msg_text = f"✅ تم {status_text} {SETTINGS_LABELS[action]}!\n\n💡 وظيفتها: {explanations.get(action, '')}"
            await cq.answer(msg_text, show_alert=True)

        title = await db.get_group_title(chat_id) or f"المجموعة {chat_id}"
        txt = await build_group_settings_text(chat_id, title)
        keyboard = build_group_settings_keyboard(chat_id, title)
        await cq.message.edit_text(txt, reply_markup=keyboard)

    @router.message(NightModeState.waiting_for_times, F.chat.type == "private")
    async def process_night_times(msg: Message, state: FSMContext):
        data = await state.get_data()
        chat_id = data.get("chat_id")
        title = data.get("title")
        
        if msg.text.strip() == "تخطي":
            start_hour, end_hour = 22, 7
        else:
            try:
                parts = msg.text.split()
                if len(parts) != 2:
                    raise ValueError
                start_hour = int(parts[0])
                end_hour = int(parts[1])
                if not (0 <= start_hour <= 23) or not (0 <= end_hour <= 23):
                    raise ValueError
            except ValueError:
                await msg.answer("❌ <b>صيغة خاطئة!</b> يرجى إرسال أرقام فقط مثل: <code>21 8</code>\nأو أرسل <code>تخطي</code>")
                return
                
        await db.set_night_mode(chat_id, True, start_hour, end_hour)
        await state.clear()
        
        txt = await build_group_settings_text(chat_id, title)
        keyboard = build_group_settings_keyboard(chat_id, title)
        await msg.answer(f"✅ <b>تم تفعيل الوضع الليلي من {start_hour}:00 إلى {end_hour}:00</b>\n\n{txt}", reply_markup=keyboard)

    return router


async def build_group_settings_text(chat_id: int, title: str) -> str:
    is_active = await db.is_group_active(chat_id)
    night = await db.get_night_mode(chat_id)
    warn_limit = await db.get_warn_limit(chat_id)
    activation = await db.get_activation_info(chat_id)

    status = "✅ مفعل" if is_active else "❌ غير مفعل"
    lines = [
        f"⚙️ <b>{title}</b>\n",
        f"🆔 <code>{chat_id}</code> | {status}\n",
        "━━━━━━━━━━━━━━",
    ]
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
    if activation and activation["activated_at"]:
        lines.append(f"🕐 آخر تفعيل: {activation['activated_at']}")
    lines.append("\n━━━━━━━━━━━━━━\n🔧 اختر إعداداً لتغييره:")
    return "\n".join(lines)
