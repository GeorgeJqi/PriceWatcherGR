import time
import threading
from typing import Any, Optional, Dict, Tuple

class SimpleCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            record = self._store.get(key)
            if not record:
                return None
            data, expire_at = record
            if time.time() > expire_at:
                del self._store[key]
                return None
            return data

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expire_at = time.time() + ttl_seconds
        with self._lock:
            self._store[key] = (value, expire_at)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

cache = SimpleCache()
