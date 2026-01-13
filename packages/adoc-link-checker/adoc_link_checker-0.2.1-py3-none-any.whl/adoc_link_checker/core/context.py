import threading
from typing import Optional


class LinkCheckContext:
    """
    Shared, thread-safe context for link checking.

    Responsibilities:
    - store global configuration (timeout, blacklist)
    - cache URL check results to avoid duplicate HTTP calls
    """

    def __init__(self, timeout: int, blacklist: list[str]):
        self.timeout = timeout
        self.blacklist = blacklist

        self._cache: dict[str, bool] = {}
        self._lock = threading.Lock()

    def get_cached(self, url: str) -> Optional[bool]:
        """
        Return cached result for URL if present, else None.
        """
        with self._lock:
            return self._cache.get(url)

    def set_cached(self, url: str, result: bool) -> None:
        """
        Store URL check result in cache.
        """
        with self._lock:
            self._cache[url] = result

    def clear_cache(self) -> None:
        """
        Clear the URL cache (useful for tests or repeated runs).
        """
        with self._lock:
            self._cache.clear()
