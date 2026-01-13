"""
Caching layer for robots.txt parsing.

Provides LRU caching for both full Robots objects and per-agent rules.
"""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock
from typing import TYPE_CHECKING, Any

from fastrobots._core import Agent, Robots, robots_url, url_path
from fastrobots.client import fetch, fetch_async


@dataclass
class CacheEntry:
    """A cached robots.txt entry with TTL support."""
    robots: Robots
    expires_at: float

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at

    @property
    def ttl(self) -> float:
        """Time remaining until expiration in seconds."""
        return max(0, self.expires_at - time.time())


class RobotsCache:
    """
    LRU cache for Robots objects.

    Caches parsed robots.txt files by domain, with configurable capacity
    and TTL (time-to-live) for entries.

    Example:
        >>> cache = RobotsCache(capacity=100, default_ttl=3600)
        >>> allowed = cache.allowed("https://example.com/path", "MyBot")

        # Async usage
        >>> allowed = await cache.allowed_async("https://example.com/path", "MyBot")
    """

    def __init__(
        self,
        capacity: int = 100,
        default_ttl: float = 3600,
        user_agent: str = "fastrobots/0.1",
    ):
        """
        Initialize the cache.

        Args:
            capacity: Maximum number of robots.txt files to cache
            default_ttl: Default time-to-live in seconds
            user_agent: User-agent string for HTTP requests
        """
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.user_agent = user_agent
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = Lock()

    def _cache_key(self, url: str) -> str:
        """Extract the cache key (scheme + host) from a URL."""
        return robots_url(url).rsplit("/robots.txt", 1)[0]

    def _evict_if_needed(self) -> None:
        """Evict oldest entries if cache is over capacity."""
        while len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def get(self, url: str) -> Robots | None:
        """
        Get cached Robots for a URL if available and not expired.

        Args:
            url: Any URL on the target domain

        Returns:
            Cached Robots object or None if not cached/expired
        """
        key = self._cache_key(url)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None or entry.expired:
                if entry is not None:
                    del self._cache[key]
                return None
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return entry.robots

    def put(self, url: str, robots: Robots, ttl: float | None = None) -> None:
        """
        Cache a Robots object for a URL.

        Args:
            url: Any URL on the target domain
            robots: Parsed Robots object
            ttl: Time-to-live in seconds (uses default if None)
        """
        key = self._cache_key(url)
        ttl = ttl if ttl is not None else self.default_ttl
        entry = CacheEntry(
            robots=robots,
            expires_at=time.time() + ttl,
        )
        with self._lock:
            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._evict_if_needed()

    def fetch_robots(self, url: str, ttl: float | None = None) -> Robots:
        """
        Fetch and cache robots.txt for a URL.

        Args:
            url: Any URL on the target domain
            ttl: Time-to-live in seconds

        Returns:
            Parsed Robots object
        """
        robots = fetch(url, user_agent=self.user_agent)
        self.put(url, robots, ttl)
        return robots

    async def fetch_robots_async(self, url: str, ttl: float | None = None) -> Robots:
        """
        Async fetch and cache robots.txt for a URL.

        Args:
            url: Any URL on the target domain
            ttl: Time-to-live in seconds

        Returns:
            Parsed Robots object
        """
        robots = await fetch_async(url, user_agent=self.user_agent)
        self.put(url, robots, ttl)
        return robots

    def allowed(
        self,
        url: str,
        user_agent: str | None = None,
        fetch_if_missing: bool = True,
    ) -> bool:
        """
        Check if a URL is allowed for a user-agent.

        Args:
            url: The URL to check
            user_agent: User-agent to check (uses cache's user_agent if None)
            fetch_if_missing: Whether to fetch robots.txt if not cached

        Returns:
            True if the URL is allowed
        """
        user_agent = user_agent or self.user_agent
        path = url_path(url)

        robots = self.get(url)
        if robots is None:
            if not fetch_if_missing:
                return True  # Assume allowed if not fetching
            robots = self.fetch_robots(url)

        return robots.allowed(path, user_agent)

    async def allowed_async(
        self,
        url: str,
        user_agent: str | None = None,
        fetch_if_missing: bool = True,
    ) -> bool:
        """
        Async check if a URL is allowed for a user-agent.

        Args:
            url: The URL to check
            user_agent: User-agent to check (uses cache's user_agent if None)
            fetch_if_missing: Whether to fetch robots.txt if not cached

        Returns:
            True if the URL is allowed
        """
        user_agent = user_agent or self.user_agent
        path = url_path(url)

        robots = self.get(url)
        if robots is None:
            if not fetch_if_missing:
                return True
            robots = await self.fetch_robots_async(url)

        return robots.allowed(path, user_agent)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, url: str) -> bool:
        return self.get(url) is not None


class AgentCache:
    """
    Cache optimized for a single user-agent.

    More memory-efficient than RobotsCache when you only need to check
    for one user-agent.

    Example:
        >>> cache = AgentCache(agent="MyBot", capacity=100)
        >>> allowed = cache.allowed("https://example.com/path")
    """

    def __init__(
        self,
        agent: str,
        capacity: int = 100,
        default_ttl: float = 3600,
    ):
        """
        Initialize the agent cache.

        Args:
            agent: User-agent string to check against
            capacity: Maximum number of domains to cache
            default_ttl: Default time-to-live in seconds
        """
        self.agent = agent
        self._robots_cache = RobotsCache(
            capacity=capacity,
            default_ttl=default_ttl,
            user_agent=agent,
        )

    def allowed(self, url: str, fetch_if_missing: bool = True) -> bool:
        """
        Check if a URL is allowed for this agent.

        Args:
            url: The URL to check
            fetch_if_missing: Whether to fetch robots.txt if not cached

        Returns:
            True if the URL is allowed
        """
        return self._robots_cache.allowed(
            url, self.agent, fetch_if_missing=fetch_if_missing
        )

    async def allowed_async(self, url: str, fetch_if_missing: bool = True) -> bool:
        """
        Async check if a URL is allowed for this agent.

        Args:
            url: The URL to check
            fetch_if_missing: Whether to fetch robots.txt if not cached

        Returns:
            True if the URL is allowed
        """
        return await self._robots_cache.allowed_async(
            url, self.agent, fetch_if_missing=fetch_if_missing
        )

    def clear(self) -> None:
        """Clear the cache."""
        self._robots_cache.clear()

    def __len__(self) -> int:
        return len(self._robots_cache)
