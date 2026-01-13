"""Test suite and test case classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from webdav_tck.framework.result import WebdavTckTestResult
    from webdav_tck.session import WebdavTckSession


class WebdavTckContext:
    """Context for a test execution.

    Collects warnings and error messages during test execution.
    """

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.error_message: str | None = None

    def warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def context(self, message: str) -> None:
        """Set error context message."""
        self.error_message = message

    def clear(self) -> None:
        """Clear all messages."""
        self.warnings.clear()
        self.error_message = None


class WebdavTckTestCase:
    """A single test case.

    Wraps a test function with metadata.
    """

    def __init__(
        self,
        func: Callable[..., Awaitable[WebdavTckTestResult] | WebdavTckTestResult | int],
        name: str | None = None,
        check_leaks: bool = False,
    ) -> None:
        self.func = func
        self.name = name or getattr(func, "__name__", "unknown")
        self.check_leaks = check_leaks
        self._doc = getattr(func, "__doc__", None)

    def __repr__(self) -> str:
        return f"TestCase({self.name!r})"

    @property
    def description(self) -> str | None:
        """Get test description from docstring."""
        return self._doc.strip() if self._doc else None


class WebdavTckTestSuite:
    """A collection of related test cases.

    Maps to a test suite module in the original C implementation
    (e.g., basic, copymove, props, locks).
    """

    def __init__(self, name: str, session: WebdavTckSession | None = None) -> None:
        self.name = name
        self.session = session
        self.tests: list[WebdavTckTestCase] = []
        self._setup: Callable[[], None] | None = None
        self._teardown: Callable[[], None] | None = None

    def add_test(
        self,
        func: Callable[..., Awaitable[WebdavTckTestResult] | WebdavTckTestResult | int],
        name: str | None = None,
        check_leaks: bool = False,
    ) -> None:
        """Add a test to this suite."""
        self.tests.append(WebdavTckTestCase(func, name, check_leaks))

    def setup(self, func: Callable[[], None]) -> Callable[[], None]:
        """Decorator to register a setup function."""
        self._setup = func
        return func

    def teardown(self, func: Callable[[], None]) -> Callable[[], None]:
        """Decorator to register a teardown function."""
        self._teardown = func
        return func

    def run_setup(self) -> None:
        """Run setup function if defined."""
        if self._setup:
            self._setup()

    def run_teardown(self) -> None:
        """Run teardown function if defined."""
        if self._teardown:
            self._teardown()

    def __repr__(self) -> str:
        return f"TestSuite({self.name!r}, {len(self.tests)} tests)"
