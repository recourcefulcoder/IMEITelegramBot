import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from typing import Final
from sanic import Sanic, json

import aiohttp


BASE_DIR = Path(__file__).resolve().parent
env_file = os.path.join(BASE_DIR.parent, ".env")
if os.path.isfile(env_file):
    load_dotenv(env_file)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env.example"))


IMEICHECK_URL: Final = "https://api.imeicheck.net/v1/checks"
IMEICHECK_TOKEN: Final = os.getenv("IMEICHECK_TOKEN")
BOTFILE_NAME: Final = "bot.py"

app = Sanic("IMEI")


@app.after_server_start
async def open_session(app):
    headers = {
        "Authorization": "Bearer " + IMEICHECK_TOKEN,
        "Content-Type": "application/json",
    }
    app.ctx.aiohttp_session: aiohttp.ClientSession = aiohttp.ClientSession(
        headers=headers
    )
    url = app.url_for(
        "check-imei",
        _external=True,
        _server="localhost:8000"
    )
    subprocess.Popen(
        f"python {BOTFILE_NAME} --api-path {url}",
        shell=True,
    )


@app.before_server_stop
async def close_session(app):
    await app.ctx.aiohttp_session.close()


@app.post("/check-imei", name="check-imei")
async def get_imei_info(request):
    token = request.token
    # auth for my API must be written later

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
