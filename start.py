from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

from database import db


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🕋 القسم الديني"), KeyboardButton(text="🎵 تحميل الصوتيات")],
        [KeyboardButton(text="📚 المكتبة والثقافة"), KeyboardButton(text="🖼️ الافتارات")],
        [KeyboardButton(text="🏦 البنك والألعاب"), KeyboardButton(text="📋 جروباتي")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def main_inline_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 قائمة مجموعاتك", callback_data="my_groups")],
        [InlineKeyboardButton(text="⚙️ الإعدادات المطورة", callback_data="section_settings")],
        [InlineKeyboardButton(text="➕ اضفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=start")],
    ])


def PrivateStartRouter() -> Router:
    router = Router(name="private_start")

    @router.message(CommandStart())
    async def start_cmd(msg: Message):
        user = msg.from_user
        me = await msg.bot.me()
        
        await db.track_user(user.id, user.username, user.full_name)
        
        await msg.answer("👇 <b>تم فتح قائمة الأزرار السريعة بالأسفل</b> 🚀", reply_markup=main_reply_keyboard())
        await msg.answer(
            f"🎊 🌟 مرحباً بك في ريو (Rio)! 🌟\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 الاسم: {user.full_name}\n"
            f"🆔 الأيدي: <code>{user.id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 ريو - الإمبراطور الجديد لإدارة وحماية المجموعات 🛡\n\n"
            f"🔥 المميزات:\n"
            f"├ 🛡 حماية فولاذية (روابط، تكرار، كلمات، توجيه)\n"
            f"├ 🔐 نظام تحقق بشري (كابتشا)\n"
            f"├ 💬 ردود تلقائية ذكية (200+ رد)\n"
            f"├ 👮 أوامر إدارة متكاملة\n"
            f"├ 🎮 ألعاب تفاعلية واقتصاد\n"
            f"└ 🌙 وضع ليلي ذكي\n\n"
            f"👇 استخدم الأزرار في الأسفل للتنقل 🚀",
            reply_markup=main_inline_keyboard(me.username)
        )

    @router.message(F.text.in_([
        "🕋 القسم الديني", "🎵 تحميل الصوتيات",
        "📚 المكتبة والثقافة", "🖼️ الافتارات",
        "🏦 البنك والألعاب", "📋 جروباتي",
        "⚙️ الإعدادات", "ℹ️ معلومات البوت",
    ]))
    async def menu_keyboard_handler(msg: Message):
        text = msg.text
        chat = msg.chat

        if text == "🕋 القسم الديني":
            from handlers.private.religious import religious_keyboard
            await msg.answer(
                "🕋 <b>القسم الديني</b>\n━━━━━━━━━━━━━━\n📖 قرآن | 📿 أذكار | 🤲 أدعية",
                reply_markup=religious_keyboard()
            )
        elif text == "🎵 تحميل الصوتيات":
            from handlers.private.media import media_keyboard
            await msg.answer(
                "🎵 <b>تحميل الصوتيات والفيديو</b>\n━━━━━━━━━━━━━━\n📥 أرسل رابط يوتيوب للتحميل",
                reply_markup=media_keyboard()
            )
        elif text == "📚 المكتبة والثقافة":
            from handlers.private.library import library_keyboard
            await msg.answer(
                "📚 <b>المكتبة والثقافة</b>\n━━━━━━━━━━━━━━\n📖 اقتباسات | 📚 كتب | 💡 معلومات",
                reply_markup=library_keyboard()
            )
        elif text == "🖼️ الافتارات":
            from handlers.private.avatars import avatars_keyboard
            await msg.answer(
                "🖼️ <b>الافتارات والتصميم</b>\n━━━━━━━━━━━━━━\n🖼️ افتارات | 🖌 جداريات",
                reply_markup=avatars_keyboard()
            )
        elif text == "🏦 البنك والألعاب":
            from handlers.private.economy import bank_keyboard
            await msg.answer(
                "🏦 <b>البنك والألعاب</b>\n━━━━━━━━━━━━━━\n💰 رصيد | 🎮 ألعاب | 🏆 ترتيب",
                reply_markup=bank_keyboard()
            )
        elif text == "📋 جروباتي":
            await show_my_groups(msg)
        elif text == "⚙️ الإعدادات":
            from handlers.private.settings import private_settings_keyboard
            await msg.answer(
                "⚙️ <b>الإعدادات المتطورة</b>\n━━━━━━━━━━━━━━\n🔧 تحكم في إعدادات مجموعاتك",
                reply_markup=private_settings_keyboard()
            )
        elif text == "ℹ️ معلومات البوت":
            me = await msg.bot.me()
            txt = (
                f"🤖 <b>معلومات ريو</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"📛 <b>الاسم:</b> {me.full_name}\n"
                f"🆔 <b>الأيدي:</b> <code>{me.id}</code>\n"
                f"🔗 <b>اليوزر:</b> @{me.username}\n"
                f"📝 <b>الإصدار:</b> 3.0\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"🛡️ <b>ريو</b> - نظام حماية وإدارة متكامل\n"
                f"├ حماية فولاذية\n"
                f"├ نظام تحقق بشري\n"
                f"├ ردود تلقائية ذكية\n"
                f"└ أوامر إدارة متكاملة\n\n"
                f"➕ <b>لإضافة البوت:</b>\n"
                f"أضف البوت لمجموعتك وارفعه مشرف!"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ إضافة البوت", url=f"https://t.me/{me.username}?startgroup=start")],
            ])
            await msg.answer(txt, reply_markup=keyboard)

    return router


async def show_my_groups(msg: Message, user=None):
    if user is None:
        user = msg.from_user
    from database import db
    groups = await db.get_user_admin_groups(user.id)

    if not groups:
        await msg.answer(
            "📋 <b>جروباتي</b>\n━━━━━━━━━━━━━━\n"
            "لا توجد مجموعات مسجلة.\n\n"
            "💡 أضف البوت لمجموعتك وارفعه مشرف،\n"
            "ثم أرسل <b>تفعيل</b> في المجموعة لتفعيلها."
        )
        return

    lines = ["📋 <b>جروباتي</b>\n━━━━━━━━━━━━━━"]
    keyboard = []
    for g in groups:
        status = "✅" if g["is_active"] else "❌"
        title = g["title"] or f"المجموعة {g['chat_id']}"
        lines.append(f"{status} <b>{title}</b>")
        keyboard.append([InlineKeyboardButton(text=f"{status} {title[:25]}", callback_data=f"mygroup_{g['chat_id']}")])
    lines.append("━━━━━━━━━━━━━━")
    lines.append("👇 اختر مجموعة للإعدادات")
    keyboard.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")])

    await msg.answer("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
