import random
import re
from datetime import datetime
from aiogram.types import ChatMemberUpdated, Chat
from aiogram.enums import ChatMemberStatus

# Arabic character normalization
_AR_NORM = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه"})


def norm(text: str) -> str:
    return text.lower().strip().translate(_AR_NORM)


def is_command(text: str, *commands) -> bool:
    lower = text.strip().lower()
    for cmd in commands:
        if lower == cmd or lower == f"/{cmd}":
            return True
    return False


async def is_admin(chat: Chat, user_id: int) -> bool:
    try:
        member = await chat.get_member(user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        return False


async def is_group_admin(event, user_id: int) -> bool:
    return await is_admin(event.chat, user_id)


def random_id(length: int = 8) -> str:
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def format_date(dt: datetime = None) -> str:
    dt = dt or datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
