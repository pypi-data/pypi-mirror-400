import hashlib

from sanic import response

from bakit import settings


def _build_cache_key(request):
    """
    Redis-safe cache key.

    Uses SHA-256 of method + path + query so we avoid unsafe chars and
    overlong keys while still being deterministic.
    """
    raw = "|".join(
        [
            request.method or "",
            request.path or "",
            request.query_string or "",
        ]
    )

    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"sanic-cache:{digest}"


def _is_no_cache(request):
    handler = getattr(request.route, "handler", None)
    if handler is None:
        return False

    # Function views
    if getattr(handler, "disable_cache", False):
        return True

    # Class-based views: handler.view_class is the HTTPMethodView subclass
    view_class = getattr(handler, "view_class", None)
    if view_class is not None and getattr(view_class, "disable_cache", False):  # noqa: SIM103
        return True
    return False


async def cache_middleware_request(request):
    app = request.app
    if not app.config.CACHE_MIDDLEWARE_ENABLED:
        return

    if request.method != "GET" or not getattr(request, "route", None):
        return

    # Skip if decorated with @no_cache
    if _is_no_cache(request):
        return

    key = _build_cache_key(request)
    cache = app.ctx.cache

    cached = await cache.get(key)
    if cached is not None:
        # mark that this request is served from cache
        request.ctx.response_from_cache = True
        return response.raw(
            cached["body"],
            status=cached["status"],
            headers=cached["headers"],
            content_type=cached["content_type"],
        )


async def cache_middleware_response(request, response):
    # If response came from cache, do nothing
    if getattr(request.ctx, "response_from_cache", False):
        return

    app = request.app
    if not app.config.CACHE_MIDDLEWARE_ENABLED:
        return

    if request.method != "GET" or not getattr(request, "route", None):
        return

    # Skip if decorated with @no_cache
    if _is_no_cache(request):
        return

    if response.status != 200:
        return

    key = _build_cache_key(request)
    cache = app.ctx.cache

    payload = {
        "body": response.body,  # bytes
        "status": response.status,
        "headers": list(response.headers.items()),
        "content_type": response.content_type,
    }
    await cache.set(key, payload, ttl=settings.CACHE_MIDDLEWARE_SECONDS)
