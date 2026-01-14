"""
State store implementations for HTTP layer.

Provides state management backends:
- InMemoryState: For development/testing
- RedisState: For production distributed state
"""

from __future__ import annotations

import json
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class StateStore(Protocol):
    """Protocol for state store implementations."""

    async def get(self, key: str, default: T | None = None) -> T | None:
        """Get a value from state."""
        ...

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set a value in state."""
        ...

    async def delete(self, key: str) -> bool:
        """Delete a value from state."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...

    async def close(self) -> None:
        """Close the state store."""
        ...


class InMemoryState:
    """
    In-memory state store for development and testing.

    Note: State is lost on restart and not shared across instances.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str, default: T | None = None) -> T | None:
        """Get a value from state."""
        return self._store.get(key, default)

    async def set(
        self, key: str, value: Any, ttl_seconds: int | None = None
    ) -> None:
        """Set a value in state. TTL is ignored in memory store."""
        self._store[key] = value

    async def delete(self, key: str) -> bool:
        """Delete a value from state."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._store

    async def close(self) -> None:
        """Close the state store."""
        self._store.clear()

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern (simple wildcard support)."""
        if pattern == "*":
            return list(self._store.keys())

        # Simple prefix matching
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [k for k in self._store.keys() if k.startswith(prefix)]

        return [k for k in self._store.keys() if k == pattern]


class RedisState:
    """
    Redis-backed state store for production.

    Provides distributed state with TTL support.
    """

    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self._url = url
        self._client = None

    async def connect(self) -> None:
        """Connect to Redis."""
        import redis.asyncio as redis

        self._client = redis.from_url(
            self._url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def get(self, key: str, default: T | None = None) -> T | None:
        """Get a value from state."""
        if self._client is None:
            raise RuntimeError("Redis not connected")

        value = await self._client.get(key)
        if value is None:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(
        self, key: str, value: Any, ttl_seconds: int | None = None
    ) -> None:
        """Set a value in state with optional TTL."""
        if self._client is None:
            raise RuntimeError("Redis not connected")

        serialized = json.dumps(value) if not isinstance(value, str) else value

        if ttl_seconds:
            await self._client.setex(key, ttl_seconds, serialized)
        else:
            await self._client.set(key, serialized)

    async def delete(self, key: str) -> bool:
        """Delete a value from state."""
        if self._client is None:
            raise RuntimeError("Redis not connected")

        result = await self._client.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._client is None:
            raise RuntimeError("Redis not connected")

        return await self._client.exists(key) > 0

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        if self._client is None:
            raise RuntimeError("Redis not connected")

        return await self._client.keys(pattern)
