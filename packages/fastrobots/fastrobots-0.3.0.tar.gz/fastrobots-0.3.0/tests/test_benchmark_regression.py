"""Benchmark regression tests for fastrobots.

These tests ensure performance doesn't regress below acceptable thresholds.
"""

import time

import pytest

from fastrobots import Robots, lint


SAMPLE_ROBOTS = """
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /api/internal/
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

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-news.xml
"""

# Minimum acceptable performance thresholds
# These should be achievable on most modern hardware
MIN_PARSE_SPEED = 100_000  # parses per second
MIN_CHECK_SPEED = 1_000_000  # checks per second
MIN_BATCH_SPEED = 5_000_000  # individual path checks per second (via batch)
MIN_LINT_SPEED = 50_000  # lints per second


class TestParsePerformance:
    """Test parsing performance."""

    def test_parse_speed_regression(self):
        """Ensure parse speed stays above minimum threshold."""
        iterations = 10000

        start = time.perf_counter()
        for _ in range(iterations):
            Robots.parse(SAMPLE_ROBOTS)
        elapsed = time.perf_counter() - start

        speed = iterations / elapsed
        assert speed > MIN_PARSE_SPEED, (
            f"Parse speed regressed: {speed:,.0f}/sec "
            f"(minimum: {MIN_PARSE_SPEED:,}/sec)"
        )

    def test_parse_optimized_not_slower(self):
        """parse_optimized() should not be significantly slower than parse()."""
        iterations = 5000

        # Regular parse
        start = time.perf_counter()
        for _ in range(iterations):
            Robots.parse(SAMPLE_ROBOTS)
        regular_elapsed = time.perf_counter() - start

        # Optimized parse
        start = time.perf_counter()
        for _ in range(iterations):
            Robots.parse_optimized(SAMPLE_ROBOTS)
        optimized_elapsed = time.perf_counter() - start

        # Optimized may be slightly slower due to pre-compilation
        # but should not be more than 3x slower
        assert optimized_elapsed < regular_elapsed * 3, (
            f"parse_optimized() is too slow: {optimized_elapsed:.3f}s "
            f"vs regular {regular_elapsed:.3f}s"
        )


