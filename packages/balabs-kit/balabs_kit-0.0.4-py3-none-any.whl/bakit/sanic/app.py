import hashlib
import hmac
from pathlib import Path

from orjson import dumps
from sanic import Sanic
from sanic.response import text
from sanic_ext import Extend
from tortoise.contrib.sanic import register_tortoise

from bakit import settings
from bakit.sanic.listeners import setup_cache_listener, setup_sentry_listener
from bakit.sanic.middlewares import cache_middleware_request, cache_middleware_response
from bakit.settings import APP_NAME, LOGGING_CONFIG, TORTOISE_ORM
from bakit.utils.metrics import view_metrics

STATIC_DIR = Path(__file__).resolve().parent / "static"

_SENTRY_DEBUG_DIGEST = (
    "b2cded34bf480236d91e54b631185347f52321b1fdc8c40b89ca507d3a1458ee"
)
_SENTRY_DEBUG_KEY = b"sentry-debug-v1"


def create_base_app(app_name=APP_NAME, log_config=LOGGING_CONFIG, is_testing=False):
    app = Sanic(app_name, strict_slashes=True, log_config=log_config, dumps=dumps)
    app.config.FALLBACK_ERROR_FORMAT = "json"

    app.config.CACHE_MIDDLEWARE_ENABLED = settings.CACHE_MIDDLEWARE_ENABLED

    app.config.CORS_ORIGINS = settings.CORS_ORIGINS
    app.config.CORS_METHODS = settings.CORS_METHODS

    Extend(app)

    app.static("/favicon.ico", STATIC_DIR / "favicon.png")

    # listeners
    app.register_listener(setup_cache_listener, "before_server_start")
    app.register_listener(setup_sentry_listener, "before_server_start")

    # middleware
    app.register_middleware(cache_middleware_request, "request")
    app.register_middleware(cache_middleware_response, "response")

    # /ping/ endpoint is needed for load balancer health checks. Do not remove.
    @app.route("/ping/", methods=["GET"])
    @view_metrics()
    async def health(request):
        return text("pong", status=200)

    # /sentry-debug/ endpoint is used for testing sentry integration. Do not remove.
    @app.route("/sentry-debug/", methods=["GET"])
    @view_metrics()
    async def sentry_debug(request):
        secret = request.args.get("secret")
        if not secret:
            return text("not found", status=404)

        digest = hmac.new(
            _SENTRY_DEBUG_KEY, secret.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(digest, _SENTRY_DEBUG_DIGEST):
            return text("not found", status=404)

        a = 1 / 0
        return text(str(a), status=500)

    # Setup Tortoise ORM
    if not is_testing:
        register_tortoise(
            app,
            config=TORTOISE_ORM,
            generate_schemas=False,
        )

    return app
