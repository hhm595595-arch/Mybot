import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8698455754:AAFBHjh-xQ_bDl6g2IV6RsUKsu5BaBNs3g8", "")
OWNER_ID = int(os.getenv("8698455754", 0))

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
