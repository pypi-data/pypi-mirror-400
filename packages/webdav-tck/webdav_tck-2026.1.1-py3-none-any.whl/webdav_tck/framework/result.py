"""Test result types and classes."""

from __future__ import annotations

from enum import IntEnum


class WebdavTckTestResult(IntEnum):
    """Test result status codes.

    Maps to the original C litmus result codes:
    - OK: Test passed
    - FAIL: Test failed
    - FAILHARD: Test failed, skip remaining tests in suite
    - SKIP: Test skipped (precondition not met)
    - SKIPREST: Skipped, and skip all remaining tests in suite
    """

    OK = 0
    FAIL = 1
    FAILHARD = 2
    SKIP = 3
    SKIPREST = 4

    def is_failure(self) -> bool:
        """Return True if this result represents a failure."""
        return self in (WebdavTckTestResult.FAIL, WebdavTckTestResult.FAILHARD)

    def is_skip(self) -> bool:
        """Return True if this result represents a skip."""
        return self in (WebdavTckTestResult.SKIP, WebdavTckTestResult.SKIPREST)

    def should_stop_suite(self) -> bool:
        """Return True if this result should stop the test suite."""
        return self in (WebdavTckTestResult.FAILHARD, WebdavTckTestResult.SKIPREST)


class TestResultInfo:
    """Information about a test result."""

    def __init__(
        self,
        name: str,
        result: WebdavTckTestResult,
        message: str | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.name = name
        self.result = result
        self.message = message
        self.warnings = warnings or []

    def __repr__(self) -> str:
        return f"TestResultInfo(name={self.name!r}, result={self.result.name})"
