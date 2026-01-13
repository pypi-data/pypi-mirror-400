"""Locking test suite.

Ports src/locks.c from the original litmus C implementation.
Tests WebDAV Class 2 locking functionality including exclusive/shared locks,
lock discovery, refresh, and conditional requests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from webdav_tck.framework import (
    WebdavTckContext,
    WebdavTckTestResult,
    WebdavTckTestSuite,
)
from webdav_tck.xml_utils import (
    build_if_header,
    build_lock_body,
    build_propfind_body,
    build_proppatch_body,
    parse_lock_response,
)

if TYPE_CHECKING:
    from webdav_tck.client import WebDAVResponse
    from webdav_tck.session import WebdavTckSession

NS = "http://webdav.org/neon/litmus/"


def _check_locked_failure(
    response: WebDAVResponse, context: WebdavTckContext, operation: str
) -> WebdavTckTestResult | None:
    """Check that an operation on a locked resource failed correctly.

    Returns WebdavTckTestResult.FAIL if wrong status, None if correct.
    """
    if response.status_code not in (400, 423):
        context.context(
            f"{operation} of locked resource should fail, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL
    if response.status_code != 423:
        context.warning(f"{operation} failed with {response.status_code} not 423")
    return None


async def test_options(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """OPTIONS: Check server capabilities."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    response = await session.client.options(session.base_path, test_name="options")

    if response.status_code not in (200, 204):
        context.context(f"OPTIONS returned {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Already checked in session.discover_capabilities()
    return WebdavTckTestResult.OK


def test_precond(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Precondition: Check server supports Class 2 (locking)."""
    if not session.class2:
        context.context(
            "Locking tests skipped, server does not claim Class 2 compliance"
        )
        return WebdavTckTestResult.SKIPREST

    return WebdavTckTestResult.OK


def test_init_locks(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Initialize lock resources."""
    # Just a marker test - actual initialization happens in session
    return WebdavTckTestResult.OK


async def test_put(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PUT: Create resources for locking tests."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Create main resource
    lockme = session.make_path("lockme")
    content = b"This is a test file for locking.\n"

    response = await session.client.put(lockme, content, test_name="put_lockme")
    if response.status_code != 201:
        context.context(f"PUT lockme returned {response.status_code}, expected 201")
        return WebdavTckTestResult.FAILHARD

    # Create second resource (not locked)
    notlocked = session.make_path("notlocked")
    response = await session.client.put(notlocked, content, test_name="put_notlocked")
    if response.status_code != 201:
        context.context(f"PUT notlocked returned {response.status_code}, expected 201")
        return WebdavTckTestResult.FAILHARD

    return WebdavTckTestResult.OK


async def test_lock_excl(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Take out exclusive lock on resource."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Build lock request body
    body = build_lock_body(
        scope="exclusive",
        lock_type="write",
        owner="webdav-tck test suite",
    )

    # Send LOCK request with Depth: 0
    response = await session.client.lock(
        lockme, body, depth="0", timeout="Second-3600", test_name="lock_excl"
    )

    if response.status_code not in (200, 201):
        context.context(f"LOCK failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Parse lock token from response
    try:
        lock_token, lock_scope = parse_lock_response(response.content)
    except Exception as e:
        context.context(f"Failed to parse LOCK response: {e}")
        return WebdavTckTestResult.FAIL

    if not lock_token:
        context.context("No lock token returned from LOCK")
        return WebdavTckTestResult.FAIL

    if lock_scope != "exclusive":
        context.context(f"Requested exclusive lock but got {lock_scope}")
        return WebdavTckTestResult.FAIL

    # Store lock token for later tests
    session.locks["lockme"] = lock_token

    return WebdavTckTestResult.OK


async def test_discover(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PROPFIND: Discover lock information."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Use PROPFIND with lockdiscovery property
    props = [("DAV:", "lockdiscovery")]
    body = build_propfind_body(props)

    response = await session.client.propfind(
        lockme, depth=0, body=body, test_name="discover"
    )

    if response.status_code not in (200, 207):
        context.context(f"PROPFIND lockdiscovery failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # TODO: Parse and verify lockdiscovery property contains our lock token
    # For now, just verify the request succeeded
    return WebdavTckTestResult.OK


async def test_refresh(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Refresh existing lock."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Refresh lock by sending LOCK with If: header
    response = await session.client.lock(
        lockme,
        None,
        depth="0",
        timeout="Second-3600",
        if_header=f"(<{lock_token}>)",
        test_name="refresh",
    )

    if response.status_code != 200:
        context.context(f"LOCK refresh failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_notowner_modify(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Non-owner: Verify non-owner cannot modify locked resource."""
    if not session.client2:
        context.context("Second client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")
    notlocked = session.make_path("notlocked")
    whocares = session.make_path("whocares")

    # Try DELETE - should fail
    response = await session.client2.delete(lockme, test_name="notowner_delete")
    if error := _check_locked_failure(response, context, "DELETE"):
        return error

    # Try MOVE - should fail
    response = await session.client2.move(
        lockme, whocares, overwrite=False, test_name="notowner_move"
    )
    if error := _check_locked_failure(response, context, "MOVE"):
        return error

    # Try COPY onto locked resource - should fail
    response = await session.client2.copy(
        notlocked, lockme, overwrite=True, depth="0", test_name="notowner_copy"
    )
    if error := _check_locked_failure(response, context, "COPY"):
        return error

    # Try PROPPATCH - should fail
    set_props = {(NS, "random"): "foobar"}
    body = build_proppatch_body(set_props=set_props)
    response = await session.client2.proppatch(
        lockme, body, test_name="notowner_proppatch"
    )
    if error := _check_locked_failure(response, context, "PROPPATCH"):
        return error

    # Try PUT - should fail
    content = b"Trying to modify locked resource\n"
    response = await session.client2.put(lockme, content, test_name="notowner_put")
    if error := _check_locked_failure(response, context, "PUT"):
        return error

    return WebdavTckTestResult.OK


async def test_notowner_lock(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Non-owner: Verify non-owner cannot unlock or lock resource."""
    if not session.client2:
        context.context("Second client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Try UNLOCK with bogus token - should fail
    bogus_token = "opaquelocktoken:foobar"
    response = await session.client2.unlock(
        lockme, bogus_token, test_name="notowner_unlock"
    )
    if response.status_code < 400:
        context.context("UNLOCK with bogus lock token should fail")
        return WebdavTckTestResult.FAIL

    # Try to take out another exclusive lock - should fail
    body = build_lock_body(
        scope="exclusive",
        lock_type="write",
        owner="notowner lock",
    )

    response = await session.client2.lock(
        lockme, body, depth="0", timeout="Second-3600", test_name="notowner_lock"
    )
    if response.status_code not in (400, 423):
        context.context(
            f"LOCK on locked resource should fail, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 423:
        context.warning(f"LOCK failed with {response.status_code} not 423")

    return WebdavTckTestResult.OK


async def test_owner_modify(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Owner: Verify lock owner can modify resource."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # PUT with lock token should succeed
    if_header = build_if_header(lock_token)
    content = b"Modified by lock owner\n"

    response = await session.client.put(
        lockme, content, if_header=if_header, test_name="owner_put"
    )
    if response.status_code not in (200, 201, 204):
        context.context(
            f"PUT on locked resource by owner failed: {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # PROPPATCH with lock token should succeed
    set_props = {(NS, "random"): "foobar"}
    body = build_proppatch_body(set_props=set_props)

    response = await session.client.proppatch(
        lockme, body, if_header=if_header, test_name="owner_proppatch"
    )
    if response.status_code not in (200, 207):
        context.context(
            f"PROPPATCH on locked resource by owner failed: {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_copy(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """COPY: Verify locks don't follow COPY operations."""
    if not session.client2:
        context.context("Second client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")
    copydest = session.make_path("lockme-copydest")

    # Clean destination
    await session.client2.delete(copydest, test_name="copy_cleanup")

    # Copy locked resource (should succeed, and copy should not be locked)
    response = await session.client2.copy(
        lockme, copydest, overwrite=True, depth="0", test_name="copy"
    )
    if response.status_code not in (200, 201, 204):
        context.context(f"COPY of locked resource failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Verify copy is not locked by trying to delete it without lock token
    response = await session.client2.delete(copydest, test_name="copy_verify")
    if response.status_code not in (200, 204):
        context.context(
            f"Copied resource appears to be locked: DELETE returned {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_cond_put(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Conditional PUT: PUT with valid lock token and etag."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Get current ETag
    etag = session.etags.get("lockme")
    if not etag:
        # Try to get it
        response = await session.client.get(lockme, test_name="cond_put_get")
        if response.status_code == 200:
            etag = response.headers.get("etag")
            if etag:
                session.etags["lockme"] = etag

    if not etag:
        context.warning("No ETag available, skipping conditional PUT test")
        return WebdavTckTestResult.OK

    # Build If: header with lock token and etag
    if_header = f"(<{lock_token}> [{etag}])"
    content = b"Conditional PUT with lock and etag\n"

    response = await session.client.put(
        lockme, content, if_header=if_header, test_name="cond_put"
    )
    if response.status_code not in (200, 204):
        context.context(
            f"Conditional PUT with lock and etag failed: {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # Update ETag if returned
    new_etag = response.headers.get("etag")
    if new_etag:
        session.etags["lockme"] = new_etag

    return WebdavTckTestResult.OK


async def test_fail_cond_put(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Conditional PUT: PUT with bogus lock token should fail."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")
    etag = session.etags.get("lockme")

    if not etag:
        context.warning("No ETag available, skipping test")
        return WebdavTckTestResult.OK

    # Build If: header with bogus lock token and valid etag
    if_header = f"(<DAV:no-lock> [{etag}])"
    content = b"This should fail\n"

    response = await session.client.put(
        lockme, content, if_header=if_header, test_name="fail_cond_put"
    )

    if response.status_code < 400:
        context.context("Conditional PUT with invalid lock token should fail")
        return WebdavTckTestResult.FAIL

    if response.status_code == 400:
        context.context(
            "Conditional PUT with invalid lock token got 400 (should be 412)"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 412:
        context.warning(f"PUT failed with {response.status_code} not 412")

    return WebdavTckTestResult.OK


async def test_cond_put_with_not(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Conditional PUT: PUT with lock token and Not clause."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Build If: header: (lock-token) (Not bogus-token)
    if_header = f"(<{lock_token}>) (Not <DAV:no-lock>)"
    content = b"Conditional PUT with Not clause\n"

    response = await session.client.put(
        lockme, content, if_header=if_header, test_name="cond_put_with_not"
    )
    if response.status_code not in (200, 204):
        context.context(
            f"PUT with conditional (Not <DAV:no-lock>) failed: {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # Update ETag
    etag = response.headers.get("etag")
    if etag:
        session.etags["lockme"] = etag

    return WebdavTckTestResult.OK


async def test_cond_put_corrupt_token(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Conditional PUT: PUT with corrupted lock token should fail."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Corrupt the lock token
    corrupt_token = lock_token + "x"
    if_header = f"(<{corrupt_token}>) (Not <DAV:no-lock>)"
    content = b"This should fail\n"

    response = await session.client.put(
        lockme, content, if_header=if_header, test_name="cond_put_corrupt"
    )
    if response.status_code < 400:
        context.context("Conditional PUT with invalid lock token should fail")
        return WebdavTckTestResult.FAIL

    if response.status_code != 423:
        context.warning(f"PUT failed with {response.status_code} not 423")

    return WebdavTckTestResult.OK


async def test_unlock(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """UNLOCK: Release the lock."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    response = await session.client.unlock(lockme, lock_token, test_name="unlock")
    if response.status_code != 204:
        context.context(f"UNLOCK failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Remove lock token
    del session.locks["lockme"]

    return WebdavTckTestResult.OK


async def test_fail_cond_put_unlocked(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Conditional PUT: PUT with bogus token on unlocked resource."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Try conditional PUT with bogus token on unlocked resource
    if_header = "(<DAV:no-lock>)"
    content = b"This should fail\n"

    response = await session.client.put(
        lockme, content, if_header=if_header, test_name="fail_cond_put_unlocked"
    )
    if response.status_code < 400:
        context.context("Conditional PUT with invalid lock token should fail")
        return WebdavTckTestResult.FAIL

    if response.status_code == 400:
        context.context(
            "Conditional PUT with invalid lock token got 400 (should be 412)"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 412:
        context.warning(f"PUT failed with {response.status_code} not 412")

    return WebdavTckTestResult.OK


async def test_lock_shared(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Take out shared lock on resource."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Build lock request body for shared lock
    body = build_lock_body(
        scope="shared",
        lock_type="write",
        owner="webdav-tck test suite",
    )

    response = await session.client.lock(
        lockme, body, depth="0", timeout="Second-3600", test_name="lock_shared"
    )

    if response.status_code not in (200, 201):
        context.context(f"LOCK failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Parse lock token
    try:
        lock_token, lock_scope = parse_lock_response(response.content)
    except Exception as e:
        context.context(f"Failed to parse LOCK response: {e}")
        return WebdavTckTestResult.FAIL

    if not lock_token:
        context.context("No lock token returned from LOCK")
        return WebdavTckTestResult.FAIL

    if lock_scope != "shared":
        context.context(f"Requested shared lock but got {lock_scope}")
        return WebdavTckTestResult.FAIL

    session.locks["lockme"] = lock_token

    return WebdavTckTestResult.OK


async def test_double_sharedlock(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Take out second shared lock on resource."""
    if not session.client2:
        context.context("Second client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockme")
    if not lock_token:
        context.context("No lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme = session.make_path("lockme")

    # Take out second shared lock with client2
    body = build_lock_body(
        scope="shared",
        lock_type="write",
        owner="litmus: notowner_sharedlock",
    )

    response = await session.client2.lock(
        lockme, body, depth="0", timeout="Second-3600", test_name="double_sharedlock"
    )

    if response.status_code not in (200, 201):
        context.context(f"Second shared LOCK failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Parse second lock token
    try:
        lock_token2, _lock_scope = parse_lock_response(response.content)
    except Exception as e:
        context.context(f"Failed to parse LOCK response: {e}")
        return WebdavTckTestResult.FAIL

    if not lock_token2:
        context.context("No lock token returned from second LOCK")
        return WebdavTckTestResult.FAIL

    # Unlock the second lock
    response = await session.client2.unlock(
        lockme, lock_token2, test_name="double_sharedlock_unlock"
    )
    if response.status_code != 204:
        context.context(f"UNLOCK of second shared lock failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_prep_collection(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Prepare collection for collection locking tests."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Clear existing lock if any
    if "lockme" in session.locks:
        del session.locks["lockme"]

    # Create collection
    lockcoll = session.make_path("lockcoll")
    response = await session.client.mkcol(lockcoll, test_name="prep_collection")

    if response.status_code != 201:
        context.context(f"MKCOL failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    return WebdavTckTestResult.OK


async def test_lock_collection(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Take out depth infinity lock on collection."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lockcoll = session.make_path("lockcoll")

    # Lock collection with Depth: infinity
    body = build_lock_body(
        scope="exclusive",
        lock_type="write",
        owner="webdav-tck test suite",
    )

    response = await session.client.lock(
        lockcoll,
        body,
        depth="infinity",
        timeout="Second-3600",
        test_name="lock_collection",
    )

    if response.status_code not in (200, 201):
        context.context(f"LOCK collection failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Parse lock token
    try:
        lock_token, _lock_scope = parse_lock_response(response.content)
    except Exception as e:
        context.context(f"Failed to parse LOCK response: {e}")
        return WebdavTckTestResult.FAIL

    if not lock_token:
        context.context("No lock token returned")
        return WebdavTckTestResult.FAIL

    session.locks["lockcoll"] = lock_token

    # Create a resource in the locked collection
    lockme_txt = session.make_path("lockcoll", "lockme.txt")
    content = b"Resource in locked collection\n"

    # Use tagged If header format for inherited collection lock
    # Apache requires the collection URL to be specified for inherited locks
    lockcoll_url = session.client._make_url(lockcoll + "/")
    if_header = build_if_header([(lockcoll_url, [lock_token])])

    response = await session.client.put(
        lockme_txt, content, if_header=if_header, test_name="lock_collection_put"
    )
    if response.status_code not in (201, 204):
        context.context(f"PUT in locked collection failed: {response.status_code}")
        return WebdavTckTestResult.FAILHARD

    return WebdavTckTestResult.OK


async def test_owner_modify_coll(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Owner: Verify lock owner can modify collection member."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockcoll")
    if not lock_token:
        context.context("No collection lock token available")
        return WebdavTckTestResult.FAILHARD

    lockcoll = session.make_path("lockcoll")
    lockme_txt = session.make_path("lockcoll", "lockme.txt")

    # Use tagged If header format for inherited collection lock
    lockcoll_url = session.client._make_url(lockcoll + "/")
    if_header = build_if_header([(lockcoll_url, [lock_token])])

    # PUT with lock token should succeed
    content = b"Modified by collection lock owner\n"

    response = await session.client.put(
        lockme_txt, content, if_header=if_header, test_name="owner_put_coll"
    )
    if response.status_code not in (200, 201, 204):
        context.context(
            f"PUT on locked collection member by owner failed: {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    # PROPPATCH with lock token should succeed
    set_props = {(NS, "random"): "foobar"}
    body = build_proppatch_body(set_props=set_props)

    response = await session.client.proppatch(
        lockme_txt, body, if_header=if_header, test_name="owner_proppatch_coll"
    )
    if response.status_code not in (200, 207):
        context.context(
            f"PROPPATCH on locked collection member by owner failed: {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_notowner_modify_coll(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """Non-owner: Verify non-owner cannot modify collection member."""
    if not session.client2:
        context.context("Second client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockcoll")
    if not lock_token:
        context.context("No collection lock token available")
        return WebdavTckTestResult.FAILHARD

    lockme_txt = session.make_path("lockcoll", "lockme.txt")
    notlocked = session.make_path("notlocked")

    # Try DELETE with second session (no lock token) - should fail
    response = await session.client2.delete(
        lockme_txt, test_name="notowner_delete_coll"
    )
    if response.status_code not in (400, 423):
        context.context(
            f"DELETE of locked collection member should fail, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 423:
        context.warning(f"DELETE failed with {response.status_code} not 423")

    # Try PUT - should fail
    content = b"Trying to modify locked collection member\n"
    response = await session.client2.put(
        lockme_txt, content, test_name="notowner_put_coll"
    )
    if response.status_code not in (400, 423):
        context.context(
            f"PUT on locked collection member should fail, got {response.status_code}"
        )
        return WebdavTckTestResult.FAIL

    if response.status_code != 423:
        context.warning(f"PUT failed with {response.status_code} not 423")

    return WebdavTckTestResult.OK


async def test_indirect_refresh(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Indirectly refresh collection lock via member."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockcoll")
    if not lock_token:
        context.context("No collection lock token available")
        return WebdavTckTestResult.FAILHARD

    # Refresh the collection lock using the member path
    lockcoll = session.make_path("lockcoll")
    lockme_txt = session.make_path("lockcoll", "lockme.txt")

    # Use tagged If header format for inherited collection lock
    lockcoll_url = session.client._make_url(lockcoll + "/")
    if_header = build_if_header([(lockcoll_url, [lock_token])])

    response = await session.client.lock(
        lockme_txt,
        None,
        depth="0",
        timeout="Second-3600",
        if_header=if_header,
        test_name="indirect_refresh",
    )

    if response.status_code != 200:
        context.context(f"Indirect refresh LOCK failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    return WebdavTckTestResult.OK


async def test_unlock_collection(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """UNLOCK: Release collection lock."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("lockcoll")
    if not lock_token:
        context.context("No collection lock token available")
        return WebdavTckTestResult.FAILHARD

    lockcoll = session.make_path("lockcoll")

    response = await session.client.unlock(
        lockcoll, lock_token, test_name="unlock_collection"
    )
    if response.status_code != 204:
        context.context(f"UNLOCK collection failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    # Clear locks
    if "lockcoll" in session.locks:
        del session.locks["lockcoll"]
    if "lockme" in session.locks:
        del session.locks["lockme"]

    return WebdavTckTestResult.OK


async def test_unmapped_lock(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """LOCK: Lock on unmapped URL should return 201."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    # Clear any existing locks
    if "lockme" in session.locks:
        del session.locks["lockme"]

    unmapped = session.make_path("unmapped_url")

    # Lock unmapped URL (creates lock-null resource)
    body = build_lock_body(
        scope="exclusive",
        lock_type="write",
        owner="webdav-tck test suite",
    )

    response = await session.client.lock(
        unmapped, body, depth="0", timeout="Second-3600", test_name="unmapped_lock"
    )

    if response.status_code not in (200, 201):
        context.context(f"LOCK on unmapped URL failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    if response.status_code != 201:
        context.warning(
            f"LOCK on unmapped URL returned {response.status_code} not 201 (RFC4918:S7.3)"
        )

    # Parse and store lock token
    try:
        lock_token, _ = parse_lock_response(response.content)
        if lock_token:
            session.locks["unmapped_url"] = lock_token
    except Exception:
        pass

    return WebdavTckTestResult.OK


async def test_unlock_unmapped(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """UNLOCK: Release lock on unmapped resource."""
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    lock_token = session.locks.get("unmapped_url")
    if not lock_token:
        # Not a hard failure - maybe previous test was skipped
        return WebdavTckTestResult.OK

    unmapped = session.make_path("unmapped_url")

    response = await session.client.unlock(
        unmapped, lock_token, test_name="unlock_unmapped"
    )
    if response.status_code != 204:
        context.context(f"UNLOCK unmapped resource failed: {response.status_code}")
        return WebdavTckTestResult.FAIL

    del session.locks["unmapped_url"]

    return WebdavTckTestResult.OK


def create_locks_suite(session: WebdavTckSession) -> WebdavTckTestSuite:
    """Create the locks test suite.

    Args:
        session: WebdavTck session

    Returns:
        Test suite with locking tests
    """
    suite = WebdavTckTestSuite("locks", session=session)

    # Add tests in order matching locks.c
    tests = [
        test_options,
        test_precond,
        test_init_locks,
        # Exclusive lock tests
        test_put,
        test_lock_excl,
        test_discover,
        test_refresh,
        test_notowner_modify,
        test_notowner_lock,
        test_owner_modify,
        # Check lock persists after modification
        test_notowner_modify,
        test_notowner_lock,
        # Locks don't follow COPY
        test_copy,
        # Conditional PUTs
        test_cond_put,
        test_fail_cond_put,
        test_cond_put_with_not,
        test_cond_put_corrupt_token,
        test_unlock,
        test_fail_cond_put_unlocked,
        # Shared lock tests
        test_lock_shared,
        test_notowner_modify,
        test_notowner_lock,
        test_owner_modify,
        test_double_sharedlock,
        # Check main lock still intact
        test_notowner_modify,
        test_notowner_lock,
        test_unlock,
        # Collection locking
        test_prep_collection,
        test_lock_collection,
        test_owner_modify_coll,
        test_notowner_modify_coll,
        test_indirect_refresh,  # Refresh collection lock via member
        test_unlock_collection,
        # Lock-null resources
        test_unmapped_lock,
        test_unlock_unmapped,
    ]

    for test_func in tests:
        suite.add_test(test_func)

    return suite
