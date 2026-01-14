"""Agent cache with improved performance and monitoring."""

import asyncio
import logging
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TypeVar

DEFAULT_TTL = 3600
DEFAULT_MAX_SIZE = 100
DEFAULT_CLEANUP_INTERVAL = 60

T = TypeVar("T")


@dataclass
class TTLQueueConfig:
    """Configuration for TTLQueue."""

    default_ttl: int = DEFAULT_TTL
    max_size: int = DEFAULT_MAX_SIZE
    cleanup_interval: int = DEFAULT_CLEANUP_INTERVAL
    enable_stats: bool = True
    name: str = "TTLQueue"


class TTLQueueItem[T]:
    """TTL queue item with generic type."""

    def __init__(self, value: T, ttl: int = DEFAULT_TTL):
        """Initialize the TTL queue item."""
        if ttl <= 0:
            raise ValueError("TTL must be positive")
        self.value: T = value
        self.expire_at = time.time() + ttl

    def reset_ttl(self, ttl: int = DEFAULT_TTL):
        """Reset the TTL."""
        if ttl <= 0:
            raise ValueError("TTL must be positive")
        self.expire_at = time.time() + ttl

    def is_expired(self) -> bool:
        """Check if the item is expired."""
        return time.time() > self.expire_at


class TTLQueue[T]:
    """TTL queue with improved performance and monitoring."""

    def __init__(self, config: TTLQueueConfig | None = None):
        """Initialize the TTL queue."""
        self.config = config or TTLQueueConfig()

        if self.config.default_ttl <= 0:
            raise ValueError("Default TTL must be positive")

        self.name = self.config.name
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._items: dict[str, TTLQueueItem[T]] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._stats = defaultdict(int) if self.config.enable_stats else None

        # Start cleanup thread
        self._thread = threading.Thread(target=self._cleanup_task, daemon=True)
        self._thread.start()

        self.logger.info(
            f"TTLQueue '{self.name}' initialized with config: {self.config}"
        )

    def put(self, id: str, value: T, ttl: int | None = None) -> None:
        """Put the item into the queue with validation and size limit."""
        if not isinstance(id, str) or not id:
            raise ValueError("ID must be a non-empty string")

        if ttl is not None and ttl <= 0:
            raise ValueError("TTL must be positive")

        with self._lock:
            # Check size limit and evict oldest if necessary
            if len(self._items) >= self.config.max_size:
                self._evict_oldest()

            self._items[id] = TTLQueueItem(value, ttl or self.config.default_ttl)

            if self._stats is not None:
                self._stats["puts"] += 1

    def get(self, id: str) -> T | None:
        """Get the item from the queue with statistics."""
        if not isinstance(id, str):
            raise ValueError("ID must be a string")

        with self._lock:
            item = self._items.get(id)
            if item and not item.is_expired():
                item.reset_ttl(self.config.default_ttl)
                if self._stats is not None:
                    self._stats["hits"] += 1
                return item.value
            elif item:
                del self._items[id]
                if self._stats is not None:
                    self._stats["expired_gets"] += 1

            if self._stats is not None:
                self._stats["misses"] += 1
        return None

    def delete(self, id: str) -> bool:
        """Delete an item from the queue."""
        if not isinstance(id, str):
            raise ValueError("ID must be a string")

        with self._lock:
            if id in self._items:
                del self._items[id]
                if self._stats is not None:
                    self._stats["deletes"] += 1
                return True
        return False

    def clear(self) -> None:
        """Clear all items from the queue."""
        with self._lock:
            item_count = len(self._items)
            self._items.clear()
            if self._stats is not None:
                self._stats["clears"] += 1
            self.logger.info(f"Cleared {item_count} items from queue")

    def _evict_oldest(self) -> None:
        """Evict the oldest item when cache is full."""
        if not self._items:
            return

        oldest_key = min(self._items.keys(), key=lambda k: self._items[k].expire_at)
        del self._items[oldest_key]
        self.logger.debug(f"Evicted oldest item: {oldest_key}")

        if self._stats is not None:
            self._stats["evictions"] += 1

    def _cleanup_task(self) -> None:
        """Cleanup task with configurable interval."""
        while not self._stop_event.is_set():
            time.sleep(self.config.cleanup_interval)
            self._cleanup_expired_items()

    def _cleanup_expired_items(self) -> None:
        """Cleanup expired items with batch processing."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, item in self._items.items()
                if current_time > item.expire_at
            ]

            for key in expired_keys:
                del self._items[key]

            if expired_keys and self._stats is not None:
                self._stats["cleanup_removals"] += len(expired_keys)

            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired items")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for item in self._items.values() if current_time > item.expire_at
            )

            stats = {
                "total_items": len(self._items),
                "expired_items": expired_count,
                "active_items": len(self._items) - expired_count,
                "max_size": self.config.max_size,
                "utilization": len(self._items) / self.config.max_size,
            }

            if self._stats is not None:
                total_requests = self._stats["hits"] + self._stats["misses"]
                stats.update(
                    {
                        "hits": self._stats["hits"],
                        "misses": self._stats["misses"],
                        "puts": self._stats["puts"],
                        "deletes": self._stats["deletes"],
                        "clears": self._stats["clears"],
                        "evictions": self._stats["evictions"],
                        "expired_gets": self._stats["expired_gets"],
                        "cleanup_removals": self._stats["cleanup_removals"],
                        "hit_rate": self._stats["hits"] / max(1, total_requests),
                    }
                )

            return stats

    def stop(self) -> None:
        """Stop the cleanup task with timeout."""
        self._stop_event.set()
        try:
            self._thread.join(timeout=5.0)  # 5 second timeout
            self.logger.info(f"TTLQueue '{self.name}' stopped successfully")
        except Exception as e:
            self.logger.warning(f"Error stopping TTLQueue '{self.name}': {e}")

    def __del__(self):
        """Stop the cleanup task on destruction."""
        try:
            self.stop()
        except Exception:
            pass  # Ignore errors during cleanup


class AsyncTTLQueue[T]:
    """Async wrapper for TTLQueue."""

    def __init__(self, config: TTLQueueConfig | None = None):
        """Initialize the async TTL queue."""
        self._queue = TTLQueue(config)
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def put(self, id: str, value: T, ttl: int | None = None) -> None:
        """Async put operation."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._queue.put, id, value, ttl)

    async def get(self, id: str) -> T | None:
        """Async get operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._queue.get, id)

    async def delete(self, id: str) -> bool:
        """Async delete operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._queue.delete, id)

    async def clear(self) -> None:
        """Async clear operation."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._queue.clear)

    async def get_stats(self) -> dict:
        """Async get stats operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._queue.get_stats)

    def stop(self) -> None:
        """Stop the async queue."""
        self._queue.stop()
        self._executor.shutdown(wait=True)

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.stop()
        except Exception:
            pass
