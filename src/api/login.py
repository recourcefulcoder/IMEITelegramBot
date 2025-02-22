import datetime

import jwt

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
