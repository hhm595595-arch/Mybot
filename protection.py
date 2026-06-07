import asyncio
import re
import time
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message, ChatPermissions
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command

from config import FLOOD_COUNT, FLOOD_SECONDS, FLOOD_MUTE_DURATION, LONG_MSG_LIMIT
from database import db
from utils.helpers import is_admin, norm

LINK_PATTERN = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.IGNORECASE)
MEDIA_PATTERN = re.compile(r"(https?://)?(www\.)?(tiktok\.com|instagram\.com|facebook\.com|x\.com|twitter\.com)/\S+", re.IGNORECASE)

flood_tracker: dict = {}
media_flood_tracker: dict = {}

DEFAULT_BAD_WORDS = [
    "كس", "كسم", "شرموط", "خرة", "زبالة", "منحوس", "يلعن", "اللعنة",
    "fuck", "shit", "bitch", "asshole", "damn", "bastard",
    "احا", "احاا", "خول", "متناك", "قحبة", "عرص", "ابن القحبة",
    "منيك", "نييك", "كسمك", "كسمها",
]


class ProtectionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not isinstance(event, Message):
            return await handler(event, data)
            
        msg = event
        chat = msg.chat
        user = msg.from_user
        if not chat or chat.type not in ("group", "supergroup") or not user or user.is_bot:
            return await handler(event, data)

        chat_id = chat.id
        user_id = user.id

        text_to_print = msg.text or msg.caption or "[No Text]"
        print(f"====> [MIDDLEWARE] Received '{text_to_print}' in chat {chat_id} (type: {chat.type}) from {user.full_name}")

        await db.ensure_group(chat_id, chat.title or "")

        if not await db.is_group_active(chat_id):
            return await handler(event, data)

        # ── Strict Night Mode (Owner only bypass) ──
        owner_id = await db.get_owner(chat_id)
        if user_id != owner_id:
            night_info = await db.get_night_mode(chat_id)
            if night_info["enabled"]:
                current_hour = datetime.now().hour
                start_h = night_info["start"]
                end_h = night_info["end"]
                
                is_night = False
                if start_h > end_h:
                    if current_hour >= start_h or current_hour < end_h:
                        is_night = True
                else:
                    if start_h <= current_hour < end_h:
                        is_night = True
                        
                if is_night:
                    try:
                        await msg.delete()
                    except:
                        pass
                    return

        if await is_admin(chat, user_id):
            return await handler(event, data)

        await db.add_message(chat_id, user_id)
        
        # ── Add XP and Level Up ──
        level_up_info = await db.add_xp(chat_id, user_id, 1)
        if level_up_info and level_up_info[0]:
            try:
                await msg.answer(
                    f"🎉 <b>مبروووك!</b> يا {user.full_name}\n"
                    f"🌟 لقد ارتفع مستواك إلى <b>{level_up_info[1]}</b>!\n"
                    f"🎁 استمر في التفاعل للوصول للقمة."
                )
            except Exception:
                pass

        link_enabled = await db.get_setting(chat_id, "link_protection")
        flood_enabled = await db.get_setting(chat_id, "anti_flood")
        bad_words_enabled = await db.get_setting(chat_id, "bad_words_filter")
        forward_enabled = await db.get_setting(chat_id, "forward_protection")
        media_protection = await db.get_setting(chat_id, "media_protection")
        bot_protection = await db.get_setting(chat_id, "bot_protection")
        long_msg_protection = await db.get_setting(chat_id, "long_msg_protection")
        warn_limit = await db.get_warn_limit(chat_id)

        # ── Bot Protection: kick new bots ──
        if bot_protection and msg.new_chat_members:
            for new_user in msg.new_chat_members:
                if new_user.is_bot:
                    try:
                        await chat.ban(new_user.id)
                        await msg.answer(
                            f"🤖 <b>تم حظر بوت!</b>\n"
                            f"━━━━━━━━━━━━━━━━━\n"
                            f"📛 @{new_user.username or new_user.full_name}\n"
                            f"👤 بواسطة: الحماية التلقائية"
                        )
                    except Exception:
                        pass
            return

        text = msg.text or msg.caption or ""

        # ── Media Spam Protection ──
        if media_protection and not text and any([
            msg.sticker, msg.animation, msg.photo, msg.video,
            msg.video_note, msg.document, msg.voice, msg.audio
        ]):
            now = time.time()
            key = f"media:{chat_id}:{user_id}"
            if key not in media_flood_tracker:
                media_flood_tracker[key] = []
            media_flood_tracker[key].append(now)
            media_flood_tracker[key] = [t for t in media_flood_tracker[key] if now - t < 10]
            if len(media_flood_tracker[key]) > 8:
                try:
                    await _mute_user(chat, user_id, 600)
                    await msg.delete()
                    notification = await msg.answer(
                        f"🔇 <b>تم كتم</b> {user.full_name}\n"
                        f"⚠️ السبب: سبام ميديا\n"
                        f"⏳ المدة: 10 دقائق"
                    )
                    asyncio.create_task(_delete_after(notification, 10))
                except Exception:
                    pass
                media_flood_tracker[key] = []
                return

        if not text:
            return await handler(event, data)

        # ── Forward Protection ──
        if forward_enabled and msg.forward_from_chat:
            try:
                await msg.delete()
                warns = await db.add_warn(chat_id, user_id, "إعادة توجيه من قناة")
                remaining = warn_limit - warns
                if remaining <= 0:
                    await _ban_user(chat, user_id)
                    await msg.answer(
                        f"🚫 <b>تم حظر</b> {user.full_name}\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"⚠️ السبب: إعادة توجيه (بلوغ {warn_limit} إنذارات)"
                    )
                else:
                    await msg.answer(
                        f"🚫 <b>ممنوع إعادة التوجيه من القنوات!</b>\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"👤 {user.full_name}\n"
                        f"⚠️ إنذار {warns}/{warn_limit} ─ 📌 المتبقي: {remaining}"
                    )
            except Exception:
                pass
            return

        # ── Bad Words Filter ──
        if bad_words_enabled:
            custom_words = await db.get_bad_words(chat_id)
            all_words = list(set(DEFAULT_BAD_WORDS + custom_words))
            lower_text = norm(text)
            found_word = None
            for word in all_words:
                if word in lower_text:
                    found_word = word
                    break
            if found_word:
                try:
                    await msg.delete()
                    warns = await db.add_warn(chat_id, user_id, f"كلمة ممنوعة: {found_word}")
                    remaining = warn_limit - warns
                    if remaining <= 0:
                        await _ban_user(chat, user_id)
                        await msg.answer(
                            f"🚫 <b>تم حظر</b> {user.full_name}\n"
                            f"━━━━━━━━━━━━━━━━━\n"
                            f"⚠️ السبب: كلمات ممنوعة (بلوغ {warn_limit} إنذارات)"
                        )
                    else:
                        notification = await msg.answer(
                            f"🚫 <b>ممنوع استخدام الكلمات الغير لائقة!</b>\n"
                            f"━━━━━━━━━━━━━━━━━\n"
                            f"👤 {user.full_name}\n"
                            f"⚠️ إنذار {warns}/{warn_limit} ─ 📌 المتبقي: {remaining}"
                        )
                        asyncio.create_task(_delete_after(notification, 5))
                except Exception:
                    pass
                return

        # ── Social Media Links ──
        if link_enabled and MEDIA_PATTERN.search(text):
            try:
                await msg.delete()
                warns = await db.add_warn(chat_id, user_id, "رابط منصات تواصل")
                remaining = warn_limit - warns
                if remaining <= 0:
                    await _ban_user(chat, user_id)
                    await msg.answer(
                        f"🚫 <b>تم حظر</b> {user.full_name}\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"⚠️ السبب: روابط تواصل (بلوغ {warn_limit} إنذارات)"
                    )
                else:
                    notification = await msg.answer(
                        f"⚠️ <b>ممنوع إرسال روابط التواصل!</b>\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"👤 {user.full_name}\n"
                        f"⚠️ إنذار {warns}/{warn_limit} ─ 📌 المتبقي: {remaining}"
                    )
                    asyncio.create_task(_delete_after(notification, 5))
            except Exception:
                pass
            return

        # ── Link Protection ──
        if link_enabled and LINK_PATTERN.search(text):
            try:
                await msg.delete()
                warns = await db.add_warn(chat_id, user_id, "إرسال رابط")
                remaining = warn_limit - warns
                if remaining <= 0:
                    await _ban_user(chat, user_id)
                    await msg.answer(
                        f"🚫 <b>تم حظر</b> {user.full_name}\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"⚠️ السبب: روابط (بلوغ {warn_limit} إنذارات)"
                    )
                else:
                    notification = await msg.answer(
                        f"⚠️ <b>ممنوع إرسال الروابط!</b>\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"👤 {user.full_name}\n"
                        f"⚠️ إنذار {warns}/{warn_limit} ─ 📌 المتبقي: {remaining}"
                    )
                    asyncio.create_task(_delete_after(notification, 5))
            except Exception:
                pass
            return

        # ── Long Message Filter ──
        if long_msg_protection and len(text) > LONG_MSG_LIMIT:
            try:
                await msg.delete()
                await msg.answer(
                    f"⛔ <b>الرسائل الطويلة ممنوعة!</b>\n"
                    f"━━━━━━━━━━━━━━━━━\n"
                    f"👤 {user.full_name}\n"
                    f"📊 عدد الأحرف: {len(text)} (الحد: {LONG_MSG_LIMIT})"
                )
            except Exception:
                pass
            return

        # ── Anti-Flood ──
        if flood_enabled:
            now = time.time()
            key = f"{chat_id}:{user_id}"
            if key not in flood_tracker:
                flood_tracker[key] = []
            flood_tracker[key].append(now)
            flood_tracker[key] = [t for t in flood_tracker[key] if now - t < FLOOD_SECONDS]
            if len(flood_tracker[key]) > FLOOD_COUNT:
                try:
                    await _mute_user(chat, user_id, FLOOD_MUTE_DURATION)
                    await msg.delete()
                    notification = await msg.answer(
                        f"🔇 <b>تم كتم</b> {user.full_name}\n"
                        f"━━━━━━━━━━━━━━━━━\n"
                        f"⚠️ السبب: سبام وتكرار\n"
                        f"⏳ المدة: {FLOOD_MUTE_DURATION//60} دقائق"
                    )
                    asyncio.create_task(_delete_after(notification, 10))
                except Exception:
                    pass
                flood_tracker[key] = []
                return

        # If it survived all protections, proceed to other handlers
        return await handler(event, data)


async def _mute_user(chat, user_id: int, duration: int):
    until = datetime.now() + timedelta(seconds=duration)
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
    )
    await chat.restrict(user_id, permissions, until_date=until)


async def _ban_user(chat, user_id: int):
    await chat.ban(user_id)


async def _delete_after(message, seconds: int):
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except Exception:
        pass
