from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
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


def PrivateMenuRouter() -> Router:
    router = Router(name="private_menu")

    @router.callback_query(F.data == "main_menu")
    async def back_to_main(cq: CallbackQuery):
        await cq.answer()
        me = await cq.bot.me()
        await cq.message.delete()
        await cq.message.answer(
            f"🎊 🌟 مرحباً بك في ريو (Rio)! 🌟\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 الاسم: {cq.from_user.full_name}\n"
            f"🆔 الأيدي: <code>{cq.from_user.id}</code>\n"
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

    @router.callback_query(F.data == "my_groups")
    async def my_groups_callback(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.start import show_my_groups
        await show_my_groups(cq.message, cq.from_user)

    @router.callback_query(F.data == "bot_info")
    async def bot_info(cq: CallbackQuery):
        await cq.answer()
        me = await cq.bot.me()
        text = (
            f"🤖 <b>معلومات ريو</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"📛 <b>الاسم:</b> {me.full_name}\n"
            f"🆔 <b>الأيدي:</b> <code>{me.id}</code>\n"
            f"🔗 <b>اليوزر:</b> @{me.username}\n"
            f"📝 <b>الإصدار:</b> 3.0\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"🛡️ <b>ريو</b> - الإمبراطور الجديد لإدارة وحماية المجموعات\n"
            f"├ حماية فولاذية (روابط، تكرار، كلمات ممنوعة، توجيه)\n"
            f"├ نظام تحقق بشري (كابتشا)\n"
            f"├ نظام إنذارات وعقوبات تدريجي\n"
            f"├ ردود تلقائية ذكية\n"
            f"└ أوامر إدارة متكاملة\n\n"
            f"💬 <b>لإضافة البوت لمجموعتك:</b>\n"
            f"أضف البوت إلى مجموعتك وارفعه مشرف!\n"
            f"━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ إضافة البوت", url=f"https://t.me/{me.username}?startgroup=start")],
            [InlineKeyboardButton(text="🔙 العودة", callback_data="main_menu")],
        ])
        await cq.message.edit_text(text, reply_markup=keyboard)

    @router.callback_query(F.data == "section_religious")
    async def section_religious(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.religious import religious_keyboard
        await cq.message.edit_text(
            "🕋 <b>القسم الديني</b>\n"
            "━━━━━━━━━━━━━━\n"
            "📖 قرآن كريم | 📿 أذكار | 🤲 أدعية\n"
            "━━━━━━━━━━━━━━",
            reply_markup=religious_keyboard()
        )

    @router.callback_query(F.data == "section_media")
    async def section_media(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.media import media_keyboard
        await cq.message.edit_text(
            "🎵 <b>تحميل الصوتيات والفيديو</b>\n"
            "━━━━━━━━━━━━━━\n"
            "📥 أرسل رابط فيديو أو أغنية من يوتيوب للتحميل\n"
            "━━━━━━━━━━━━━━",
            reply_markup=media_keyboard()
        )

    @router.callback_query(F.data == "section_library")
    async def section_library(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.library import library_keyboard
        await cq.message.edit_text(
            "📚 <b>المكتبة والثقافة</b>\n"
            "━━━━━━━━━━━━━━\n"
            "📖 اقتباسات | 📚 كتب | 💡 معلومات\n"
            "━━━━━━━━━━━━━━",
            reply_markup=library_keyboard()
        )

    @router.callback_query(F.data == "section_avatars")
    async def section_avatars(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.avatars import avatars_keyboard
        await cq.message.edit_text(
            "🖼️ <b>الافتارات والتصميم</b>\n"
            "━━━━━━━━━━━━━━\n"
            "🖼️ افتارات جاهزة | ✏️ طلب تعديل | 🖌 جداريات\n"
            "━━━━━━━━━━━━━━",
            reply_markup=avatars_keyboard()
        )

    @router.callback_query(F.data == "section_bank")
    async def section_bank(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.economy import bank_keyboard
        await cq.message.edit_text(
            "🏦 <b>البنك والألعاب</b>\n"
            "━━━━━━━━━━━━━━\n"
            "💰 رصيدك | 🎁 راتبك اليومي | 🎮 العاب\n"
            "━━━━━━━━━━━━━━",
            reply_markup=bank_keyboard()
        )

    @router.callback_query(F.data == "section_settings")
    async def section_settings(cq: CallbackQuery):
        await cq.answer()
        from handlers.private.settings import private_settings_keyboard
        await cq.message.edit_text(
            "⚙️ <b>الإعدادات المتطورة</b>\n"
            "━━━━━━━━━━━━━━\n"
            "🔧 تحكم في إعدادات الحماية لمجموعاتك\n"
            "━━━━━━━━━━━━━━",
            reply_markup=private_settings_keyboard()
        )

    @router.callback_query(F.data.startswith("mygroup_"))
    async def my_group_settings(cq: CallbackQuery):
        await cq.answer()
        chat_id = int(cq.data.split("_", 1)[1])
        title = await db.get_group_title(chat_id) or f"المجموعة {chat_id}"
        is_active = await db.is_group_active(chat_id)
        activation = await db.get_activation_info(chat_id)
        night = await db.get_night_mode(chat_id)

        status = "✅ مفعل" if is_active else "❌ غير مفعل"
        txt = (
            f"⚙️ <b>{title}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"🆔 <code>{chat_id}</code>\n"
            f"📊 الحالة: {status}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔧 اختر إعداداً للتعديل:"
        )

        from handlers.private.settings import build_group_settings_keyboard
        await cq.message.edit_text(txt, reply_markup=build_group_settings_keyboard(chat_id, title))

    return router
