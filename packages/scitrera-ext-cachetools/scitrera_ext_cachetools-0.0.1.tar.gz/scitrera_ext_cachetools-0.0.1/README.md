# scitrera-ext-cachetools

`scitrera-ext-cachetools` is a metapackage that combines [`cachetools`](https://github.com/tkem/cachetools) and [`asyncache`](https://github.com/hephex/asyncache) to make them all conveniently available under a single namespace.

It provides both synchronous and asynchronous caching decorators and various cache implementations (TTL, LRU, LFU, etc.) out of the box.

## Installation

```bash
pip install scitrera-ext-cachetools
```

## Features

- **Unified Access**: Import everything you need for caching from one place.
- **Sync & Async Support**: Includes `cachetools` for synchronous code and `asyncache` for `asyncio`.
- **Conditional Caching**: Includes `cached_in_production`, a utility to easily disable caching in development environments.

## Available Exports

From `scitrera_ext_cachetools`, you can import:

- **Decorators**: `cached`, `cachedmethod`, `cached_async`, `cachedmethod_async`
- **Cache Types**: `Cache`, `TTLCache`, `TLRUCache`, `LRUCache`, `FIFOCache`, `RRCache`, `LFUCache`
- **Utilities**: `keys`, `cached_in_production`

## `cached_in_production`

The only new functionality provided by this package is the `cached_in_production` decorator. It is a "meta-decorator" designed to make it easy to test code without memoization during development while ensuring it is enabled in production, without requiring code changes.

Caching is **enabled by default** unless the environment variable `DEV_NOCACHE` is set to `True`, `1`, `yes`, or other truthy values (parsed via `scitrera-app-framework`).

### Usage Example

#### Synchronous Caching

```python
from scitrera_ext_cachetools import cached_in_production, TTLCache, cached

@cached_in_production(cached, cache=TTLCache(maxsize=100, ttl=300))
def get_expensive_data(key):
    # This logic will be cached in production, 
    # but can be bypassed in dev by setting DEV_NOCACHE=1
    return ...
```

#### Asynchronous Caching

```python
from scitrera_ext_cachetools import cached_in_production, TTLCache, cached_async

@cached_in_production(cached_async, cache=TTLCache(maxsize=100, ttl=300))
async def get_expensive_data_async(key):
    return ...
```

## License

This project is licensed under the BSD-3-Clause License.
