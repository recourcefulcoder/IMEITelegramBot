import os
import datetime
from typing import Final


IMEICHECK_URL: Final = "https://api.imeicheck.net/v1/checks"
IMEICHECK_TOKEN: Final = os.getenv("IMEICHECK_TOKEN")
BOTFILE_NAME: Final = "bot.py"

BOT_TOKEN: Final = os.getenv("BOT_TOKEN")
ID_WHITELIST: Final = {7835373811}

API_PASSWORD: Final = os.getenv("API_BOT_PASSWORD")
API_BOT_USERNAME: Final = os.getenv("API_BOT_USERNAME", default="TELEGRAM_BOT")

HOSTNAME: Final = os.getenv("HOSTNAME", default="localhost")

JWT_SECRET_KEY: Final = os.getenv("SECRET_KEY")
POSTGRES_PASSWORD: Final = os.getenv("POSTGRES_PASSWORD", "postgres")
REDIS_URL: Final = f"redis://{HOSTNAME}:6379"
REFRESH_TOKEN_EXPIRE: datetime.timedelta = datetime.timedelta(days=14)
