import os

from config import load_environ

load_environ(levels=2)

BOT_NAME = os.getenv("API_BOT_USERNAME", default="TELEGRAM_BOT")
BOT_PASSWORD = os.getenv("API_BOT_PASSWORD")
