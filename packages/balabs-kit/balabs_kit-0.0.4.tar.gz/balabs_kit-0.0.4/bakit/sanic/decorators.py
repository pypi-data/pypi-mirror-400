def no_cache(handler):
    """
    Mark a view (function or class-based) as non-cacheable.

    When applied to:
      • Function views — the decorated function will never be cached.
      • Class-based views (HTTPMethodView subclasses) — all HTTP methods
        on the view will bypass the cache middleware.

    The cache middleware checks for this marker and skips both reading from
    and writing to the cache for any matching route.

    Use this decorator when a route must always produce fresh output or when
    caching would cause incorrect behavior.
    """
    handler.disable_cache = True
    return handler
