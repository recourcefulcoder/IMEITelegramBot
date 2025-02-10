import os
import subprocess
from http import HTTPStatus
from pathlib import Path
from typing import Final

import aiohttp

from dotenv import load_dotenv

import login as app_login

from sanic import Sanic, json

import ujson

# from auth import protected


BASE_DIR = Path(__file__).resolve().parent
env_file = os.path.join(BASE_DIR.parent, ".env")
if os.path.isfile(env_file):
    load_dotenv(env_file)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env.example"))


IMEICHECK_URL: Final = "https://api.imeicheck.net/v1/checks"
IMEICHECK_TOKEN: Final = os.getenv("IMEICHECK_TOKEN")
BOTFILE_NAME: Final = "bot.py"
with open(os.path.join(BASE_DIR.parent, "tokens.json"), "r") as f:
    TOKENS: Final = ujson.load(f)

app = Sanic("IMEI")
app.config.SECRET = os.getenv("SECRET_KEY")
app.blueprint(app_login.login)


@app.after_server_start
async def start_bot(app):
    headers = {
        "Authorization": "Bearer " + IMEICHECK_TOKEN,
        "Content-Type": "application/json",
    }
    app.ctx.aiohttp_session: aiohttp.ClientSession = aiohttp.ClientSession(
        headers=headers
    )
    main_end = app.url_for(
        "check-imei",
    )

    refresh_end = app.url_for(
        "refresh",
    )

    command = (
        f"python {BOTFILE_NAME} --login-end login/ "
        f"--refresh-end {refresh_end} --main-end {main_end}"
    )

    subprocess.Popen(
        command,
        shell=True,
    )


@app.before_server_stop
async def close_session(app):
    await app.ctx.aiohttp_session.close()


@app.post("/refresh")
async def refresh(request):
    data = request.json
    refresh_token = data.get("refresh_token")

    if not refresh_token or refresh_token not in app_login.refresh_tokens:
        return json(
            {"error": "Invalid refresh token"}, status=HTTPStatus.UNAUTHORIZED
        )

    new_access_token = app_login.generate_token(
        app_login.refresh_tokens[refresh_token]
    )
    return json({"access_token": new_access_token}, HTTPStatus.OK)


@app.post("/check-imei", name="check-imei")
# @protected
async def get_imei_info(request):
    payload = {
        "deviceId": request.args.get("imei"),
        "serviceId": 15,
    }

    async with app.ctx.aiohttp_session.post(
        IMEICHECK_URL, json=payload
    ) as response:
        ans = await response.json()
    return json(ans)


if __name__ == "__main__":
    app.run()
