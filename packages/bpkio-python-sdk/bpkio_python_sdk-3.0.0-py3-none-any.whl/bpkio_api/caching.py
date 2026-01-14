import os
import tempfile
from typing import Optional

import diskcache
from loguru import logger

from .helpers.recorder import SessionComment, SessionRecorder

CACHE: diskcache.Cache | None = None


def init_cache(fqdn, tenant_id):
    temp_dir = tempfile.gettempdir()
    cache_dir = os.path.join(temp_dir, "bpkio_sdk", str(fqdn), str(tenant_id))

    global CACHE
    CACHE = diskcache.Cache(cache_dir)
    logger.debug("Cache folder: " + cache_dir)


def cache_api_results(
    key: str, ttl: int = 120, key_suffix_from_arg: Optional[str] = None
):
    """Decorator to retrieve and/or store the results of an API helper method into Cache"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = key
            if key_suffix_from_arg and key_suffix_from_arg in kwargs:
                cache_key = (
                    f"{cache_key}_{key_suffix_from_arg}={kwargs[key_suffix_from_arg]}"
                )

            global CACHE
            if CACHE is not None and cache_key in CACHE:
                logger.debug(f"Cache entry found for '{cache_key}'")
                SessionRecorder.record(SessionComment("Cache hit"))
                return CACHE[cache_key]
            result = func(*args, **kwargs)
            if CACHE is not None:
                CACHE.set(key=cache_key, value=result, expire=ttl)
                logger.debug(f"Adding cache entry for '{cache_key}'")
            return result

        return wrapper

    return decorator


def invalidate_cache(key: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            global CACHE
            if CACHE is not None and key in CACHE:
                del CACHE[key]
                logger.debug("Cache for '{key}' cleared")
            return result

        return wrapper

    return decorator


def clear_cache_entry(key: str):
    global CACHE
    if CACHE is not None and key in CACHE:
        del CACHE[key]
        logger.debug(f"Cache for '{key}' cleared")


def clear_cache():
    global CACHE
    if CACHE is not None:
        CACHE.clear()
        logger.debug("Cache cleared")
