"""CLI entry point for WebDAV test suite."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click

from webdav_tck.framework import TestRunner
from webdav_tck.session import WebdavTckSession
from webdav_tck.suites.basic import create_basic_suite
from webdav_tck.suites.copymove import create_copymove_suite
from webdav_tck.suites.http import create_http_suite
from webdav_tck.suites.largefile import create_largefile_suite
from webdav_tck.suites.locks import create_locks_suite
from webdav_tck.suites.props import create_props_suite

if TYPE_CHECKING:
    from collections.abc import Callable

    from webdav_tck.framework.suite import WebdavTckTestSuite

# Map suite names to their factory functions
SUITE_FACTORIES: dict[str, Callable[[WebdavTckSession], WebdavTckTestSuite]] = {
    "basic": create_basic_suite,
    "copymove": create_copymove_suite,
    "props": create_props_suite,
    "locks": create_locks_suite,
    "http": create_http_suite,
    "largefile": create_largefile_suite,
}


def _get_suite_list(suites: str | None) -> list[str]:
    """Parse and validate suite list from command line."""
    available = list(SUITE_FACTORIES.keys())
    if not suites:
        return available
    return [s.strip() for s in suites.split(",") if s.strip() in available]


async def _run_test_session(
    session: WebdavTckSession,
    runner: TestRunner,
    suite_list: list[str],
    url: str,
    username: str | None,
) -> int:
    """Run test session with initialized session and runner."""
    click.echo(f"Testing WebDAV server: {url}")
    if username:
        click.echo(f"Using authentication: {username}")

    runner.log_debug(f"Connecting to {url}")
    await session.discover_capabilities()

    class_level = "Class 2 (locking)" if session.class2 else "Class 1 (basic)"
    click.echo(f"Server supports WebDAV {class_level}")

    await session.create_test_collection()
    runner.log_debug(f"Created test collection: {session.base_path}")

    for suite_name in suite_list:
        factory = SUITE_FACTORIES[suite_name]
        suite = factory(session)
        await runner.run_suite(suite)

    await session.cleanup_test_collection()
    runner.print_summary()
    return runner.get_exit_code()


async def run_tck(
    url: str,
    username: str | None,
    password: str | None,
    proxy: str | None,
    system_proxy: bool,
    client_cert: str | None,
    insecure: bool,
    quiet: bool,
    colour: bool | None,
    suites: str | None,
) -> int:
    """Run WebDAV TCK test suites."""
    suite_list = _get_suite_list(suites)
    if not suite_list:
        click.echo("No valid test suites specified", err=True)
        return 1

    debug_log = Path("debug.log")
    session = WebdavTckSession(
        url=url,
        username=username,
        password=password,
        verify_ssl=not insecure,
        proxy=proxy if not system_proxy else None,
        client_cert=client_cert,
        debug_log=debug_log,
    )

    with TestRunner(quiet=quiet, use_color=colour, debug_log=debug_log) as runner:
        try:
            async with session:
                return await _run_test_session(
                    session, runner, suite_list, url, username
                )
        except KeyboardInterrupt:
            click.echo("\n\nInterrupted by user", err=True)
            return 130
        except Exception as e:
            click.echo(f"\n\nFatal error: {e}", err=True)
            runner.log_debug(f"Fatal error: {e}")
            return 1


@click.command()
@click.argument("url")
@click.argument("username", required=False)
@click.argument("password", required=False)
@click.option("--proxy", "-p", help="Proxy server URL")
@click.option(
    "--system-proxy", "-s", is_flag=True, help="Use system proxy configuration"
)
@click.option("--client-cert", "-c", help="PKCS#12 client certificate path")
@click.option(
    "--insecure", "-i", is_flag=True, help="Ignore TLS certificate verification"
)
@click.option("--quiet", "-q", is_flag=True, help="Use abbreviated output")
@click.option(
    "--colour/--no-colour",
    default=None,
    help="Force color output on/off (default: auto-detect)",
)
@click.option("--suites", help="Comma-separated list of test suites to run")
@click.version_option()
def main(
    url: str,
    username: str | None,
    password: str | None,
    proxy: str | None,
    system_proxy: bool,
    client_cert: str | None,
    insecure: bool,
    quiet: bool,
    colour: bool | None,
    suites: str | None,
) -> None:
    """Run WebDAV test suite against URL.

    \b
    Examples:
        dav-tck http://localhost/webdav/
        dav-tck http://localhost/webdav/ user password
        dav-tck --insecure https://localhost/webdav/
        dav-tck --quiet --suites=basic http://localhost/webdav/

    The test suite will create a collection called 'webdav-tck' at the
    specified URL and run various WebDAV protocol compliance tests.
    """
    # Validate URL
    if not url.startswith("http://") and not url.startswith("https://"):
        click.echo("Error: URL must start with http:// or https://", err=True)
        sys.exit(1)

    # Validate credentials
    if username and not password:
        click.echo("Error: Password required when username is provided", err=True)
        sys.exit(1)

    if password and not username:
        click.echo("Error: Username required when password is provided", err=True)
        sys.exit(1)

    # Run async main
    exit_code = asyncio.run(
        run_tck(
            url=url,
            username=username,
            password=password,
            proxy=proxy,
            system_proxy=system_proxy,
            client_cert=client_cert,
            insecure=insecure,
            quiet=quiet,
            colour=colour,
            suites=suites,
        )
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
