import re
import sys

from environs import Env

env = Env()

APP_NAME = env("APP_NAME")

CORS_ORIGINS = [
    re.compile(r"^http://(localhost|127\.0\.0\.1):\d+$"),
    re.compile(r"^https://(\S+\.)?vercel\.app$"),
    re.compile(r"^https://(\S+\.)?blockanalitica\.com$"),
]
CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]


TORTOISE_ORM = {
    "connections": {
        "default": env("APP_DB_URL"),
    },
    "apps": {
        "core": {
            "models": [],
            "default_connection": "default",
        },
    },
}


SENTRY_DSN = env("SENTRY_DSN", "")

STATSD_HOST = env("STATSD_HOST", "")
STATSD_PORT = env("STATSD_PORT", default=8125)
STATSD_PREFIX = env("STATSD_PREFIX", default=APP_NAME)

REDIS_HOST = env("REDIS_HOST", "")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 2)

CACHE_MIDDLEWARE_SECONDS = 5
CACHE_MIDDLEWARE_ENABLED = env.bool("CACHE_MIDDLEWARE_ENABLED", False)

APP_LOG_LEVEL = env("APP_LOG_LEVEL", default="INFO")
TORTOISE_LOG_LEVEL = env("TORTOISE_LOG_LEVEL", default="WARNING")
DEFAULT_LOG_LEVEL = env("DEFAULT_LOG_LEVEL", default="WARNING")
ARQ_LOG_LEVEL = env("ARQ_LOG_LEVEL", default="INFO")
CHAIN_HARVESTER_LOG_LEVEL = env("CHAIN_HARVESTER_LOG_LEVEL", default="WARNING")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": (
                "[%(asctime)s] %(name)s {%(module)s:%(lineno)d} "
                "PID=%(process)d [%(levelname)s] - %(message)s"
            ),
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
        },
    },
    "loggers": {
        "bakit": {
            "propagate": True,
            "level": APP_LOG_LEVEL,
        },
        "core": {
            "propagate": True,
            "level": APP_LOG_LEVEL,
        },
        "tortoise": {
            "propagate": True,
            "level": TORTOISE_LOG_LEVEL,
        },
        "tortoise.db_client": {
            "propagate": True,
            "level": TORTOISE_LOG_LEVEL,
        },
        "arq": {
            "propagate": True,
            "level": ARQ_LOG_LEVEL,
        },
        "arq.worker": {
            "propagate": True,
            "level": ARQ_LOG_LEVEL,
        },
        "chain_harvester": {
            "propagate": True,
            "level": CHAIN_HARVESTER_LOG_LEVEL,
        },
        "": {
            "level": DEFAULT_LOG_LEVEL,
            "handlers": ["console"],
        },
    },
}
