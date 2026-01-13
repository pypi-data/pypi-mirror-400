"""Basic WebDAV operations test suite.

Ports src/basic.c from the original litmus C implementation.
Tests fundamental HTTP and WebDAV methods for creating, retrieving,
and deleting resources and collections.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from webdav_tck.framework import (
    WebdavTckContext,
    WebdavTckTestResult,
    WebdavTckTestSuite,
)

if TYPE_CHECKING:
    from webdav_tck.session import WebdavTckSession


async def test_options(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """OPTIONS: Check OPTIONS request and DAV header."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    response = await session.client.options(session.base_path, test_name="options")

    # Accept 200 or 204 (both are valid per HTTP spec)
    if response.status_code not in (200, 204):
        context.context(f"OPTIONS returned {response.status_code}, expected 200 or 204")
        return WebdavTckTestResult.FAIL

    dav_header = response.headers.get("DAV", "")
    if not dav_header:
        context.context("No DAV header in OPTIONS response")
        return WebdavTckTestResult.FAIL

    if "1" not in dav_header:
        context.context(f"DAV header does not indicate Class 1 support: {dav_header}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_put_get(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PUT/GET: Create resource with PUT, verify with GET."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("res1")
    content = b"This is a test file for WebDAV testing.\n"

    # PUT the resource
    response = await session.client.put(path, content, test_name="put_get")

    if response.status_code != 201:
        context.context(f"PUT returned {response.status_code}, expected 201")
        return WebdavTckTestResult.FAIL

    # GET the resource back
    response = await session.client.get(path, test_name="put_get")

    if response.status_code != 200:
        context.context(f"GET returned {response.status_code}, expected 200")
        return WebdavTckTestResult.FAIL

    # Verify content matches byte-for-byte
    if response.content != content:
        context.context("GET content does not match PUT content")
        return WebdavTckTestResult.FAIL

    # Store ETag if present
    etag = response.headers.get("ETag")
    if etag:
        session.store_etag(path, etag)

    return WebdavTckTestResult.OK


async def test_put_get_utf8_segment(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PUT/GET: UTF-8 character in URI (€ as %e2%82%ac)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Use UTF-8 character in path (€ = euro sign)
    path = session.make_path("res-%E2%82%AC")
    content = b"UTF-8 filename test\n"

    # PUT the resource
    response = await session.client.put(path, content, test_name="put_get_utf8_segment")

    if response.status_code != 201:
        context.context(f"PUT returned {response.status_code}, expected 201")
        return WebdavTckTestResult.FAIL

    # GET the resource back
    response = await session.client.get(path, test_name="put_get_utf8_segment")

    if response.status_code != 200:
        context.context(f"GET returned {response.status_code}, expected 200")
        return WebdavTckTestResult.FAIL

    # Verify content
    if response.content != content:
        context.context("GET content does not match PUT content")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_put_no_parent(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PUT: PUT to non-existent parent collection (expect 409)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Try to PUT into a collection that doesn't exist
    path = session.make_path("noparent", "res")
    content = b"test\n"

    response = await session.client.put(path, content, test_name="put_no_parent")

    if response.status_code != 409:
        context.context(f"PUT returned {response.status_code}, expected 409 Conflict")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_mkcol(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MKCOL: Create collection."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("coll1")

    response = await session.client.mkcol(path, test_name="mkcol")

    if response.status_code != 201:
        context.context(f"MKCOL returned {response.status_code}, expected 201")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_mkcol_again(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MKCOL: Create same collection twice (should fail)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("coll1")

    # Try to create again (should fail)
    response = await session.client.mkcol(path, test_name="mkcol_again")

    if response.status_code in (200, 201):
        context.context(f"MKCOL returned {response.status_code}, should have failed")
        return WebdavTckTestResult.FAIL

    # Expected: 405 Method Not Allowed or similar
    if response.status_code not in (405, 409):
        context.warning(f"MKCOL returned {response.status_code}, expected 405 or 409")

    return WebdavTckTestResult.OK


async def test_delete(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """DELETE: Delete a resource."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("res1")

    response = await session.client.delete(path, test_name="delete")

    if response.status_code not in (200, 204):
        context.context(f"DELETE returned {response.status_code}, expected 200 or 204")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_delete_null(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """DELETE: Delete non-existent resource (expect 404)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("nothere")

    response = await session.client.delete(path, test_name="delete_null")

    if response.status_code != 404:
        context.context(f"DELETE returned {response.status_code}, expected 404")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_delete_coll(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """DELETE: Delete empty collection."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("coll1")

    response = await session.client.delete(path, test_name="delete_coll")

    if response.status_code not in (200, 204):
        context.context(f"DELETE returned {response.status_code}, expected 200 or 204")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_mkcol_no_parent(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MKCOL: Create collection in non-existent parent (expect 409)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("noparent", "coll")

    response = await session.client.mkcol(path, test_name="mkcol_no_parent")

    if response.status_code != 409:
        context.context(f"MKCOL returned {response.status_code}, expected 409 Conflict")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_mkcol_with_body(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MKCOL: MKCOL with request body (expect 415)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("coll2")
    body = b"<test>body</test>"

    response = await session.client.mkcol(path, test_name="mkcol_with_body", body=body)

    # Per RFC 4918, server must reject MKCOL with unsupported Content-Type
    if response.status_code == 201:
        context.context("MKCOL with body returned 201, should have failed")
        return WebdavTckTestResult.FAIL

    # Expected: 415 Unsupported Media Type
    if response.status_code != 415:
        context.warning(
            f"MKCOL with body returned {response.status_code}, expected 415"
        )

    return WebdavTckTestResult.OK


def create_basic_suite(session: WebdavTckSession) -> WebdavTckTestSuite:
    """Create the basic test suite.

    Args:
        session: WebdavTck session

    Returns:
        Test suite with basic tests
    """
    suite = WebdavTckTestSuite("basic", session=session)

    # Add tests in order
    tests = [
        test_options,
        test_put_get,
        test_put_get_utf8_segment,
        test_put_no_parent,
        test_mkcol,
        test_mkcol_again,
        test_delete,
        test_delete_null,
        test_delete_coll,
        test_mkcol_no_parent,
        test_mkcol_with_body,
    ]

    for test_func in tests:
        suite.add_test(test_func)

    return suite
