from typing import Protocol


class CustomTTLCacheProtocol(Protocol):
    def _is_expired(self, timestamp: float) -> bool:
        """Checks if cache is expired"""

    def ttl_cache(self, seconds: int, cache_key: str):
        """Wrapper function to manage a custom ttl object"""