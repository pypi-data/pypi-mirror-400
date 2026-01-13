"""Property-based tests using Hypothesis."""

import pytest
from hypothesis import given, strategies as st, settings, assume

from fastrobots import Robots, lint


class TestParserProperties:
    """Property-based tests for the parser."""

    @given(st.text(max_size=10000))
    @settings(max_examples=100)
    def test_parse_never_crashes(self, content):
        """Parser should never crash on any input."""
        # This should not raise any exception
        robots = Robots.parse(content)
        assert robots is not None

    @given(st.text(max_size=1000), st.text(max_size=100))
    @settings(max_examples=50)
    def test_allowed_consistent(self, content, path):
        """Multiple calls to allowed() should return same result."""
        robots = Robots.parse(content)
        result1 = robots.allowed(path, "*")
        result2 = robots.allowed(path, "*")
        assert result1 == result2

    @given(st.text(max_size=1000))
    @settings(max_examples=50)
    def test_parse_then_properties_accessible(self, content):
        """Parsed robots should have accessible properties."""
        robots = Robots.parse(content)
        # These should not crash
        _ = robots.sitemaps
        _ = robots.user_agents

    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
    @settings(max_examples=30)
    def test_batch_allowed_same_as_individual(self, paths):
        """Batch allowed should return same results as individual calls."""
        content = """
User-agent: *
Disallow: /private/
Allow: /public/
"""
        robots = Robots.parse(content)

        # Individual results
        individual = [robots.allowed(p, "bot") for p in paths]

        # Batch results
        batch = robots.allowed_batch(paths, "bot")

        assert individual == batch


class TestLinterProperties:
    """Property-based tests for the linter."""

    @given(st.text(max_size=10000))
    @settings(max_examples=100)
    def test_lint_never_crashes(self, content):
        """Linter should never crash on any input."""
        result = lint(content)
        assert result is not None
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.info, list)

    @given(st.text(max_size=1000))
    @settings(max_examples=50)
    def test_lint_strict_has_more_issues(self, content):
        """Strict mode should find at least as many issues as normal mode."""
        normal = lint(content, strict=False)
        strict = lint(content, strict=True)
        # Strict mode should find >= issues
        assert strict.issue_count >= normal.issue_count


class TestValidRobotsTxt:
    """Test with valid robots.txt content."""

    @given(
        user_agent=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        path=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P'))).map(lambda s: '/' + s),
    )
    @settings(max_examples=50)
    def test_valid_robots_parses_correctly(self, user_agent, path):
        """Valid robots.txt format should parse correctly."""
        assume(user_agent.strip())  # Non-empty user agent
        assume(path.strip())  # Non-empty path

        content = f"""
User-agent: {user_agent}
Disallow: {path}
"""
        robots = Robots.parse(content)
        assert user_agent.lower() in robots.user_agents

    @given(
        sitemap_url=st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N'), blacklist_characters='#')).map(lambda s: 'https://example.com/' + s),
    )
    @settings(max_examples=30)
    def test_sitemap_extracted(self, sitemap_url):
        """Sitemaps should be extracted correctly."""
        # Note: # is excluded from test URLs because it starts inline comments
        content = f"""
User-agent: *
Disallow:

Sitemap: {sitemap_url}
"""
        robots = Robots.parse(content)
        assert sitemap_url in robots.sitemaps
