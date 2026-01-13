"""Tests for the core parser functionality."""

import pytest


# We'll import from the built module
# For now, test the structure
class TestRobotsParser:
    """Test robots.txt parsing."""

    def test_simple_disallow(self):
        """Test simple disallow rule."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /private/
""")
        assert robots.allowed("/public/", "*") is True
        assert robots.allowed("/private/", "*") is False
        assert robots.allowed("/private/secret", "*") is False

    def test_simple_allow(self):
        """Test simple allow rule."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /
Allow: /public/
""")
        assert robots.allowed("/public/", "*") is True
        assert robots.allowed("/public/page", "*") is True
        assert robots.allowed("/private/", "*") is False

    def test_empty_disallow(self):
        """Empty disallow means allow all."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow:
""")
        assert robots.allowed("/anything", "*") is True
        assert robots.allowed("/private/secret", "*") is True

    def test_multiple_user_agents(self):
        """Test multiple user-agent blocks."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: Googlebot
Disallow: /nogoogle/

User-agent: Bingbot
Disallow: /nobing/

User-agent: *
Disallow: /private/
""")
        # Googlebot rules
        assert robots.allowed("/nogoogle/page", "Googlebot") is False
        assert robots.allowed("/nobing/page", "Googlebot") is True

        # Bingbot rules
        assert robots.allowed("/nobing/page", "Bingbot") is False
        assert robots.allowed("/nogoogle/page", "Bingbot") is True

        # Wildcard rules
        assert robots.allowed("/private/page", "RandomBot") is False
        assert robots.allowed("/public/page", "RandomBot") is True

    def test_crawl_delay(self):
        """Test crawl-delay parsing."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Crawl-delay: 10

User-agent: Googlebot
Crawl-delay: 5
""")
        assert robots.crawl_delay("*") == 10.0
        assert robots.crawl_delay("Googlebot") == 5.0
        assert robots.crawl_delay("RandomBot") == 10.0  # Falls back to *

    def test_sitemaps(self):
        """Test sitemap extraction."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /private/

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-news.xml
""")
        assert len(robots.sitemaps) == 2
        assert "https://example.com/sitemap.xml" in robots.sitemaps
        assert "https://example.com/sitemap-news.xml" in robots.sitemaps

    def test_user_agents_list(self):
        """Test user_agents property."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: Googlebot
Disallow: /

User-agent: Bingbot
Disallow: /

User-agent: *
Allow: /
""")
        agents = robots.user_agents
        assert "googlebot" in agents
        assert "bingbot" in agents
        assert "*" in agents

    def test_case_insensitive_user_agent(self):
        """User-agent matching should be case-insensitive."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: Googlebot
Disallow: /private/
""")
        assert robots.allowed("/private/", "googlebot") is False
        assert robots.allowed("/private/", "GOOGLEBOT") is False
        assert robots.allowed("/private/", "GoogleBot") is False

    def test_comments_ignored(self):
        """Comments should be ignored."""
        from fastrobots import Robots

        robots = Robots.parse("""
# This is a comment
User-agent: *
Disallow: /private/  # Inline comment should work too
""")
        assert robots.allowed("/private/", "*") is False
        assert robots.allowed("/public/", "*") is True

    def test_empty_content(self):
        """Empty robots.txt allows everything."""
        from fastrobots import Robots

        robots = Robots.parse("")
        assert robots.allowed("/anything", "*") is True
        assert robots.allowed("/private/secret", "Googlebot") is True


class TestWildcardMatching:
    """Test wildcard pattern matching."""

    def test_star_wildcard(self):
        """Test * wildcard in path."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /private/*.html
""")
        assert robots.allowed("/private/page.html", "*") is False
        assert robots.allowed("/private/other.html", "*") is False
        assert robots.allowed("/private/page.php", "*") is True
        assert robots.allowed("/public/page.html", "*") is True

    def test_end_anchor(self):
        """Test $ end anchor."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /*.pdf$
""")
        assert robots.allowed("/document.pdf", "*") is False
        assert robots.allowed("/path/to/file.pdf", "*") is False
        assert robots.allowed("/document.pdf.bak", "*") is True
        assert robots.allowed("/document.html", "*") is True

    def test_complex_pattern(self):
        """Test complex wildcard patterns."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /search?*q=
""")
        assert robots.allowed("/search?q=test", "*") is False
        assert robots.allowed("/search?foo=bar&q=test", "*") is False
        assert robots.allowed("/search", "*") is True


class TestAgent:
    """Test Agent class."""

    def test_agent_allowed(self):
        """Test Agent.allowed method."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: TestBot
Disallow: /private/
Crawl-delay: 5
""")
        agent = robots.agent("TestBot")
        assert agent.allowed("/public/") is True
        assert agent.allowed("/private/") is False
        assert agent.delay == 5.0
        assert agent.name == "TestBot"

    def test_agent_fallback_to_wildcard(self):
        """Agent should fall back to * rules if no specific rules."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /admin/
""")
        agent = robots.agent("UnknownBot")
        assert agent.allowed("/admin/") is False
        assert agent.allowed("/public/") is True


class TestUrlFunctions:
    """Test URL utility functions."""

    def test_robots_url(self):
        """Test robots_url function."""
        from fastrobots import robots_url

        assert robots_url("https://example.com/page") == "https://example.com/robots.txt"
        assert robots_url("https://example.com:8080/page") == "https://example.com:8080/robots.txt"
        assert robots_url("http://sub.example.com/") == "http://sub.example.com/robots.txt"

    def test_url_path(self):
        """Test url_path function."""
        from fastrobots import url_path

        assert url_path("https://example.com/path/to/page") == "/path/to/page"
        assert url_path("https://example.com/") == "/"
        assert url_path("https://example.com") == "/"


class TestLongestMatchWins:
    """Test that longest matching rule wins."""

    def test_longer_allow_wins(self):
        """Longer allow should override shorter disallow."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /private/
Allow: /private/public/
""")
        assert robots.allowed("/private/secret", "*") is False
        assert robots.allowed("/private/public/page", "*") is True

    def test_longer_disallow_wins(self):
        """Longer disallow should override shorter allow."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Allow: /api/
Disallow: /api/internal/
""")
        assert robots.allowed("/api/public", "*") is True
        assert robots.allowed("/api/internal/secret", "*") is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_malformed_lines(self):
        """Malformed lines should be ignored."""
        from fastrobots import Robots

        robots = Robots.parse("""
This is not valid
User-agent: *
Invalid line without colon
Disallow: /private/
Another bad line
""")
        assert robots.allowed("/private/", "*") is False
        assert robots.allowed("/public/", "*") is True

    def test_no_user_agent(self):
        """Rules without user-agent should be ignored."""
        from fastrobots import Robots

        robots = Robots.parse("""
Disallow: /private/
""")
        # No user-agent defined, so no rules apply
        assert robots.allowed("/private/", "*") is True

    def test_unicode_content(self):
        """Should handle unicode content."""
        from fastrobots import Robots

        robots = Robots.parse("""
User-agent: *
Disallow: /日本語/
Disallow: /émojis/🎉/
""")
        assert robots.allowed("/日本語/page", "*") is False
        assert robots.allowed("/émojis/🎉/party", "*") is False
        assert robots.allowed("/english/", "*") is True
