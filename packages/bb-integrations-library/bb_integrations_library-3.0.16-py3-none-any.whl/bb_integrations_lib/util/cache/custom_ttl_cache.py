import time
from loguru import logger
from typing import TypeVar, Callable, Dict, Tuple, Any
import asyncio

T = TypeVar('T')

class CustomTTLCache:
    def __init__(self, verbose: bool = False):
        self.caches: dict = {}
        self.verbose = verbose

    def _is_expired(self, timestamp: float) -> bool:
        return time.time() > timestamp

    def ttl_cache(self, seconds: int,  cache_key: str):
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            def wrapper(*args, **kwargs):
                if cache_key in self.caches:
                    value, expires_at = self.caches[cache_key]
                    if time.time() < expires_at:
                        if self.verbose:
                            logger.info(f"Cache HIT for {cache_key}")
                        return value
                    else:
                        if self.verbose:
                            logger.info(f"Cache EXPIRED for {cache_key}")
                        del self.caches[cache_key]
                else:
                    if self.verbose:
                        logger.info(f"Cache MISS for {cache_key}")
                result = func(*args, **kwargs)
                expires_at = time.time() + seconds
                self.caches[cache_key] = (result, expires_at)
                if self.verbose:
                    logger.info(
                        f"Cached result for {cache_key} (expires at {time.strftime('%H:%M:%S', time.localtime(expires_at))})")
                return result
            return wrapper
        return decorator


class CustomAsyncTTLCache:
    def __init__(self, verbose: bool = False):
        self.caches: Dict[str, Tuple[Any, float]] = {}
        self.verbose = verbose
        self.locks: Dict[str, asyncio.Lock] = {}

    def _is_expired(self, timestamp: float) -> bool:
        return time.time() > timestamp

    async def get_or_set(self, cache_key: str, seconds: int, fetch_func, *args, **kwargs):
        if cache_key not in self.locks:
            self.locks[cache_key] = asyncio.Lock()
        async with self.locks[cache_key]:
            if cache_key in self.caches:
                value, expires_at = self.caches[cache_key]
                if time.time() < expires_at:
                    if self.verbose:
                        logger.info(f"Cache HIT for {cache_key}")
                    return value
                else:
                    if self.verbose:
                        logger.info(f"Cache EXPIRED for {cache_key}")
                    del self.caches[cache_key]
            else:
                if self.verbose:
                    logger.info(f"Cache MISS for {cache_key}")
            result = await fetch_func(*args, **kwargs)
            expires_at = time.time() + seconds
            self.caches[cache_key] = (result, expires_at)
            if self.verbose:
                logger.info(
                    f"Cached result for {cache_key} (expires at {time.strftime('%H:%M:%S', time.localtime(expires_at))})")
            return result