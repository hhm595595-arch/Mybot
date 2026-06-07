import asyncio
import random
import time
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.enums import ChatMemberStatus

from config import CAPTCHA_TIMEOUT
from database import db
from utils.helpers import format_date


CAPTCHA_TASKS = {}


async def _kick_after_timeout(chat_id, user_id, full_name, captcha_msg, bot):
    await asyncio.sleep(CAPTCHA_TIMEOUT)
    captcha = await db.get_captcha(chat_id, user_id)
    if not captcha:
        return

    await db.delete_captcha(chat_id, user_id)
    CAPTCHA_TASKS.pop((chat_id, user_id), None)

    try:
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)
        await captcha_msg.edit_text(
            f"❌ <b>تم طرد</b> {full_name}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"⚠️ السبب: لم يجتاز التحقق البشري في الوقت المحدد.\n"
            f"⏳ المهلة: {CAPTCHA_TIMEOUT//60} دقائق"
        )
    except Exception:
        pass


def GroupWelcomeRouter() -> Router:
    router = Router(name="group_welcome")

    @router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
    async def on_new_member(event):
        chat = event.chat
        user = event.new_chat_member.user
        if user.is_bot:
            return

        chat_id = chat.id
        user_id = user.id

        await db.ensure_group(chat_id, chat.title or "")
        captcha_enabled = await db.get_setting(chat_id, "captcha")
        welcome_enabled = await db.get_setting(chat_id, "welcome")

        now = format_date()
        await db.set_join_date(chat_id, user_id, now)
        await db.set_captcha_passed(chat_id, user_id, 0)

        if captcha_enabled is not False:
            num1 = random.randint(1, 25)
            num2 = random.randint(1, 25)
            op = random.choice(["+", "-"])
            if op == "-":
                if num1 < num2:
                    num1, num2 = num2, num1
                answer = str(num1 - num2)
            else:
                answer = str(num1 + num2)

            await db.save_captcha(chat_id, user_id, answer, time.time())

            try:
                await chat.restrict(
                    user_id,
                    ChatPermissions(can_send_messages=False),
                    until_date=datetime.now().timestamp() + CAPTCHA_TIMEOUT,
                )

                captcha_msg = await event.answer(
                    f"🔐 <b>🔒 التحقق البشري</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👋 أهلاً <b>{user.full_name}</b>! 🎊\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"للتأكد من أنك إنسان، قم بحل المسألة التالية:\n\n"
                    f"🧮 <b>{num1} {op} {num2} = ؟</b>\n\n"
                    f"⌛️ لديك <b>{CAPTCHA_TIMEOUT//60} دقائق</b> للإجابة\n"
                    f"━━━━━━━━━━━━━━━━━━━"
                )

                task = asyncio.create_task(
                    _kick_after_timeout(chat_id, user_id, user.full_name, captcha_msg, event.bot)
                )
                CAPTCHA_TASKS[(chat_id, user_id)] = task

            except Exception:
                await db.delete_captcha(chat_id, user_id)
            return

        if welcome_enabled is not False:
            await send_welcome(event, chat, user)

    async def has_captcha_filter(msg: Message) -> bool:
        if not msg.from_user or msg.from_user.is_bot:
            return False
        captcha = await db.get_captcha(msg.chat.id, msg.from_user.id)
        return bool(captcha)

    @router.message(F.chat.type.in_({"group", "supergroup"}), F.text, has_captcha_filter)
    async def captcha_answer_check(msg: Message):
        user = msg.from_user
        chat = msg.chat

        captcha = await db.get_captcha(chat.id, user.id)

        if msg.text.strip() == captcha["answer"]:
            try:
                await chat.restrict(
                    user.id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                    ),
                )
            except Exception:
                pass

            await db.set_captcha_passed(chat.id, user.id, 1)
            await db.delete_captcha(chat.id, user.id)

            task = CAPTCHA_TASKS.pop((chat.id, user.id), None)
            if task:
                task.cancel()

            await msg.reply(
                f"✅ <b>🎉 تم التحقق بنجاح!</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 <b>{user.full_name}</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎊 مرحباً بك في الجروب!\n"
                f"📜 القوانين: أرسل <b>القوانين</b> لعرضها"
            )

            welcome_enabled = await db.get_setting(chat.id, "welcome")
            if welcome_enabled is not False:
                await send_welcome(msg, chat, user)
        else:
            try:
                await msg.delete()
            except Exception:
                pass

    # ── Bot added / promoted ──
    @router.my_chat_member()
    async def bot_added_to_group(event):
        chat = event.chat
        if chat.type not in ("group", "supergroup"):
            return

        new_status = event.new_chat_member.status
        old_status = event.old_chat_member.status

        await db.ensure_group(chat.id, chat.title or "")

        if old_status == ChatMemberStatus.MEMBER and new_status == ChatMemberStatus.ADMINISTRATOR:
            await send_activation_prompt(event, chat)

        elif old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED) and \
             new_status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
            try:
                admins = await chat.get_administrators()
                for admin in admins:
                    if admin.status == ChatMemberStatus.CREATOR:
                        await db.track_admin(chat.id, admin.user.id)
                        await db._execute(
                            "UPDATE groups SET owner_id=? WHERE chat_id=?", [admin.user.id, chat.id]
                        )
                    elif admin.status == ChatMemberStatus.ADMINISTRATOR:
                        await db.track_admin(chat.id, admin.user.id)
            except Exception:
                pass

            # Auto-activate
            await db.activate_group(chat.id, event.from_user.id, event.from_user.id, format_date())
            await db.track_admin(chat.id, event.from_user.id)

            try:
                await event.answer(
                    f"🎊 <b>🎉 شكراً لإضافتي للمجموعة!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"تم تفعيل البوت تلقائياً والتعرف على المجموعة.\n"
                    f"✅ <b>أنا الآن جاهز لحماية المجموعة!</b>\n"
                    f"⚠️ (إذا لم تكن رفعتني مشرفاً، يرجى رفعي لكي أتمكن من حذف الرسائل)"
                )
            except Exception:
                pass
            
            try:
                await event.bot.send_message(
                    event.from_user.id,
                    f"✅ <b>تم إضافة البوت بنجاح للمجموعة!</b>\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"📛 اسم المجموعة: <b>{chat.title}</b>\n"
                    f"🆔 أيدي المجموعة: <code>{chat.id}</code>\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"⚙️ يمكنك التحكم بإعداداتها من خلال قسم <b>الإعدادات المطورة</b>."
                )
            except Exception:
                pass

            if new_status == ChatMemberStatus.ADMINISTRATOR:
                await send_activation_prompt(event, chat)

    return router


