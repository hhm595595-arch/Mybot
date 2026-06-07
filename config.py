import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

BOT_NAME = "ريو"
BOT_NAME_EN = "Rio"
BOT_VERSION = "3.0"

# Protection defaults
FLOOD_COUNT = 5
FLOOD_SECONDS = 3
FLOOD_MUTE_DURATION = 300
WARN_LIMIT = 3
LONG_MSG_LIMIT = 700
CAPTCHA_TIMEOUT = 120