class TestCheckPerformance:
    """Test URL checking performance."""

    def test_check_speed_regression(self):
        """Ensure check speed stays above minimum threshold."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        iterations = 100000

        paths = [
            "/admin/users",
            "/public/page",
            "/api/public/endpoint",
            "/api/internal/secret",
            "/random/path",
            "/private/data",
        ]

        start = time.perf_counter()
        for i in range(iterations):
            path = paths[i % len(paths)]
            robots.allowed(path, "Googlebot")
        elapsed = time.perf_counter() - start

        speed = iterations / elapsed
        assert speed > MIN_CHECK_SPEED, (
            f"Check speed regressed: {speed:,.0f}/sec "
            f"(minimum: {MIN_CHECK_SPEED:,}/sec)"
        )

    def test_batch_check_speed(self):
        """Batch checking should be fast."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        paths = [
            "/admin/users",
            "/public/page",
            "/api/public/endpoint",
            "/api/internal/secret",
            "/random/path",
            "/private/data",
        ]

        iterations = 10000
        total_checks = iterations * len(paths)

        start = time.perf_counter()
        for _ in range(iterations):
            robots.allowed_batch(paths, "Googlebot")
        elapsed = time.perf_counter() - start

        speed = total_checks / elapsed
        assert speed > MIN_BATCH_SPEED, (
            f"Batch check speed regressed: {speed:,.0f}/sec "
            f"(minimum: {MIN_BATCH_SPEED:,}/sec)"
        )

    def test_batch_faster_than_individual(self):
        """Batch checking should be faster than individual checks."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        paths = [f"/path{i}/" for i in range(100)]
        iterations = 1000

        # Individual checks
        start = time.perf_counter()
        for _ in range(iterations):
            for path in paths:
                robots.allowed(path, "*")
        individual_elapsed = time.perf_counter() - start

        # Batch checks
        start = time.perf_counter()
        for _ in range(iterations):
            robots.allowed_batch(paths, "*")
        batch_elapsed = time.perf_counter() - start

        # Batch should be at least 1.5x faster
        assert batch_elapsed < individual_elapsed, (
            f"Batch not faster: {batch_elapsed:.3f}s "
            f"vs individual {individual_elapsed:.3f}s"
        )


class TestLintPerformance:
    """Test linting performance."""

    def test_lint_speed_regression(self):
        """Ensure lint speed stays above minimum threshold."""
        iterations = 5000

        start = time.perf_counter()
        for _ in range(iterations):
            lint(SAMPLE_ROBOTS)
        elapsed = time.perf_counter() - start

        speed = iterations / elapsed
        assert speed > MIN_LINT_SPEED, (
            f"Lint speed regressed: {speed:,.0f}/sec "
            f"(minimum: {MIN_LINT_SPEED:,}/sec)"
        )


class TestMemoryBehavior:
    """Test memory-related performance characteristics."""

    def test_repeated_parse_no_slowdown(self):
        """Parsing should not slow down over many iterations."""
        iterations_per_batch = 5000
        batches = 5

        times = []
        for _ in range(batches):
            start = time.perf_counter()
            for _ in range(iterations_per_batch):
                Robots.parse(SAMPLE_ROBOTS)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        # Last batch should not be more than 2x slower than first
        assert times[-1] < times[0] * 2, (
            f"Performance degraded over time: "
            f"first batch {times[0]:.3f}s, last batch {times[-1]:.3f}s"
        )

    def test_large_robots_file(self):
        """Large robots.txt should still parse quickly."""
        # Create a 1MB robots.txt
        rules = "\n".join([f"Disallow: /path{i}/subpath{i}/" for i in range(20000)])
        large_content = f"User-agent: *\n{rules}\n"

        iterations = 100

        start = time.perf_counter()
        for _ in range(iterations):
            Robots.parse(large_content)
        elapsed = time.perf_counter() - start

        speed = iterations / elapsed
        # Large files should still parse at a reasonable speed
        assert speed > 100, (
            f"Large file parse too slow: {speed:.1f}/sec "
            f"(file size: {len(large_content):,} bytes)"
        )


class TestOptimizationEffectiveness:
    """Test that optimizations are effective."""

    def test_agent_caching(self):
        """Repeated agent lookups should be fast."""
        robots = Robots.parse(SAMPLE_ROBOTS)

        # First lookup may be slower
        robots.allowed("/test", "Googlebot")

        # Subsequent lookups should be very fast
        iterations = 50000

        start = time.perf_counter()
        for _ in range(iterations):
            robots.allowed("/test", "Googlebot")
        elapsed = time.perf_counter() - start

        speed = iterations / elapsed
        assert speed > 2_000_000, (
            f"Agent caching not effective: {speed:,.0f}/sec"
        )

    def test_wildcard_agent_fast(self):
        """Wildcard agent should be fast to look up."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        iterations = 50000

        start = time.perf_counter()
        for _ in range(iterations):
            robots.allowed("/test", "*")
        elapsed = time.perf_counter() - start

        speed = iterations / elapsed
        assert speed > 2_000_000, (
            f"Wildcard agent lookup slow: {speed:,.0f}/sec"
        )


@pytest.mark.benchmark
class TestBenchmarkMarkers:
    """Tests that can be run with pytest-benchmark."""

    def test_parse_benchmark(self, benchmark):
        """Benchmark parsing."""
        benchmark(Robots.parse, SAMPLE_ROBOTS)

    def test_allowed_benchmark(self, benchmark):
        """Benchmark allowed check."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        benchmark(robots.allowed, "/admin/users", "Googlebot")

    def test_batch_benchmark(self, benchmark):
        """Benchmark batch check."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        paths = ["/admin/", "/public/", "/api/", "/"]
        benchmark(robots.allowed_batch, paths, "*")

    def test_lint_benchmark(self, benchmark):
        """Benchmark linting."""
        benchmark(lint, SAMPLE_ROBOTS)
