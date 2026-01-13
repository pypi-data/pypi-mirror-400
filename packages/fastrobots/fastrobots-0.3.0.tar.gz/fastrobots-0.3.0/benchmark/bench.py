#!/usr/bin/env python3
"""
Benchmark: fastrobots vs reppy

Direct comparison of parsing and URL checking performance.
"""

import time
import sys

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

TEST_PATHS = [
    "/admin/users",
    "/public/page",
    "/api/public/endpoint",
    "/api/internal/secret",
    "/random/path",
    "/private/data",
]

PARSE_ITERATIONS = 50000
CHECK_ITERATIONS = 500000


def benchmark_fastrobots():
    """Benchmark fastrobots library."""
    from fastrobots import Robots

    # Warm up
    for _ in range(100):
        Robots.parse(SAMPLE_ROBOTS)

    # Parse benchmark
    start = time.perf_counter()
    for _ in range(PARSE_ITERATIONS):
        Robots.parse(SAMPLE_ROBOTS)
    parse_time = time.perf_counter() - start
    parse_speed = PARSE_ITERATIONS / parse_time

    # Check benchmark
    robots = Robots.parse(SAMPLE_ROBOTS)

    # Warm up
    for i in range(1000):
        robots.allowed(TEST_PATHS[i % len(TEST_PATHS)], "Googlebot")

    start = time.perf_counter()
    for i in range(CHECK_ITERATIONS):
        robots.allowed(TEST_PATHS[i % len(TEST_PATHS)], "Googlebot")
    check_time = time.perf_counter() - start
    check_speed = CHECK_ITERATIONS / check_time

    return parse_speed, check_speed


def benchmark_reppy():
    """Benchmark reppy library."""
    import reppy
    from reppy.robots import Robots as ReppyRobots

    # Warm up
    for _ in range(100):
        ReppyRobots.parse("https://example.com/robots.txt", SAMPLE_ROBOTS)

    # Parse benchmark
    start = time.perf_counter()
    for _ in range(PARSE_ITERATIONS):
        ReppyRobots.parse("https://example.com/robots.txt", SAMPLE_ROBOTS)
    parse_time = time.perf_counter() - start
    parse_speed = PARSE_ITERATIONS / parse_time

    # Check benchmark
    robots = ReppyRobots.parse("https://example.com/robots.txt", SAMPLE_ROBOTS)
    agent = robots.agent("Googlebot")

    # Warm up
    for i in range(1000):
        agent.allowed(TEST_PATHS[i % len(TEST_PATHS)])

    start = time.perf_counter()
    for i in range(CHECK_ITERATIONS):
        agent.allowed(TEST_PATHS[i % len(TEST_PATHS)])
    check_time = time.perf_counter() - start
    check_speed = CHECK_ITERATIONS / check_time

    return parse_speed, check_speed


def main():
    print("=" * 70)
    print("          BENCHMARK: fastrobots v0.3.0 vs reppy")
    print("=" * 70)
    print(f"\nIterations: {PARSE_ITERATIONS:,} parses, {CHECK_ITERATIONS:,} checks")
    print(f"Test paths: {len(TEST_PATHS)}")
    print()

    # Benchmark reppy first
    print("[reppy]")
    try:
        reppy_parse, reppy_check = benchmark_reppy()
        print(f"  Parse speed: {reppy_parse:>12,.0f} /sec")
        print(f"  Check speed: {reppy_check:>12,.0f} /sec")
    except Exception as e:
        print(f"  ERROR: {e}")
        reppy_parse, reppy_check = None, None

    print()

    # Benchmark fastrobots
    print("[fastrobots v0.3.0]")
    try:
        fast_parse, fast_check = benchmark_fastrobots()
        print(f"  Parse speed: {fast_parse:>12,.0f} /sec")
        print(f"  Check speed: {fast_check:>12,.0f} /sec")
    except Exception as e:
        print(f"  ERROR: {e}")
        fast_parse, fast_check = None, None

    print()
    print("=" * 70)
    print("                         RESULTS")
    print("=" * 70)

    if reppy_parse and fast_parse:
        print(f"\n  Parse speedup: {fast_parse/reppy_parse:.1f}x faster")
        print(f"  Check speedup: {fast_check/reppy_check:.1f}x faster")

        print("\n" + "-" * 70)
        print("  Summary Table:")
        print("-" * 70)
        print(f"  {'Library':<20} {'Parse/sec':>15} {'Check/sec':>15}")
        print(f"  {'-'*20} {'-'*15} {'-'*15}")
        print(f"  {'reppy':<20} {reppy_parse:>15,.0f} {reppy_check:>15,.0f}")
        print(f"  {'fastrobots v0.3.0':<20} {fast_parse:>15,.0f} {fast_check:>15,.0f}")
        print(f"  {'-'*20} {'-'*15} {'-'*15}")
        print(f"  {'SPEEDUP':<20} {fast_parse/reppy_parse:>14.1f}x {fast_check/reppy_check:>14.1f}x")

    print()


if __name__ == "__main__":
    main()
