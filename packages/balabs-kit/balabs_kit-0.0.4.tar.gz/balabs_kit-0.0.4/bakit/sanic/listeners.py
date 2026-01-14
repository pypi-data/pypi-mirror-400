import logging

import sentry_sdk
from aiocache import caches
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from bakit import settings

log = logging.getLogger(__name__)


async def setup_cache_listener(app):
    if not app.config.CACHE_MIDDLEWARE_ENABLED:
        log.debug("Caching disabled")
        app.ctx.cache = None
        return

    caches.set_config(
        {
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "db": settings.REDIS_DB,
                "timeout": 3,
                "serializer": {"class": "aiocache.serializers.PickleSerializer"},
            }
        }
    )
    app.ctx.cache = caches.get("default")


async def setup_sentry_listener(_):
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        send_default_pii=True,
        integrations=[AsyncioIntegration(), LoggingIntegration(event_level="WARNING")],
    )
