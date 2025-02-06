import os
import sys
from pathlib import Path
from typing import Final
import logging
import asyncio
import argparse

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

import aiohttp

from dotenv import load_dotenv
from utils import imei_valid


BASE_DIR = Path(__file__).resolve().parent
env_file = os.path.join(BASE_DIR.parent, ".env")
load_dotenv(env_file)
if os.path.isfile(env_file):
    load_dotenv(env_file)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env.example"))

parser = argparse.ArgumentParser()
parser.add_argument(
    "--api-path", dest="api_path", type=str, help="Add product_id"
)
args = parser.parse_args()


TOKEN: Final = os.getenv("BOT_TOKEN")
BOT_USERNAME: Final = "IMEI_API_BOT"
API_APP_NAME: Final = os.getenv("APP_NAME")
API_PATH: Final = args.api_path

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


async def on_startup():
    session = aiohttp.ClientSession()
    await dp.storage.set_data(key="storage", data={"session": session})


async def on_shutdown():
    data = await dp.storage.get_data("storage")
    session: aiohttp.ClientSession = data["session"]
    await session.close()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("imei"))
async def imei_handler(message: Message) -> None:
    text = message.text.strip("imei/ ")

    await message.answer(
        f"Your imei ({text}) was taken into execution; expect answer"
    )

    if not imei_valid(text):
        await message.answer("invalid IMEI!")
        return

    data = await dp.storage.get_data("storage")
    session: aiohttp.ClientSession = data["session"]

    params = {
        "imei": text,
        "token": 4512,
    }

    async with session.get(API_PATH, params=params) as response:
        log = logging.getLogger(__name__)
        ans = await response.json()
        text = await response.text()
        log.info(text)
        await message.answer(f"IMEI DATA:\n{ans}")


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    await on_startup()

    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
