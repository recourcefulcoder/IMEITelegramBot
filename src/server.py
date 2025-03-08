from contextvars import ContextVar

from api.auth import bp as auth_bp, protected

from database.engine import create_bind

from listeners import close_session, start_subprocesses

from sanic import Sanic, json

from sqlalchemy.ext.asyncio import async_sessionmaker


_sessionmaker = async_sessionmaker(create_bind(), expire_on_commit=False)
_base_model_session_ctx = ContextVar("session")


def create_app():
    app = Sanic("IMEI")
    app.update_config("./config.py")

    app.blueprint(auth_bp)

    app.register_listener(start_subprocesses, "after_server_start")
    app.register_listener(close_session, "before_server_stop")

    @app.middleware("request")
    async def inject_db_session_inside(request):
        request.ctx.session = _sessionmaker()
        request.ctx.session_ctx_token = _base_model_session_ctx.set(
            request.ctx.session
        )

    @app.middleware("response")
    async def close_db_session_inside(request, response):
        if hasattr(request.ctx, "session_ctx_token"):
            _base_model_session_ctx.reset(request.ctx.session_ctx_token)
            await request.ctx.session.close()

    @app.post("/check-imei", name="check-imei")
    @protected
    async def get_imei_info_inside(request):
        payload = {
            "deviceId": request.args.get("imei"),
            "serviceId": 15,
        }

        async with app.ctx.aiohttp_session.post(
            app.config.IMEICHECK_URL, json=payload
        ) as response:
            ans = await response.json()
        return json(ans)

    return app


if __name__ == "__main__":
    create_app().run()
