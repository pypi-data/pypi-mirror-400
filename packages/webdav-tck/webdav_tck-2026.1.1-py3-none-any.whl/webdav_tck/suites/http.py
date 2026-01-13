"""HTTP protocol compliance test suite.

Ports src/http.c from the original litmus C implementation.
Tests low-level HTTP protocol features like Expect: 100-continue.
"""

from __future__ import annotations

import asyncio
import urllib.parse
from typing import TYPE_CHECKING

from webdav_tck.framework import (
    WebdavTckContext,
    WebdavTckTestResult,
    WebdavTckTestSuite,
)

if TYPE_CHECKING:
    from webdav_tck.session import WebdavTckSession


async def test_expect_100(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Expect: Test Expect: 100-continue header handling.

    Per RFC 2616 Section 8.2.3, when a client sends Expect: 100-continue,
    the server should respond with 100 Continue before reading the request body.
    """
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Skip for HTTPS - raw socket operations don't work well with SSL
    if session.base_url.startswith("https://"):
        context.context("skipping for SSL server")
        return WebdavTckTestResult.SKIP

    # Parse URL to get host and port
    parsed = urllib.parse.urlparse(session.base_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 80
    path = session.make_path("expect100")

    try:
        # Open raw TCP socket
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=10.0
        )

        # Build HTTP request with Expect: 100-continue
        # Include Content-Length but don't send body yet
        request_lines = [
            f"PUT {path} HTTP/1.1",
            f"Host: {host}:{port}",
            "X-Litmus: http",
            "User-Agent: webdav-tck/0.1.0",
            "Content-Length: 100",
            "Expect: 100-continue",
            "",
            "",  # Empty line to end headers
        ]
        request = "\r\n".join(request_lines)

        # Send request headers
        writer.write(request.encode("utf-8"))
        await writer.drain()

        # Wait for interim response (100 Continue) with timeout
        try:
            status_line = await asyncio.wait_for(reader.readline(), timeout=30.0)
        except asyncio.TimeoutError:
            context.context("timeout waiting for interim response")
            writer.close()
            await writer.wait_closed()
            return WebdavTckTestResult.FAIL

        if not status_line:
            context.context("no response from server")
            writer.close()
            await writer.wait_closed()
            return WebdavTckTestResult.FAIL

        # Parse status line
        status_str = status_line.decode("utf-8", errors="replace").strip()
        parts = status_str.split(None, 2)
        if len(parts) < 2:
            context.context(f"invalid status line: {status_str}")
            writer.close()
            await writer.wait_closed()
            return WebdavTckTestResult.FAIL

        # Check for 100 Continue
        try:
            status_code = int(parts[1])
        except ValueError:
            context.context(f"invalid status code: {parts[1]}")
            writer.close()
            await writer.wait_closed()
            return WebdavTckTestResult.FAIL

        if status_code == 100:
            # Got 100 Continue, now send the body
            body = b"\0" * 100  # Send 100 bytes of zeros
            writer.write(body)
            await writer.drain()

        # Clean up
        writer.close()
        await writer.wait_closed()

        return WebdavTckTestResult.OK

    except OSError as e:
        context.context(f"socket error: {e}")
        return WebdavTckTestResult.FAIL
    except Exception as e:
        context.context(f"unexpected error: {e}")
        return WebdavTckTestResult.FAIL


def create_http_suite(session: WebdavTckSession) -> WebdavTckTestSuite:
    """Create the HTTP protocol compliance test suite.

    Args:
        session: WebdavTck session

    Returns:
        Test suite with HTTP protocol tests
    """
    suite = WebdavTckTestSuite("http", session=session)

    # Add tests
    suite.add_test(test_expect_100)

    return suite
