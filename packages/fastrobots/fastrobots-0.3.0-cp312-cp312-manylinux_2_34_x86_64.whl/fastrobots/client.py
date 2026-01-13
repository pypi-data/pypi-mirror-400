"""
HTTP client for fetching robots.txt files.

Provides both sync and async interfaces using httpx.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from fastrobots._core import Robots, robots_url

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT = 10.0

# Default user agent
DEFAULT_USER_AGENT = "fastrobots/0.1 (+https://github.com/fastrobots/fastrobots)"


class FetchError(Exception):
    """Error fetching robots.txt."""

    def __init__(self, url: str, status_code: int | None = None, message: str = ""):
        self.url = url
        self.status_code = status_code
        super().__init__(
            f"Failed to fetch {url}"
            + (f" (status {status_code})" if status_code else "")
            + (f": {message}" if message else "")
        )


def fetch(
    url: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: float = DEFAULT_TIMEOUT,
    follow_redirects: bool = True,
) -> Robots:
    """
    Fetch and parse robots.txt for a URL (sync).

    Args:
        url: Any URL on the target domain (robots.txt URL will be derived)
        user_agent: User-agent string for the HTTP request
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow HTTP redirects

    Returns:
        Parsed Robots object

    Raises:
        FetchError: If the request fails

    Example:
        >>> robots = fetch("https://example.com")
        >>> robots.allowed("/path", "MyBot")
        True
    """
    target_url = robots_url(url)

    try:
        with httpx.Client(
            timeout=timeout,
            follow_redirects=follow_redirects,
        ) as client:
            response = client.get(
                target_url,
                headers={"User-Agent": user_agent},
            )

            # Handle different status codes
            if response.status_code == 200:
                return Robots.parse(response.text)
            elif response.status_code in (401, 403):
                # Access denied = disallow all
                return Robots.parse("User-agent: *\nDisallow: /")
            elif response.status_code == 404:
                # No robots.txt = allow all
                return Robots.parse("")
            elif response.status_code >= 500:
                # Server error - could retry, but for now treat as allow all
                return Robots.parse("")
            else:
                raise FetchError(target_url, response.status_code)

    except httpx.TimeoutException:
        raise FetchError(target_url, message="Request timed out")
    except httpx.RequestError as e:
        raise FetchError(target_url, message=str(e))


async def fetch_async(
    url: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: float = DEFAULT_TIMEOUT,
    follow_redirects: bool = True,
) -> Robots:
    """
    Fetch and parse robots.txt for a URL (async).

    Args:
        url: Any URL on the target domain (robots.txt URL will be derived)
        user_agent: User-agent string for the HTTP request
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow HTTP redirects

    Returns:
        Parsed Robots object

    Raises:
        FetchError: If the request fails

    Example:
        >>> robots = await fetch_async("https://example.com")
        >>> robots.allowed("/path", "MyBot")
        True
    """
    target_url = robots_url(url)

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=follow_redirects,
        ) as client:
            response = await client.get(
                target_url,
                headers={"User-Agent": user_agent},
            )

            # Handle different status codes
            if response.status_code == 200:
                return Robots.parse(response.text)
            elif response.status_code in (401, 403):
                return Robots.parse("User-agent: *\nDisallow: /")
            elif response.status_code == 404:
                return Robots.parse("")
            elif response.status_code >= 500:
                return Robots.parse("")
            else:
                raise FetchError(target_url, response.status_code)

    except httpx.TimeoutException:
        raise FetchError(target_url, message="Request timed out")
    except httpx.RequestError as e:
        raise FetchError(target_url, message=str(e))
