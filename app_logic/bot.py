import argparse
import asyncio
import logging
import os
import sys
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Dict, Final

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

import aiohttp

from utils import imei_valid

parser = argparse.ArgumentParser()
parser.add_argument(
    "--api-url",
    dest="api_url",
    type=str,
    help="API's base URL",
    default="http://localhost:8000",
)
parser.add_argument(
    "--login-end",
    dest="login_endpoint",
    type=str,
    help="API's login endpoint",
    default="/login",
)
parser.add_argument(
    "--refresh-end",
    dest="refresh_endpoint",
    type=str,
    help="API's refreshing token endpoint",
    default="/refresh",
)
parser.add_argument(
    "--main-end",
    dest="main_endpoint",
    type=str,
    help="API's main functionality endpoint",
    default="/check-imei",
)
args = parser.parse_args()


TOKEN: Final = os.getenv("BOT_TOKEN")
ID_WHITELIST: Final = {7835373811}

API_URL: Final = args.api_url
LOGIN_ENDPOINT: Final = args.login_endpoint
MAIN_ENDPOINT: Final = args.main_endpoint
REFRESH_ENDPOINT: Final = args.refresh_endpoint

API_PASSWORD: Final = os.getenv("API_BOT_PASSWORD")
API_BOT_USERNAME: Final = os.getenv("API_BOT_USERNAME", default="TELEGRAM_BOT")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


class TokenHolder:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None


token_holder = TokenHolder()


class AuthorizationError(BaseException):
    pass


@dp.message.outer_middleware()
async def user_allowed(
    handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: Dict[str, Any],
) -> Any:
    if event.from_user.id not in ID_WHITELIST:
        return await event.answer(
            f"Unauthorized: id {event.from_user.id} not allowed"
        )
    return await handler(event, data)


async def login(session: aiohttp.ClientSession):
    credentials = {
        "password": API_PASSWORD,
        "username": API_BOT_USERNAME,
    }
    async with session.post(
        f"{API_URL}{LOGIN_ENDPOINT}/", json=credentials
    ) as resp:
        data = await resp.json()
        if resp.status == HTTPStatus.OK:
            token_holder.access_token = data["access_token"]
            token_holder.refresh_token = data["refresh_token"]
        elif resp.status == HTTPStatus.UNAUTHORIZED:
            print(data, resp.status)
            raise AuthorizationError(
                "Critical error - invalid bot auth credentials!"
            )
        else:
            raise AiogramError("Unexpected server error on login")


async def refresh_token_func(session):
    """Refresh the access token"""
    async with session.post(
        f"{API_URL}{REFRESH_ENDPOINT}/",
        json={"refresh_token": token_holder.refresh_token},
    ) as resp:
        data = await resp.json()
        if resp.status == HTTPStatus.OK:
            token_holder.access_token = data["access_token"]
        else:
            raise AuthorizationError("Unexpected error occured")


async def on_startup():
    session = aiohttp.ClientSession()
    # login_task = asyncio.create_task(login(session))
    storage_task = asyncio.create_task(
        dp.storage.set_data(key="storage", data={"session": session})
    )

    # await login_task
    await storage_task


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

    async with session.post(
        f"{API_URL}{MAIN_ENDPOINT}/",
        params=params,
        headers={"Authorization": f"Bearer {token_holder.access_token}"},
    ) as response:
        log = logging.getLogger(__name__)
        text = await response.text()
        log.info(text)
        await message.answer(f"IMEI DATA:\n{text}")


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
