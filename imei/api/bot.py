import os
import sys
from pathlib import Path
from typing import Final
import logging
import asyncio

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import aiohttp

from dotenv import load_dotenv
from utils import imei_valid

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = os.path.join(BASE_DIR.parent, ".env")
load_dotenv(env_file)


TOKEN: Final = os.environ["BOT_TOKEN"]
BOT_USERNAME: Final = "IMEI_API_BOT"


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("imei"))
async def imei_handler(message: Message) -> None:
    # try:
    text = message.text.strip("imei/ ")

    # log.info(text)
    if not imei_valid(text):
        await message.answer("invalid IMEI!")
        return
    # except TypeError as e:
    #     await message.answer(f"INVALID MESSAGE, error occurred: {e}")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://127.0.0.1:8000/api/check-imei?imei={text}&token=4562") as response:
            log = logging.getLogger(__name__)
            ans = await response.json()
            text = await response.text()
            # log.info(ans)
            log.info(text)
            await message.answer(f"IMEI DATA:\n{ans}")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
