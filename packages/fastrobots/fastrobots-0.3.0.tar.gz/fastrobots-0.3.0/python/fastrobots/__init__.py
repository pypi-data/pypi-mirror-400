"""
fastrobots - Blazingly fast robots.txt parser

A modern, high-performance robots.txt parser written in Rust with Python bindings.
Designed to be a complete replacement for `reppy` with extended features.

Example usage:
    >>> from fastrobots import Robots
    >>> robots = Robots.parse('''
    ... User-agent: *
    ... Disallow: /private/
    ... Allow: /public/
    ... ''')
    >>> robots.allowed("/public/page", "MyBot")
    True
    >>> robots.allowed("/private/secret", "MyBot")
    False
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Import core Rust bindings
from fastrobots._core import Agent, Robots, robots_url, url_path

# Import Python extensions
from fastrobots.cache import AgentCache, RobotsCache
from fastrobots.client import fetch, fetch_async

__version__ = "0.3.0"
__all__ = [
    "Robots",
    "Agent",
    "RobotsCache",
    "AgentCache",
    "fetch",
    "fetch_async",
    "robots_url",
    "url_path",
]
