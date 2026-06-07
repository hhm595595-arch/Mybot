import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import db

from handlers.group.protection import ProtectionMiddleware
from handlers.group.admin import GroupAdminRouter
from handlers.group.auto_reply import GroupAutoReplyRouter
from handlers.group.welcome import GroupWelcomeRouter
from handlers.group.misc import GroupMiscRouter
from handlers.group.social import GroupSocialRouter
from handlers.private.start import PrivateStartRouter
from handlers.private.owner import OwnerRouter
from handlers.private.menu import PrivateMenuRouter
from handlers.private.economy import PrivateEconomyRouter
from handlers.private.games import PrivateGamesRouter
from handlers.private.settings import PrivateSettingsRouter
from handlers.private.religious import PrivateReligiousRouter
from handlers.private.media import PrivateMediaRouter
from handlers.private.library import PrivateLibraryRouter
from handlers.private.avatars import PrivateAvatarsRouter

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

async def night_mode_worker(bot: Bot):
    last_announced = {}
    from datetime import datetime
    while True:
        try:
            now = datetime.now()
            today_str = now.strftime("%Y%m%d")
            
            rows = await db._fetchall("SELECT chat_id, night_mode, night_start, night_end FROM groups WHERE is_active=1 AND night_mode=1")
            for row in rows:
                chat_id = row["chat_id"]
                start_h = row["night_start"]
                end_h = row["night_end"]
                
                if now.hour == start_h:
                    key = f"start_{today_str}"
                    if last_announced.get(chat_id) != key:
                        last_announced[chat_id] = key
                        try:
                            await bot.send_message(
                                chat_id, 
                                "🌙 <b>تم بدء الوضع الليلي في الجروب!</b>\n"
                                "━━━━━━━━━━━━━━━━━\n"
                                "🚫 لن يُسمح لأحد بإرسال الرسائل (ما عدا مالك الجروب).\n"
                                f"⏳ يستمر الوضع حتى الساعة {end_h}:00."
                            )
                        except:
                            pass
                elif now.hour == end_h:
                    key = f"end_{today_str}"
                    if last_announced.get(chat_id) != key:
                        last_announced[chat_id] = key
                        try:
                            await bot.send_message(
                                chat_id, 
                                "☀️ <b>انتهى الوضع الليلي!</b>\n"
                                "━━━━━━━━━━━━━━━━━\n"
                                "✅ يمكنكم الآن المراسلة بشكل طبيعي.\n"
                                "صباح الخير جميعاً 🌸"
                            )
                        except:
                            pass
        except Exception as e:
            logger.error(f"Night mode worker error: {e}")
            
        await asyncio.sleep(60)

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await db.connect()
    logger.info("Database connected")

    # Register Middleware
    dp.message.middleware(ProtectionMiddleware())

    # Register routers
    dp.include_router(GroupAdminRouter())
    dp.include_router(GroupWelcomeRouter())
    dp.include_router(GroupMiscRouter())
    dp.include_router(GroupSocialRouter())
    dp.include_router(OwnerRouter())
    dp.include_router(PrivateStartRouter())
    dp.include_router(PrivateMenuRouter())
    dp.include_router(PrivateEconomyRouter())
    dp.include_router(PrivateGamesRouter())
    dp.include_router(PrivateSettingsRouter())
    dp.include_router(PrivateReligiousRouter())
    dp.include_router(PrivateMediaRouter())
    dp.include_router(PrivateLibraryRouter())
    dp.include_router(PrivateAvatarsRouter())
    dp.include_router(GroupAutoReplyRouter())

    commands = [
        BotCommand(command="start", description="القائمة الرئيسية 🚀"),
        BotCommand(command="help", description="قائمة الأوامر 📋"),
    ]

    logger.info("Setting bot commands...")
    await bot.set_my_commands(commands)

    # Start background tasks
    asyncio.create_task(night_mode_worker(bot))

    logger.info("🚀 Rio bot started!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
