import os
import subprocess
from pathlib import Path

import aiohttp

from api.auth import BP_NAME, TokenManager

import config


async def start_subprocesses(app, loop):
    """Starting a Telegram bot and Redis storage for refresh tokens"""
    app.config.token_manager = TokenManager()
    await app.config.token_manager.init_redis()
    if config.SANIC_DEBUG:
        subprocess.Popen(
            "redis-server --port 6379",
            shell=True,
        )  # running Redis storage

    headers = {
        "Authorization": "Bearer " + app.config.IMEICHECK_TOKEN,
        "Content-Type": "application/json",
    }
    app.ctx.aiohttp_session = aiohttp.ClientSession(headers=headers)

    main_end = app.url_for("check-imei")
    refresh_end = app.url_for(f"{BP_NAME}.refresh")
    login_end = app.url_for(f"{BP_NAME}.login")

    command = (
        f"python {app.config.BOTFILE_NAME} --login-end {login_end} "
        f"--refresh-end {refresh_end} --main-end {main_end}"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent) + (
        ":" + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )  # this is done to allow bot.py import "config.py" file, stored
    # in main project's directory

    subprocess.Popen(
        command,
        shell=True,
        env=env,
    )  # running Telegram Bot


async def close_session(app, loop):
    await app.ctx.aiohttp_session.close()
