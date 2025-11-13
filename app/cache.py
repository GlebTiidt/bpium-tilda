"""Primitive in-memory TTL cache to reduce load on Bpium API."""
from __future__ import annotations

import threading
import time
from typing import Callable, Generic, Optional, TypeVar


T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl = ttl_seconds
        self._value: Optional[T] = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def get_or_create(self, factory: Callable[[], T]) -> T:
        now = time.time()
        with self._lock:
            if self._value is not None and now < self._expires_at:
                return self._value

            value = factory()
            self._value = value
            self._expires_at = now + self.ttl
            return value

    def clear(self) -> None:
        with self._lock:
            self._value = None
            self._expires_at = 0.0
