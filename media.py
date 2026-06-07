import os
import re
import tempfile

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

YT_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/\S+",
    re.IGNORECASE
)


def media_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔙 العودة", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def PrivateMediaRouter() -> Router:
    router = Router(name="private_media")

    @router.message(F.text, F.chat.type == "private")
    async def handle_youtube_link(msg: Message):
        text = msg.text.strip()
        match = YT_PATTERN.search(text)
        if not match:
            return

        url = match.group(0)
        if not url.startswith("http"):
            url = "https://" + url

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎵 صوت MP3", callback_data=f"dl_audio|{url}"),
                InlineKeyboardButton(text="🎬 فيديو MP4", callback_data=f"dl_video|{url}"),
            ],
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="main_menu")],
        ])
        await msg.reply(
            f"📥 <b>تم اكتشاف رابط يوتيوب!</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"اختر صيغة التحميل:",
            reply_markup=keyboard
        )

    @router.callback_query(F.data.startswith("dl_"))
    async def process_download(cq: CallbackQuery):
        await cq.answer("جاري التحميل...")
        parts = cq.data.split("|", 1)
        if len(parts) != 2:
            return
        dl_type = parts[0]  # dl_audio or dl_video
        url = parts[1]

        status_msg = await cq.message.edit_text("⏳ <b>جاري تحميل الملف...</b>\nيرجى الانتظار...")

        try:
            import yt_dlp

            temp_dir = tempfile.gettempdir()
            output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

            ydl_opts = {
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
            }

            if dl_type == "dl_audio":
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            else:
                ydl_opts["format"] = "best[height<=720]"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if dl_type == "dl_audio":
                    filename = filename.rsplit(".", 1)[0] + ".mp3"

                title = info.get("title", "file")
                duration = info.get("duration", 0)
                duration_str = f"{duration//60}:{duration%60:02d}" if duration else "غير معروف"

                if not os.path.exists(filename):
                    await status_msg.edit_text("❌ <b>فشل التحميل:</b> لم يتم العثور على الملف.")
                    return

                file_size = os.path.getsize(filename)
                if file_size > 50 * 1024 * 1024:  # 50MB limit for Telegram
                    await status_msg.edit_text(
                        f"❌ <b>الملف كبير جداً!</b>\n"
                        f"حجم الملف: {file_size // (1024*1024)}MB\n"
                        f"الحد الأقصى: 50MB"
                    )
                    os.remove(filename)
                    return

                caption = (
                    f"📥 <b>تم التحميل</b>\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"📌 {title}\n"
                    f"⏱ المدة: {duration_str}\n"
                    f"━━━━━━━━━━━━━━"
                )

                if dl_type == "dl_audio":
                    await status_msg.answer_audio(
                        audio=open(filename, "rb"),
                        caption=caption,
                        title=title[:255],
                        performer="ريو بوت"
                    )
                else:
                    await status_msg.answer_video(
                        video=open(filename, "rb"),
                        caption=caption
                    )

                await status_msg.delete()
                os.remove(filename)

        except ImportError:
            await status_msg.edit_text(
                "❌ <b>مكتبة التحميل غير متوفرة.</b>\n"
                "يرجى التأكد من تثبيت yt-dlp:\n"
                "<code>pip install yt-dlp</code>"
            )
        except Exception as e:
            error_msg = str(e)[:200]
            await status_msg.edit_text(
                f"❌ <b>فشل التحميل:</b>\n<code>{error_msg}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
                ])
            )

    return router
