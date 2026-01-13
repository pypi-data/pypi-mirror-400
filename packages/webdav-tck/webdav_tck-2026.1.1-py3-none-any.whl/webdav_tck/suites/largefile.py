"""Large file support test suite.

Ports src/largefile.c from the original litmus C implementation.
Tests handling of files larger than 2GB to verify 64-bit offset support.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from webdav_tck.framework import (
    WebdavTckContext,
    WebdavTckTestResult,
    WebdavTckTestSuite,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from webdav_tck.session import WebdavTckSession

# Constants matching the C implementation
BLOCKSIZE = 8192
NUMBLOCKS = 262152  # Results in ~2GB file (2,147,491,840 bytes)
TOTALSIZE = BLOCKSIZE * NUMBLOCKS

# For testing purposes, we can use a smaller file
# Set this environment variable to use a smaller test size
TEST_MODE = os.environ.get("WEBDAV_TCK_TEST_MODE", "0") == "1"
if TEST_MODE:
    NUMBLOCKS = 1024  # ~8MB for testing
    TOTALSIZE = BLOCKSIZE * NUMBLOCKS


def generate_block() -> bytes:
    """Generate the repeating 8KB block pattern.

    Creates a block where each byte is the value (position % 256).
    This allows verification that data was not corrupted during transfer.

    Returns:
        8KB block of patterned data
    """
    return bytes(n % 256 for n in range(BLOCKSIZE))


async def block_generator(  # noqa: RUF029
    block: bytes, num_blocks: int
) -> AsyncIterator[bytes]:
    """Async generator that yields blocks for streaming upload.

    Note: Must be async for httpx AsyncClient streaming compatibility,
    even though no await is used internally.

    Args:
        block: The block pattern to repeat
        num_blocks: Number of blocks to yield

    Yields:
        8KB blocks of data
    """
    for _ in range(num_blocks):
        yield block


async def test_large_put(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """PUT: Upload a file larger than 2GB.

    Tests that the server can handle PUT requests for files exceeding 2GB,
    which requires proper 64-bit offset handling. The file is streamed in
    8KB blocks to avoid loading the entire file into memory.
    """
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("large.txt")

    # Generate the repeating block pattern
    block = generate_block()

    # Stream the large file using a generator
    # This avoids loading 2GB into memory
    try:
        response = await session.client.put(
            path,
            block_generator(block, NUMBLOCKS),
            test_name="large_put",
        )

        # Accept 201 (Created) or 204 (No Content)
        if response.status_code not in (201, 204):
            context.context(
                f"large PUT returned {response.status_code}, expected 201 or 204"
            )
            return WebdavTckTestResult.FAIL

        return WebdavTckTestResult.OK

    except Exception as e:
        context.context(f"large PUT failed: {e}")
        return WebdavTckTestResult.FAIL


async def test_large_get(
    session: WebdavTckSession, context: WebdavTckContext
) -> WebdavTckTestResult:
    """GET: Download and verify a file larger than 2GB.

    Tests that the server can handle GET requests for files exceeding 2GB.
    Downloads the file in chunks and verifies that each chunk matches the
    expected pattern, ensuring data integrity across the 2GB boundary.
    """
    if not session.client:
        context.context("Client not initialized")
        return WebdavTckTestResult.FAILHARD

    path = session.make_path("large.txt")

    # Generate the expected pattern
    # We create a 16KB buffer (2 blocks) to handle offset wraparound
    block = generate_block()
    origin = block + block  # Double block for sliding window verification

    try:
        response = await session.client.get(path, test_name="large_get")

        if response.status_code != 200:
            context.context(f"large GET returned {response.status_code}, expected 200")
            return WebdavTckTestResult.FAIL

        # Stream the response and verify content
        # We verify each chunk matches the expected pattern
        offset = 0
        progress = 0
        chunk_size = BLOCKSIZE

        # For httpx, we need to stream the response
        # Since we already have response.content, let's verify it in chunks
        content = response.content
        total_size = len(content)

        # Verify we got the expected size
        if total_size != TOTALSIZE:
            context.context(
                f"large GET returned {total_size} bytes, expected {TOTALSIZE}"
            )
            return WebdavTckTestResult.FAIL

        # Verify content in chunks
        pos = 0
        while pos < total_size:
            chunk_len = min(chunk_size, total_size - pos)
            chunk = content[pos : pos + chunk_len]

            # Verify this chunk matches the pattern
            expected = origin[offset : offset + chunk_len]
            if chunk != expected:
                context.context(f"byte mismatch at offset {progress}")
                return WebdavTckTestResult.FAIL

            offset = (offset + chunk_len) % BLOCKSIZE
            progress += chunk_len
            pos += chunk_len

        return WebdavTckTestResult.OK

    except Exception as e:
        context.context(f"large GET failed: {e}")
        return WebdavTckTestResult.FAIL


def create_largefile_suite(session: WebdavTckSession) -> WebdavTckTestSuite:
    """Create the large file support test suite.

    Args:
        session: WebdavTck session

    Returns:
        Test suite with large file tests
    """
    suite = WebdavTckTestSuite("largefile", session=session)

    # Add tests
    suite.add_test(test_large_put)
    suite.add_test(test_large_get)

    return suite
