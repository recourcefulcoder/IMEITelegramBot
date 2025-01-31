from typing import Final, List
import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from django.urls import reverse
import aiohttp

from utils import imei_valid

# from utils.functions import imei_valid


TOKEN: Final = "7988436281:AAEvGkt6BsU3UiMRrFZ6jBV2nOIhTBhhr3w"
BOT_USERNAME: Final = "IMEI_API_BOT"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am \nG R U T")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type in IMEI so that I check it out")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No idea what I'm doing")


async def process_imei(
    imei: str, session: aiohttp.ClientSession
) -> (str, List[str]):
    # returns API response and list of errors
    # if not imei_valid(imei):
    async with session.post(
        reverse("api:imei_check", kwargs={"imei": imei, "token": "BOT_TOKEN"})
    ) as resp:
        return str(await resp.json()), []


async def imei_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide an IMEI number. Example: /imei 123456789012345"
        )
        return

    imei = context.args[0]
    if not imei_valid(imei):
        await update.message.reply_text(f"Invalid IMEI")
        return

    response, errors = await process_imei(imei, context.bot_data["session"])

    await update.message.reply_text(f"API Response: {response}")


def handle_response(text: str) -> str:
    if "hello" in text.lower():
        return "HIHIHIHIHI"
    return 'SOOOOO can you tell me "hello" pweeease???'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type

    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "text"')

    response: str = "default response for non-private messages"
    if message_type == "private":
        response: str = handle_response(text)

    print(f"Bot: {response}")
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


async def run_bot():
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    async with aiohttp.ClientSession() as session:
        app.bot_data["session"] = session
        handler = CommandHandler("imei", imei_command)

        app.add_handler(handler)

        app.add_error_handler(error)

        print("Polling...")
        app.run_polling(poll_interval=3)


if __name__ == "__main__":
    # print('main function cycle')
    try:
        print('try statement entrance')
        loop = asyncio.get_running_loop()
        loop.create_task(run_bot())  # Schedule the bot
    except RuntimeError:
        print('error raised')
        asyncio.run(run_bot())

__all__ = [
    "start_command",
    "help_command",
    "custom_command",
    "handle_message",
    "error",
]
