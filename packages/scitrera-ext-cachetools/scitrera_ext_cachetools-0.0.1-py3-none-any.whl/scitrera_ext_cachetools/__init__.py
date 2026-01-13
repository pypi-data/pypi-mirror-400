from os import getenv as _getenv

from cachetools import cached, cachedmethod
from cachetools import Cache, TTLCache, TLRUCache, LRUCache, FIFOCache, RRCache, LFUCache
from cachetools import keys
from asyncache import cached as cached_async, cachedmethod as cachedmethod_async

from scitrera_app_framework.util import ext_parse_bool


def cached_in_production(cache_decorator, *args, **kwargs):
    """
    "Meta-decorator" for cached/cachedmethod (or async variants: cached_async/cachedmethod_async).
    Meant to make it easy to test stuff without memoization in development and then with memoization
    in production without having to make any code changes. Memoization is always in place unless
    the environment variable "DEV_NOCACHE" evaluates to True/1/yes/etc.

    Args:
        cache_decorator: the selected cache decorator from cachetools or asyncache [or actually anywhere...]
        *args: the arguments for the cache decorator
        **kwargs: the keyword arguments for the cache decorator

    Returns:
        Either the original function if environment variable "DEV_NOCACHE" evaluates to True/1/yes/etc. OR
        otherwise the memoized function.
    """

    def decorator(func):
        if ext_parse_bool(_getenv('DEV_NOCACHE', False)):
            return func
        return cache_decorator(*args, **kwargs)(func)

    return decorator


__all__ = (
    'cached_in_production', 'cached', 'cachedmethod', 'cached_async', 'cachedmethod_async',
    'Cache', 'TTLCache', 'TLRUCache', 'TTLCache', 'LRUCache', 'FIFOCache', 'RRCache', 'LFUCache',
    'keys',
)
