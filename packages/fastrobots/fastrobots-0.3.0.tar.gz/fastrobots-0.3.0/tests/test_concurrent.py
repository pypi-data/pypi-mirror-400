"""Concurrent access tests for fastrobots."""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from fastrobots import Robots


SAMPLE_ROBOTS = """
User-agent: *
Disallow: /private/
Disallow: /admin/
Allow: /public/
Crawl-delay: 1

User-agent: Googlebot
Allow: /
Disallow: /admin/

Sitemap: https://example.com/sitemap.xml
"""


class TestConcurrentAllowed:
    """Test concurrent access to allowed() method."""

    def test_concurrent_allowed_same_result(self):
        """Concurrent allowed() calls should return consistent results."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        results = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(robots.allowed, "/private/secret", "*")
                for _ in range(1000)
            ]
            results = [f.result() for f in as_completed(futures)]

        # All results should be the same (False for /private/)
        assert all(r == results[0] for r in results)
        assert results[0] is False

    def test_concurrent_allowed_different_paths(self):
        """Concurrent allowed() calls with different paths."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        paths = [
            "/private/secret",
            "/public/page",
            "/admin/users",
            "/random/path",
            "/",
        ]
        expected = [False, True, False, True, True]

        def check_path(path):
            return robots.allowed(path, "*")

        with ThreadPoolExecutor(max_workers=10) as executor:
            for _ in range(100):  # Run 100 rounds
                futures = {
                    executor.submit(check_path, path): i
                    for i, path in enumerate(paths)
                }
                results = [None] * len(paths)
                for future in as_completed(futures):
                    idx = futures[future]
                    results[idx] = future.result()

                assert results == expected

    def test_concurrent_different_agents(self):
        """Concurrent allowed() calls with different user-agents."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        agents = ["*", "Googlebot", "Bingbot", "MyBot"]

        def check_agent(agent):
            return robots.allowed("/admin/users", agent)

        with ThreadPoolExecutor(max_workers=10) as executor:
            for _ in range(100):
                futures = [executor.submit(check_agent, agent) for agent in agents]
                results = [f.result() for f in futures]

                # /admin/ is disallowed for all agents in our sample
                assert all(r is False for r in results)


class TestConcurrentParse:
    """Test concurrent parsing."""

    def test_concurrent_parse(self):
        """Multiple threads parsing simultaneously."""
        contents = [
            "User-agent: *\nDisallow: /a/",
            "User-agent: *\nDisallow: /b/",
            "User-agent: *\nDisallow: /c/",
            "User-agent: *\nDisallow: /d/",
        ]

        def parse_and_check(content, idx):
            robots = Robots.parse(content)
            path = f"/{chr(ord('a') + idx)}/"
            return robots.allowed(path, "*")

        with ThreadPoolExecutor(max_workers=10) as executor:
            for _ in range(50):
                futures = [
                    executor.submit(parse_and_check, content, i)
                    for i, content in enumerate(contents)
                ]
                results = [f.result() for f in futures]

                # All should be disallowed for their respective paths
                assert all(r is False for r in results)


class TestConcurrentBatch:
    """Test concurrent batch operations."""

    def test_concurrent_batch_allowed(self):
        """Concurrent allowed_batch() calls."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        paths = ["/private/", "/public/", "/admin/", "/"]

        def batch_check():
            return robots.allowed_batch(paths, "*")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(batch_check) for _ in range(100)]
            results = [f.result() for f in as_completed(futures)]

        # All batch results should be identical
        expected = [False, True, False, True]
        for result in results:
            assert result == expected


class TestConcurrentAgent:
    """Test concurrent Agent operations."""

    def test_concurrent_agent_creation(self):
        """Concurrent agent() calls."""
        robots = Robots.parse(SAMPLE_ROBOTS)

        def get_agent(name):
            return robots.agent(name)

        agents_to_get = ["*", "Googlebot", "Bingbot", "CustomBot"] * 25

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_agent, name) for name in agents_to_get]
            agents = [f.result() for f in as_completed(futures)]

        # All agents should be valid
        assert all(a is not None for a in agents)


class TestThreadSafety:
    """Additional thread safety tests."""

    def test_shared_robots_across_threads(self):
        """Test sharing a single Robots instance across many threads."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        errors = []
        lock = threading.Lock()

        def worker(thread_id):
            try:
                for i in range(100):
                    # Vary operations
                    if i % 3 == 0:
                        robots.allowed(f"/path/{thread_id}/{i}", "*")
                    elif i % 3 == 1:
                        robots.allowed_batch([f"/a/{i}", f"/b/{i}"], "Googlebot")
                    else:
                        _ = robots.crawl_delay("*")
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread errors: {errors}"

    def test_high_contention(self):
        """High contention scenario with many threads."""
        robots = Robots.parse(SAMPLE_ROBOTS)
        results = []
        lock = threading.Lock()

        def check_many():
            local_results = []
            for _ in range(1000):
                r = robots.allowed("/private/data", "*")
                local_results.append(r)
            with lock:
                results.extend(local_results)

        threads = [threading.Thread(target=check_many) for _ in range(10)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All 10,000 results should be False
        assert len(results) == 10000
        assert all(r is False for r in results)
