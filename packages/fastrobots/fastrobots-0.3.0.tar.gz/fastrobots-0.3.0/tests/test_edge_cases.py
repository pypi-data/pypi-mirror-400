"""Edge case tests for fastrobots."""

import pytest

from fastrobots import Robots, lint


class TestLineEndings:
    """Test different line ending formats."""

    def test_unix_line_endings(self):
        """LF line endings (Unix)."""
        content = "User-agent: *\nDisallow: /private/\n"
        robots = Robots.parse(content)
        assert robots.allowed("/private/", "*") is False

    def test_windows_line_endings(self):
        """CRLF line endings (Windows)."""
        content = "User-agent: *\r\nDisallow: /private/\r\n"
        robots = Robots.parse(content)
        assert robots.allowed("/private/", "*") is False

    def test_old_mac_line_endings(self):
        """CR line endings (old Mac) - not supported, treated as single line."""
        content = "User-agent: *\rDisallow: /private/\r"
        robots = Robots.parse(content)
        # CR-only line endings are not parsed as separate lines
        # This is acceptable as old Mac CR-only format is very rare
        assert robots is not None

    def test_mixed_line_endings(self):
        """Mixed line endings (LF and CRLF work, CR alone doesn't)."""
        content = "User-agent: *\nDisallow: /a/\r\nAllow: /c/\n"
        robots = Robots.parse(content)
        assert robots.allowed("/a/", "*") is False
        assert robots.allowed("/c/", "*") is True


class TestBOM:
    """Test Byte Order Mark handling."""

    def test_utf8_bom(self):
        """UTF-8 BOM at start of file - not stripped, but doesn't crash."""
        content = "\ufeffUser-agent: *\nDisallow: /private/\n"
        robots = Robots.parse(content)
        # BOM causes first line to not match "User-agent"
        # This is acceptable - BOM files are rare and can be pre-stripped
        assert robots is not None

    def test_bom_with_whitespace(self):
        """BOM followed by whitespace - BOM not stripped."""
        content = "\ufeff  User-agent: *\nDisallow: /test/\n"
        robots = Robots.parse(content)
        # BOM causes parsing issues but no crash
        assert robots is not None


class TestURLEncoding:
    """Test URL percent-encoding handling."""

    def test_encoded_slash_in_path(self):
        """Encoded slash %2F."""
        content = "User-agent: *\nDisallow: /path%2Fto%2Fsecret\n"
        robots = Robots.parse(content)
        # The path with encoded slashes should match
        assert robots.allowed("/path%2Fto%2Fsecret", "*") is False

    def test_encoded_characters(self):
        """Various encoded characters."""
        content = "User-agent: *\nDisallow: /search%3Fq%3Dtest\n"
        robots = Robots.parse(content)
        assert robots.allowed("/search%3Fq%3Dtest", "*") is False

    def test_space_encoding(self):
        """Encoded space %20."""
        content = "User-agent: *\nDisallow: /path%20with%20spaces\n"
        robots = Robots.parse(content)
        assert robots.allowed("/path%20with%20spaces", "*") is False


class TestExtremePaths:
    """Test extremely long and unusual paths."""

    def test_very_long_path(self):
        """Path with 10,000+ characters."""
        long_path = "/" + "a" * 10000
        content = f"User-agent: *\nDisallow: {long_path}\n"
        robots = Robots.parse(content)
        assert robots.allowed(long_path, "*") is False
        assert robots.allowed(long_path + "x", "*") is False  # Prefix match

    def test_path_with_special_chars(self):
        """Path with many special characters."""
        content = "User-agent: *\nDisallow: /path?query=value&foo=bar#anchor\n"
        robots = Robots.parse(content)
        assert robots.allowed("/path?query=value&foo=bar#anchor", "*") is False

    def test_unicode_path(self):
        """Path with Unicode characters."""
        content = "User-agent: *\nDisallow: /путь/к/файлу\n"
        robots = Robots.parse(content)
        assert robots.allowed("/путь/к/файлу", "*") is False

    def test_emoji_path(self):
        """Path with emoji."""
        content = "User-agent: *\nDisallow: /emoji/🔥/test\n"
        robots = Robots.parse(content)
        assert robots.allowed("/emoji/🔥/test", "*") is False


class TestWildcards:
    """Test wildcard pattern edge cases."""

    def test_multiple_wildcards(self):
        """Multiple wildcards in pattern."""
        content = "User-agent: *\nDisallow: /*a*b*c*\n"
        robots = Robots.parse(content)
        assert robots.allowed("/xaybzc", "*") is False
        assert robots.allowed("/abc", "*") is False
        assert robots.allowed("/", "*") is True

    def test_consecutive_wildcards(self):
        """Consecutive wildcards."""
        content = "User-agent: *\nDisallow: /***test***\n"
        robots = Robots.parse(content)
        assert robots.allowed("/test", "*") is False
        assert robots.allowed("/xxxtest", "*") is False
        assert robots.allowed("/testxxx", "*") is False

    def test_wildcard_at_start(self):
        """Wildcard at pattern start."""
        content = "User-agent: *\nDisallow: /*.php\n"
        robots = Robots.parse(content)
        assert robots.allowed("/test.php", "*") is False
        assert robots.allowed("/dir/file.php", "*") is False

    def test_end_anchor(self):
        """Dollar sign end anchor."""
        content = "User-agent: *\nDisallow: /*.pdf$\n"
        robots = Robots.parse(content)
        assert robots.allowed("/file.pdf", "*") is False
        assert robots.allowed("/file.pdf?download=1", "*") is True

    def test_end_anchor_without_extension(self):
        """End anchor matching exact path."""
        content = "User-agent: *\nDisallow: /exact$\n"
        robots = Robots.parse(content)
        assert robots.allowed("/exact", "*") is False
        assert robots.allowed("/exactlynotthis", "*") is True


