"""
Command-line interface for fastrobots.

Usage:
    fastrobots check URL [--agent AGENT]
    fastrobots parse URL [--json]
    fastrobots benchmark [FILE] [--iterations N]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import click

from fastrobots._core import Robots, robots_url, url_path
from fastrobots.client import fetch, FetchError


@click.group()
@click.version_option(version="0.3.0", prog_name="fastrobots")
def main():
    """Blazingly fast robots.txt parser."""
    pass


@main.command()
@click.argument("url")
@click.option(
    "--agent", "-a",
    default="*",
    help="User-agent to check (default: *)",
)
def check(url: str, agent: str):
    """Check if a URL is allowed for a user-agent."""
    try:
        robots = fetch(url)
        path = url_path(url)
        allowed = robots.allowed(path, agent)

        if allowed:
            click.secho(f"✓ ALLOWED: {path}", fg="green")
        else:
            click.secho(f"✗ DISALLOWED: {path}", fg="red")

        sys.exit(0 if allowed else 1)

    except FetchError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(2)


@main.command()
@click.argument("url")
@click.option(
    "--json", "-j", "as_json",
    is_flag=True,
    help="Output as JSON",
)
def parse(url: str, as_json: bool):
    """Parse and display robots.txt for a URL."""
    try:
        robots = fetch(url)

        if as_json:
            output = {
                "url": robots_url(url),
                "user_agents": robots.user_agents,
                "sitemaps": robots.sitemaps,
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.secho(f"robots.txt for {robots_url(url)}", fg="blue", bold=True)
            click.echo()

            click.secho("User-agents:", fg="cyan")
            for agent in robots.user_agents:
                delay = robots.crawl_delay(agent)
                delay_str = f" (crawl-delay: {delay}s)" if delay else ""
                click.echo(f"  • {agent}{delay_str}")

            if robots.sitemaps:
                click.echo()
                click.secho("Sitemaps:", fg="cyan")
                for sitemap in robots.sitemaps:
                    click.echo(f"  • {sitemap}")

    except FetchError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@main.command()
@click.argument("file", type=click.Path(exists=True), required=False)
@click.option(
    "--iterations", "-n",
    default=10000,
    help="Number of iterations for benchmark",
)
@click.option(
    "--check-iterations", "-c",
    default=100000,
    help="Number of URL check iterations",
)
def benchmark(file: str | None, iterations: int, check_iterations: int):
    """Benchmark parsing and URL checking speed."""
    # Sample robots.txt for benchmarking
    sample_content = """
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

    if file:
        content = Path(file).read_text()
        click.secho(f"Using robots.txt from: {file}", fg="blue")
    else:
        content = sample_content
        click.secho("Using sample robots.txt", fg="blue")

    click.echo()

    # Benchmark parsing
    click.secho("Parsing benchmark:", fg="cyan", bold=True)
    start = time.perf_counter()
    for _ in range(iterations):
        Robots.parse(content)
    elapsed = time.perf_counter() - start

    parses_per_sec = iterations / elapsed
    click.echo(f"  Iterations: {iterations:,}")
    click.echo(f"  Time: {elapsed:.3f}s")
    click.echo(f"  Speed: {parses_per_sec:,.0f} parses/sec")

    click.echo()

    # Benchmark URL checking
    click.secho("URL checking benchmark:", fg="cyan", bold=True)
    robots = Robots.parse(content)

    test_paths = [
        "/admin/users",
        "/public/page",
        "/api/public/endpoint",
        "/api/internal/secret",
        "/random/path",
        "/private/data",
    ]

    start = time.perf_counter()
    for i in range(check_iterations):
        path = test_paths[i % len(test_paths)]
        robots.allowed(path, "Googlebot")
    elapsed = time.perf_counter() - start

    checks_per_sec = check_iterations / elapsed
    click.echo(f"  Iterations: {check_iterations:,}")
    click.echo(f"  Time: {elapsed:.3f}s")
    click.echo(f"  Speed: {checks_per_sec:,.0f} checks/sec")

    click.echo()
    click.secho("Summary:", fg="green", bold=True)
    click.echo(f"  Parse speed:  {parses_per_sec:>12,.0f} /sec")
    click.echo(f"  Check speed:  {checks_per_sec:>12,.0f} /sec")


if __name__ == "__main__":
    main()
