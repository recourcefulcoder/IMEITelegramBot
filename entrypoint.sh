#!/usr/bin/env sh

cd src
alembic upgrade head
sanic server:create_app --host=0.0.0.0
