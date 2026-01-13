"""COPY and MOVE operations test suite.

Ports src/copymove.c from the original litmus C implementation.
Tests the server's implementation of COPY and MOVE methods under various conditions.
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


async def test_copy_simple(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """COPY: Simple resource copy to new destination."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    src = session.make_path("copysrc")
    dest = session.make_path("copydest")

    # Create source resource
    content = b"This is the copy source file.\n"
    response = await session.client.put(src, content, test_name="copy_simple_setup")
    if response.status_code != 201:
        context.context(f"PUT source returned {response.status_code}, expected 201")
        return WebdavTckTestResult.FAILHARD

    # Copy it
    response = await session.client.copy(
        src, dest, overwrite=False, depth="infinity", test_name="copy_simple"
    )

    if response.status_code not in (200, 201, 204):
        context.context(
            f"COPY failed with {response.status_code}: expected 200, 201, or 204"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 201:
        context.warning("COPY to new resource should give 201 (RFC4918:S9.8.5)")

    # Verify destination exists with GET
    response = await session.client.get(dest, test_name="copy_simple_verify")
    if response.status_code != 200:
        context.context(f"GET copied resource returned {response.status_code}")
        return WebdavTckTestResult.FAIL

    if response.content != content:
        context.context("Copied content doesn't match source")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_copy_overwrite(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """COPY: Test overwrite behavior with Overwrite header."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    src = session.make_path("copysrc")
    dest = session.make_path("copydest")

    # Try to copy again with Overwrite: F (should fail)
    response = await session.client.copy(
        src, dest, overwrite=False, depth="infinity", test_name="copy_overwrite_false"
    )

    if response.status_code not in (400, 412):
        context.context(
            f"COPY with Overwrite: F on existing resource should fail with 412, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # Now with Overwrite: T (should succeed)
    response = await session.client.copy(
        src, dest, overwrite=True, depth="infinity", test_name="copy_overwrite_true"
    )

    if response.status_code not in (200, 204):
        context.context(
            f"COPY with Overwrite: T returned {response.status_code}, expected 204"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 204:
        context.warning(
            f"COPY to existing resource should give 204 (RFC4918:S9.8.5), got {response.status_code}"
        )

    return WebdavTckTestResult.OK


async def test_copy_nodestcoll(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """COPY: Copy into non-existent collection (expect 409)."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    src = session.make_path("copysrc")
    nodest = session.make_path("nonesuch", "foo")

    response = await session.client.copy(
        src, nodest, overwrite=False, depth="0", test_name="copy_nodestcoll"
    )

    if response.status_code == 201:
        context.context(
            "COPY into non-existent collection succeeded (should have failed)"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 409:
        context.warning(
            f"COPY to non-existent collection gave {response.status_code}, expected 409 (RFC4918:S9.8.5)"
        )

    return WebdavTckTestResult.OK


async def test_copy_coll(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """COPY: Recursive collection copy with Depth: infinity."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    csrc = session.make_path("ccsrc")
    cdest = session.make_path("ccdest")
    subsrc = session.make_path("ccsrc", "subcoll")

    # Create source collection
    response = await session.client.mkcol(csrc, test_name="copy_coll_setup")
    if response.status_code != 201:
        context.context(f"MKCOL for source collection failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    # Add multiple resources to the collection
    content = b"Resource content\n"
    for n in range(10):
        path = session.make_path("ccsrc", f"foo.{n}")
        response = await session.client.put(
            path, content, test_name=f"copy_coll_setup_{n}"
        )
        if response.status_code != 201:
            context.context(f"PUT resource {n} failed: {response.status_code}")
            return WebdavTckTestResult.FAILHARD

    # Create subcollection
    response = await session.client.mkcol(subsrc, test_name="copy_coll_setup_sub")
    if response.status_code != 201:
        context.context(f"MKCOL for subcollection failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    # Clean up destination if it exists
    await session.client.delete(cdest, test_name="copy_coll_cleanup")

    # Copy the collection with Depth: infinity
    response = await session.client.copy(
        csrc, cdest, overwrite=False, depth="infinity", test_name="copy_coll"
    )

    if response.status_code not in (200, 201, 204):
        context.context(f"Collection COPY failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Delete source to be sure we're checking the copy
    await session.client.delete(csrc, test_name="copy_coll_del_src")

    # Verify all resources were copied
    for n in range(10):
        path = session.make_path("ccdest", f"foo.{n}")
        response = await session.client.delete(path, test_name=f"copy_coll_verify_{n}")
        if response.status_code not in (200, 204):
            context.context(f"Copied resource {n} not found at {path}")
            return WebdavTckTestResult.FAIL

    # Verify subcollection was copied
    subdest = session.make_path("ccdest", "subcoll")
    response = await session.client.delete(subdest, test_name="copy_coll_verify_sub")
    if response.status_code not in (200, 204):
        context.context("Copied subcollection not found")
        return WebdavTckTestResult.FAIL

    # Cleanup
    await session.client.delete(cdest, test_name="copy_coll_cleanup")

    return WebdavTckTestResult.OK


async def test_copy_shallow(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """COPY: Non-recursive collection copy with Depth: 0."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    csrc = session.make_path("ccsrc_shallow")
    cdest = session.make_path("ccdest_shallow")

    # Create source collection with one member
    response = await session.client.mkcol(csrc, test_name="copy_shallow_setup")
    if response.status_code != 201:
        context.context(f"MKCOL failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    content = b"Member content\n"
    member_path = session.make_path("ccsrc_shallow", "foo")
    response = await session.client.put(
        member_path, content, test_name="copy_shallow_setup_member"
    )
    if response.status_code != 201:
        context.context(f"PUT member failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    # Clean destination
    await session.client.delete(cdest, test_name="copy_shallow_cleanup")

    # Copy with Depth: 0 (should copy collection but not members)
    response = await session.client.copy(
        csrc, cdest, overwrite=False, depth="0", test_name="copy_shallow"
    )

    if response.status_code not in (200, 201, 204):
        context.context(f"Shallow COPY failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Delete source
    await session.client.delete(csrc, test_name="copy_shallow_del_src")

    # Verify member was NOT copied
    dest_member = session.make_path("ccdest_shallow", "foo")
    response = await session.client.delete(dest_member, test_name="copy_shallow_verify")

    if response.status_code != 404:
        context.context(
            f"Shallow COPY should not have copied member, but DELETE returned {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # Cleanup
    await session.client.delete(cdest, test_name="copy_shallow_cleanup")

    return WebdavTckTestResult.OK


async def test_move(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MOVE: Basic resource move operations."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    src = session.make_path("movesrc")
    src2 = session.make_path("movesrc2")
    dest = session.make_path("movedest")

    # Create source resources
    content = b"Move source content\n"
    response = await session.client.put(src, content, test_name="move_setup")
    if response.status_code != 201:
        context.context(f"PUT source failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    response = await session.client.put(src2, content, test_name="move_setup2")
    if response.status_code != 201:
        context.context(f"PUT source2 failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    # Move first resource
    response = await session.client.move(src, dest, overwrite=False, test_name="move")

    if response.status_code not in (200, 201, 204):
        context.context(f"MOVE failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    if response.status_code != 201:
        context.warning(
            f"MOVE to new resource should give 201, got {response.status_code}"
        )

    # Verify source no longer exists
    response = await session.client.get(src, test_name="move_verify_src")
    if response.status_code != 404:
        context.context("MOVE source still exists after move")
        return WebdavTckTestResult.FAIL

    # Try MOVE with Overwrite: F to existing destination (should fail)
    response = await session.client.move(
        src2, dest, overwrite=False, test_name="move_overwrite_false"
    )

    if response.status_code not in (400, 412):
        context.context(
            f"MOVE with Overwrite: F should fail with 412, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # MOVE with Overwrite: T (should succeed)
    response = await session.client.move(
        src2, dest, overwrite=True, test_name="move_overwrite_true"
    )

    if response.status_code not in (200, 204):
        context.context(f"MOVE with Overwrite: T failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    if response.status_code != 204:
        context.warning(
            f"MOVE to existing resource should give 204, got {response.status_code}"
        )

    # Cleanup
    await session.client.delete(dest, test_name="move_cleanup")

    return WebdavTckTestResult.OK


async def _setup_move_coll_resources(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult | None:
    """Set up collection with resources for move test. Returns error or None."""
    assert session.client is not None  # Caller must verify
    msrc = session.make_path("mvsrc")
    subsrc = session.make_path("mvsrc", "subcoll")

    response = await session.client.mkcol(msrc, test_name="move_coll_setup")
    if response.status_code != 201:
        context.context(f"MKCOL failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    content = b"Resource content\n"
    for n in range(10):
        path = session.make_path("mvsrc", f"foo.{n}")
        response = await session.client.put(
            path, content, test_name=f"move_coll_setup_{n}"
        )
        if response.status_code != 201:
            context.context(f"PUT resource {n} failed: {response.status_code}")
            return WebdavTckTestResult.FAILHARD

    response = await session.client.mkcol(subsrc, test_name="move_coll_setup_sub")
    if response.status_code != 201:
        context.context(f"MKCOL subcollection failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    return None


async def _verify_moved_resources(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult | None:
    """Verify resources were moved. Returns error or None."""
    assert session.client is not None  # Caller must verify
    for n in range(10):
        path = session.make_path("mvdest", f"foo.{n}")
        response = await session.client.delete(path, test_name=f"move_coll_verify_{n}")
        if response.status_code not in (200, 204):
            context.context(f"Moved resource {n} not found")
            return WebdavTckTestResult.FAIL

    subdest = session.make_path("mvdest", "subcoll")
    response = await session.client.delete(subdest, test_name="move_coll_verify_sub")
    if response.status_code not in (200, 204):
        context.context("Moved subcollection not found")
        return WebdavTckTestResult.FAIL

    return None


async def test_move_coll(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """MOVE: Move collection with members."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    msrc = session.make_path("mvsrc")
    mdest = session.make_path("mvdest")

    # Setup
    if error := await _setup_move_coll_resources(session, context):
        return error

    # Move the collection
    response = await session.client.move(
        msrc, mdest, overwrite=False, test_name="move_coll"
    )
    if response.status_code not in (200, 201, 204):
        context.context(f"Collection MOVE failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Verify source no longer exists
    response = await session.client.get(msrc, test_name="move_coll_verify_src")
    if response.status_code != 404:
        context.context("MOVE source collection still exists")
        return WebdavTckTestResult.FAIL

    # Verify moved resources
    if error := await _verify_moved_resources(session, context):
        return error

    # Cleanup
    await session.client.delete(mdest, test_name="move_coll_cleanup")

    return WebdavTckTestResult.OK


def create_copymove_suite(session: WebdavTckSession) -> WebdavTckTestSuite:
    """Create the copymove test suite.

    Args:
        session: WebdavTck session

    Returns:
        Test suite with COPY/MOVE tests
    """
    suite = WebdavTckTestSuite("copymove", session=session)

    # Add tests in order
    tests = [
        test_copy_simple,
        test_copy_overwrite,
        test_copy_nodestcoll,
        test_copy_coll,
        test_copy_shallow,
        test_move,
        test_move_coll,
    ]

    for test_func in tests:
        suite.add_test(test_func)

    return suite