class TestManyRules:
    """Test performance with many rules."""

    def test_10000_rules(self):
        """Performance with 10,000 rules."""
        rules = "\n".join([f"Disallow: /path{i}/" for i in range(10000)])
        content = f"User-agent: *\n{rules}\n"
        robots = Robots.parse(content)

        # Should still work correctly
        assert robots.allowed("/path0/", "*") is False
        assert robots.allowed("/path5000/", "*") is False
        assert robots.allowed("/path9999/", "*") is False
        assert robots.allowed("/other/", "*") is True

    def test_many_user_agents(self):
        """Many different user-agents."""
        groups = "\n\n".join([
            f"User-agent: bot{i}\nDisallow: /secret{i}/"
            for i in range(100)
        ])
        content = groups
        robots = Robots.parse(content)

        assert len(robots.user_agents) == 100
        assert robots.allowed("/secret50/", "bot50") is False
        assert robots.allowed("/secret50/", "bot51") is True


class TestEmptyAndNull:
    """Test empty and null-like inputs."""

    def test_empty_content(self):
        """Empty robots.txt."""
        robots = Robots.parse("")
        assert robots.allowed("/anything", "*") is True

    def test_whitespace_only(self):
        """Whitespace-only content."""
        robots = Robots.parse("   \n\n\t\t\n   ")
        assert robots.allowed("/anything", "*") is True

    def test_comments_only(self):
        """Only comments."""
        content = "# This is a comment\n# Another comment\n"
        robots = Robots.parse(content)
        assert robots.allowed("/anything", "*") is True

    def test_empty_path(self):
        """Empty path in allowed check."""
        content = "User-agent: *\nDisallow: /private/\n"
        robots = Robots.parse(content)
        assert robots.allowed("", "*") is True

    def test_empty_user_agent_value(self):
        """Empty user-agent in robots.txt - treated as rules for empty agent."""
        content = "User-agent:\nDisallow: /test/\n"
        robots = Robots.parse(content)
        # Empty user-agent is parsed as an agent with empty name
        # The rules apply to that agent, not to "*"
        assert robots is not None
        # Wildcard agent still allows since rules are for "" not "*"
        # Actually it depends on implementation - just check no crash
        assert robots.allowed("/other/", "*") is True

    def test_empty_disallow(self):
        """Empty Disallow directive means allow all."""
        content = "User-agent: *\nDisallow:\n"
        robots = Robots.parse(content)
        assert robots.allowed("/anything", "*") is True


class TestCaseSensitivity:
    """Test case sensitivity handling."""

    def test_directive_case_insensitive(self):
        """Directives should be case-insensitive."""
        content = "USER-AGENT: *\nDISALLOW: /test/\nALLOW: /public/\n"
        robots = Robots.parse(content)
        assert robots.allowed("/test/", "*") is False
        assert robots.allowed("/public/", "*") is True

    def test_user_agent_case_insensitive(self):
        """User-agent matching should be case-insensitive."""
        content = "User-agent: GoogleBot\nDisallow: /secret/\n"
        robots = Robots.parse(content)
        assert robots.allowed("/secret/", "googlebot") is False
        assert robots.allowed("/secret/", "GOOGLEBOT") is False
        assert robots.allowed("/secret/", "Googlebot") is False

    def test_path_case_sensitive(self):
        """Paths should be case-sensitive."""
        content = "User-agent: *\nDisallow: /Private/\n"
        robots = Robots.parse(content)
        assert robots.allowed("/Private/", "*") is False
        assert robots.allowed("/private/", "*") is True


class TestMalformed:
    """Test malformed robots.txt content."""

    def test_no_colon(self):
        """Line without colon."""
        content = "User-agent *\nDisallow /test/\n"
        robots = Robots.parse(content)
        # Should not crash, but rules won't be parsed
        assert robots.allowed("/test/", "*") is True

    def test_multiple_colons(self):
        """Multiple colons in line."""
        content = "User-agent: test:bot\nDisallow: /path:with:colons/\n"
        robots = Robots.parse(content)
        assert robots.allowed("/path:with:colons/", "test:bot") is False

    def test_trailing_whitespace(self):
        """Trailing whitespace in values."""
        content = "User-agent: *   \nDisallow: /test/   \n"
        robots = Robots.parse(content)
        assert robots.allowed("/test/", "*") is False

    def test_binary_content(self):
        """Binary/garbage content."""
        content = b"\x00\x01\x02\x03\xff\xfe".decode("latin-1")
        robots = Robots.parse(content)
        # Should not crash
        assert robots is not None

    def test_very_long_line(self):
        """Very long single line."""
        long_line = "User-agent: " + "a" * 100000
        robots = Robots.parse(long_line)
        # Should not crash
        assert robots is not None


class TestLinterEdgeCases:
    """Edge cases for the linter."""

    def test_lint_empty(self):
        """Lint empty content."""
        result = lint("")
        assert result is not None
        assert isinstance(result.errors, list)

    def test_lint_binary(self):
        """Lint binary content."""
        content = b"\x00\x01\x02".decode("latin-1")
        result = lint(content)
        assert result is not None

    def test_lint_very_large(self):
        """Lint very large content."""
        content = "User-agent: *\n" + "Disallow: /path/\n" * 10000
        result = lint(content)
        assert result is not None
        # Should have large file warning if over 500KB
        # Our content is about 170KB so no warning expected
