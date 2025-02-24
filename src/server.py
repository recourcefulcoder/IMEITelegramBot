import os
import subprocess
from contextvars import ContextVar
from http import HTTPStatus
from pathlib import Path

import aiohttp

from api.auth import TokenManager, protected

import config

import database.models as models
from database.engine import bind

from dotenv import load_dotenv

from sanic import Sanic, json

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.sql.expression import select


BASE_DIR = Path(__file__).resolve().parent
env_file = os.path.join(BASE_DIR.parent, ".env")
if os.path.isfile(env_file):
    load_dotenv(env_file)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env.example"))


app = Sanic("IMEI")
app.update_config("./config.py")

_sessionmaker = async_sessionmaker(bind, expire_on_commit=False)
_base_model_session_ctx = ContextVar("session")

token_manager = TokenManager()


@app.after_server_start
async def start_subprocesses(app):
    """Starting a Telegram bot and Redis storage for refresh tokens"""
    await token_manager.init_redis()
    subprocess.Popen(
        "redis-server --port 6379",
        shell=True,
    )  # running Redis storage

    headers = {
        "Authorization": "Bearer " + app.config.IMEICHECK_TOKEN,
        "Content-Type": "application/json",
    }
    app.ctx.aiohttp_session = aiohttp.ClientSession(headers=headers)

    async with bind.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    main_end = app.url_for("check-imei")
    refresh_end = app.url_for("refresh")
    login_end = app.url_for("login")

    command = (
        f"python {app.config.BOTFILE_NAME} --login-end {login_end} "
        f"--refresh-end {refresh_end} --main-end {main_end}"
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR) + (
        ":" + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )  # this is done to allow bot.py import "config.py" file, stored
    # in main project's directory

    subprocess.Popen(
        command,
        shell=True,
        env=env,
    )  # running Telegram Bot


@app.before_server_stop
async def close_session(app):
    await app.ctx.aiohttp_session.close()


@app.middleware("request")
async def inject_db_session(request):
    request.ctx.session = _sessionmaker()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(
        request.ctx.session
    )


@app.middleware("response")
async def close_db_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


@app.post("/login", name="login")
async def do_login(request):
    data = request.json
    if not data or "password" not in data or "username" not in data:
        return json(
            {
                "error": "Invalid credential format: "
                "missing username and/or password"
            },
            HTTPStatus.UNAUTHORIZED,
        )
    async with request.ctx.session as session:
        async with session.begin():
            result = await session.execute(
                select(models.User).where(
                    models.User.username == data["username"]
                )
            )
            user = result.scalar()
            if not user or not user.check_password(data["password"]):
                return json(
                    {"error": "Invalid password"},
                    HTTPStatus.UNAUTHORIZED,
                )

    access_token = await TokenManager.create_access_token(data["username"])
    refresh_token = await token_manager.create_refresh_token(data["username"])

    return json(
        {"access_token": access_token, "refresh_token": refresh_token},
        HTTPStatus.OK,
    )


@app.post("/refresh", name="refresh")
async def refresh(request):
    refresh_token = request.json.get("refresh_token")

    if not refresh_token:
        return json(
            {"error": "Missing refresh token"}, status=HTTPStatus.UNAUTHORIZED
        )

    username = await token_manager.verify_refresh_token(refresh_token)

    if not username:
        return json(
            {"error": "Invalid refresh token"}, status=HTTPStatus.UNAUTHORIZED
        )

    await token_manager.delete_refresh_token(username)

    new_refresh_token = await token_manager.create_refresh_token(username)
    new_access_token = await TokenManager.create_access_token(username)

    return json(
        {"access_token": new_access_token, "refresh_token": new_refresh_token},
        HTTPStatus.OK,
    )


@app.post("/check-imei", name="check-imei")
@protected
async def get_imei_info(request):
    payload = {
        "deviceId": request.args.get("imei"),
        "serviceId": 15,
    }

    async with app.ctx.aiohttp_session.post(
        app.config.IMEICHECK_URL, json=payload
    ) as response:
        ans = await response.json()
    return json(ans)


if __name__ == "__main__":
    app.run()
