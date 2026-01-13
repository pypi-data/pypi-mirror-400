"""Type stubs for the Rust _core module."""

from typing import List, Optional

class Robots:
    """
    Main robots.txt parser and checker.

    Parse a robots.txt content string and check URL permissions.
    """

    @staticmethod
    def parse(content: str) -> Robots:
        """
        Parse a robots.txt content string.

        Args:
            content: The robots.txt file content

        Returns:
            A Robots object
        """
        ...

    def allowed(self, path: str, user_agent: str) -> bool:
        """
        Check if a path is allowed for a user-agent.

        Args:
            path: The URL path to check (e.g., "/admin/users")
            user_agent: The user-agent string

        Returns:
            True if the path is allowed
        """
        ...

    def crawl_delay(self, user_agent: str) -> Optional[float]:
        """
        Get the crawl delay for a user-agent.

        Args:
            user_agent: The user-agent string

        Returns:
            Crawl delay in seconds, or None if not specified
        """
        ...

    def agent(self, user_agent: str) -> Agent:
        """
        Get an Agent object for a specific user-agent.

        Args:
            user_agent: The user-agent string

        Returns:
            An Agent object with rules for this user-agent
        """
        ...

    @property
    def sitemaps(self) -> List[str]:
        """List of sitemap URLs defined in the robots.txt."""
        ...

    @property
    def user_agents(self) -> List[str]:
        """List of user-agents defined in the robots.txt."""
        ...


class Agent:
    """
    Rules for a specific user-agent.

    Provides methods to check URL permissions for this agent.
    """

    def allowed(self, path: str) -> bool:
        """
        Check if a path is allowed.

        Args:
            path: The URL path to check

        Returns:
            True if the path is allowed
        """
        ...

    @property
    def delay(self) -> Optional[float]:
        """Crawl delay in seconds, or None if not specified."""
        ...

    @property
    def name(self) -> str:
        """The user-agent name."""
        ...


def robots_url(url: str) -> str:
    """
    Extract the robots.txt URL from any URL.

    Args:
        url: Any URL on the target domain

    Returns:
        The robots.txt URL (e.g., "https://example.com/robots.txt")

    Raises:
        ValueError: If the URL is invalid
    """
    ...


def url_path(url: str) -> str:
    """
    Extract the path component from a URL.

    Args:
        url: A full URL

    Returns:
        The path component (e.g., "/path/to/page")

    Raises:
        ValueError: If the URL is invalid
    """
    ...
