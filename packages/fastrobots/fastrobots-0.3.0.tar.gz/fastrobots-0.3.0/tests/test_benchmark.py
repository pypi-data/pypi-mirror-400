"""Benchmark tests for fastrobots."""

import pytest


SAMPLE_ROBOTS_TXT = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /api/internal/
Disallow: /search?*q=
Allow: /api/public/
Allow: /public/
Crawl-delay: 1

User-agent: Googlebot
Allow: /
Disallow: /admin/

User-agent: Bingbot
Allow: /
Disallow: /admin/
Disallow: /private/

User-agent: BadBot
Disallow: /

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-news.xml
Sitemap: https://example.com/sitemap-images.xml
"""


@pytest.fixture
def sample_content():
    return SAMPLE_ROBOTS_TXT


class TestParsingBenchmark:
    """Benchmark parsing performance."""

    def test_parse_speed(self, benchmark, sample_content):
        """Benchmark robots.txt parsing."""
        from fastrobots import Robots

        result = benchmark(Robots.parse, sample_content)
        assert result is not None

    def test_parse_empty(self, benchmark):
        """Benchmark parsing empty content."""
        from fastrobots import Robots

        result = benchmark(Robots.parse, "")
        assert result is not None


class TestMatchingBenchmark:
    """Benchmark URL matching performance."""

    @pytest.fixture
    def robots(self, sample_content):
        from fastrobots import Robots
        return Robots.parse(sample_content)

    def test_allowed_simple(self, benchmark, robots):
        """Benchmark simple path checking."""
        result = benchmark(robots.allowed, "/public/page", "Googlebot")
        assert result is True

    def test_allowed_disallowed(self, benchmark, robots):
        """Benchmark disallowed path checking."""
        result = benchmark(robots.allowed, "/admin/users", "*")
        assert result is False

    def test_allowed_wildcard(self, benchmark, robots):
        """Benchmark wildcard pattern matching."""
        result = benchmark(robots.allowed, "/search?foo=bar&q=test", "*")
        assert result is False

    def test_allowed_unknown_agent(self, benchmark, robots):
        """Benchmark with unknown user-agent (fallback to *)."""
        result = benchmark(robots.allowed, "/public/page", "UnknownBot")
        assert result is True


class TestAgentBenchmark:
    """Benchmark Agent operations."""

    @pytest.fixture
    def robots(self, sample_content):
        from fastrobots import Robots
        return Robots.parse(sample_content)

    def test_agent_lookup(self, benchmark, robots):
        """Benchmark agent lookup."""
        result = benchmark(robots.agent, "Googlebot")
        assert result is not None

    def test_agent_allowed(self, benchmark, robots):
        """Benchmark Agent.allowed method."""
        agent = robots.agent("Googlebot")
        result = benchmark(agent.allowed, "/public/page")
        assert result is True


class TestComparisonBenchmark:
    """Compare against other implementations if available."""

    def test_parse_comparison(self, benchmark, sample_content):
        """Parse benchmark for comparison with reppy."""
        from fastrobots import Robots

        # Run benchmark
        result = benchmark(Robots.parse, sample_content)

        # Print stats for comparison
        # reppy claims ~100k parses/sec
        # We aim for >500k parses/sec
        assert result is not None

    def test_check_comparison(self, benchmark, sample_content):
        """URL check benchmark for comparison with reppy."""
        from fastrobots import Robots

        robots = Robots.parse(sample_content)

        # Run benchmark
        result = benchmark(robots.allowed, "/admin/users", "Googlebot")

        # reppy claims ~1M checks/sec
        # We aim for >5M checks/sec
        assert result is not None