async def send_activation_prompt(event, chat):
    try:
        admins = await chat.get_administrators()
        owner_name = ""
        for admin in admins:
            if admin.status == ChatMemberStatus.CREATOR:
                owner_name = admin.user.full_name
                await db.track_admin(chat.id, admin.user.id)
                await db._execute(
                    "UPDATE groups SET owner_id=? WHERE chat_id=?", [admin.user.id, chat.id]
                )
            elif admin.status == ChatMemberStatus.ADMINISTRATOR:
                await db.track_admin(chat.id, admin.user.id)
    except Exception:
        owner_name = ""

    text = (
        f"🎊 <b>🚀 تم رفعي مشرفاً!</b> 🎊\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👋 أهلاً بـ <b>{chat.title}</b>!\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>الصلاحيات الممنوحة:</b>\n"
        f"├ 🗑️ حذف الرسائل ✅\n"
        f"├ 🚫 حظر وتقييد ✅\n"
        f"├ 📌 تثبيت ✅\n"
        f"└ 👥 دعوة أعضاء ✅\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👑 المالك: <b>{owner_name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>البوت الآن يمتلك الصلاحيات كاملة</b>\n"
        f"🛡️ وهو يعمل بكفاءة 100% لحماية الجروب."
    )

    try:
        await event.answer(text)
    except Exception:
        pass


async def send_welcome(event_or_msg, chat, user):
    chat_id = chat.id
    uid = user.id
    name = user.full_name
    username = f"@{user.username}" if user.username else "لا يوجد"
    profile_link = f"tg://user?id={uid}"

    row = await db._fetchone("SELECT owner_id FROM groups WHERE chat_id=?", [chat_id])
    owner_name = "المالك"
    if row and row["owner_id"]:
        try:
            owner_member = await chat.get_member(row["owner_id"])
            owner_name = owner_member.user.first_name or "المالك"
        except:
            pass

    import datetime
    now_dt = datetime.datetime.now()
    d_str = now_dt.strftime("%Y/%m/%d")
    t_str = now_dt.strftime("%I:%M%p").replace("AM", "AM").replace("PM", "PM")

    custom_welcome = await db.get_setting(chat_id, "custom_welcome")
    if custom_welcome:
        welcome_text = custom_welcome
        welcome_text = welcome_text.replace("{{الاسم}}", name)\
            .replace("{{الايدي}}", str(uid))\
            .replace("{{اليوزر}}", username)\
            .replace("{{الرابط}}", profile_link)
    else:
        welcome_text = (
            f"⦃ {chat.title} ترحب بك ⦄\n"
            f"⦃ 『{owner_name}』 المـالك\" ⦄\n"
            f"⌯——— {chat.title} ———⌯\n"
            f"⌯ نورت قروبنا يـ ⦃ {name} ⦄ .\n"
            f"⌯ ايديك ⟸ ⦃ <span class='tg-spoiler'>{uid}</span> ⦄\n"
            f"⌯ يوزرك ⟸ ⦃ <span class='tg-spoiler'>{username}</span> ⦄\n"
            f"⌯——— {chat.title} ———⌯\n"
            f"⦃ شكرآ ل انظمامك يرجئ الالتزام بلقوانين ⦄\n"
            f"⦃ تاريخ انضمامك ☜ {d_str}\n"
            f"⦃ الساعة ☜ {t_str} ."
        )

    try:
        photos = await event_or_msg.bot.get_user_profile_photos(uid, limit=1)
        if photos and photos.photos:
            photo = photos.photos[0][-1].file_id
            await event_or_msg.answer_photo(photo=photo, caption=welcome_text)
        else:
            await event_or_msg.answer(welcome_text)
    except Exception:
        try:
            await event_or_msg.answer(welcome_text)
        except Exception:
            pass
