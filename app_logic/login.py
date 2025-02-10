import datetime
import os
from http import HTTPStatus
from pathlib import Path

from dotenv import load_dotenv

import jwt

from sanic import Blueprint, json

login = Blueprint("login", url_prefix="/login")

BASE_DIR = Path(__file__).resolve().parent
env_file = os.path.join(BASE_DIR.parent, ".env")
if os.path.isfile(env_file):
    load_dotenv(env_file)
else:
    load_dotenv(os.path.join(BASE_DIR, ".env.example"))

BOT_PASSWORD = os.getenv("API_BOT_PASSWORD")


refresh_tokens = dict()


def generate_token(identity, secret, is_refresh=False):
    exp_time = datetime.datetime.utcnow() + (
        datetime.timedelta(days=7)
        if is_refresh
        else datetime.timedelta(hours=1)
    )
    payload = {
        "sub": identity,
        "exp": exp_time,
        "type": "refresh" if is_refresh else "access",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@login.post("/", name="login")
async def do_login(request):
    data = request.json()
    if not data or data.get("password") != BOT_PASSWORD:
        return json({"error": "Invalid credentials"}, HTTPStatus.UNAUTHORIZED)

    access_token = generate_token("bot", request.app.config.SECRET)
    refresh_token = generate_token(
        "bot", request.app.config.SECRET, is_refresh=True
    )
    refresh_tokens[refresh_token] = "bot"  # Store refresh token

    return json(
        {"access_token": access_token, "refresh_token": refresh_token},
        HTTPStatus.OK,
    )
