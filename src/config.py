import datetime
import json
import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv


def load_environ():
    BASE_DIR = Path(__file__).resolve().parent
    env_file = os.path.join(BASE_DIR.parent, ".env")
    if os.path.isfile(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv(os.path.join(BASE_DIR, ".env.example"))


load_environ()
IMEICHECK_URL: Final = "https://api.imeicheck.net/v1/checks"
IMEICHECK_TOKEN: Final = os.getenv("IMEICHECK_TOKEN")
BOTFILE_NAME: Final = "api/bot.py"

BOT_TOKEN: Final = os.getenv("BOT_TOKEN")
with open("whitelist.json", mode="r") as file:
    ID_WHITELIST: Final = set(json.load(file))

API_PASSWORD: Final = os.getenv("API_BOT_PASSWORD")
API_BOT_USERNAME: Final = os.getenv("API_BOT_USERNAME", default="TELEGRAM_BOT")

HOSTNAME: Final = os.getenv("HOSTNAME", default="localhost")
SANIC_DEBUG: Final = os.getenv("SANIC_DEBUG", default="false").lower() in [
    "true",
    "yes",
    "y",
    "1",
]

JWT_SECRET_KEY: Final = os.getenv("SECRET_KEY")

REDIS_URL: Final = f"redis://{HOSTNAME}:6379"
REFRESH_TOKEN_EXPIRE: datetime.timedelta = datetime.timedelta(days=14)
ACCESS_TOKEN_EXPIRE: datetime.timedelta = datetime.timedelta(minutes=15)

POSTGRES_PASSWORD: Final = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_USER: Final = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB: Final = os.getenv("POSTGRES_DB")
