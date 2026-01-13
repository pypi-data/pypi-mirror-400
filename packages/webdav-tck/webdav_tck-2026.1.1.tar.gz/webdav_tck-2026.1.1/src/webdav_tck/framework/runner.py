"""Test runner with colored output and reporting."""

from __future__ import annotations

import inspect
import sys
import time
from typing import TYPE_CHECKING, TextIO

from rich.console import Console
from rich.table import Table
from typing_extensions import Self

from webdav_tck.framework.result import TestResultInfo, WebdavTckTestResult
from webdav_tck.framework.suite import (
    WebdavTckContext,
    WebdavTckTestCase,
    WebdavTckTestSuite,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestRunner:
    """Runs test suites and reports results.

    Provides colored terminal output and debug logging.
    """

    def __init__(
        self,
        quiet: bool = False,
        use_color: bool | None = None,
        debug_log: Path | None = None,
    ) -> None:
        """Initialize test runner.

        Args:
            quiet: Use abbreviated output
            use_color: Force color output (None = auto-detect)
            debug_log: Path to debug log file
        """
        self.quiet = quiet
        self.console = Console(force_terminal=use_color, file=sys.stdout)
        self.debug_log = debug_log
        self.debug_file: TextIO | None = None

        # Result tracking
        self.results: list[TestResultInfo] = []
        self.current_suite: str | None = None

    def __enter__(self) -> Self:
        """Open debug log file if specified."""
        if self.debug_log:
            self.debug_file = self.debug_log.open("w", encoding="utf-8")
        return self

    def __exit__(self, *args: object) -> None:
        """Close debug log file."""
        if self.debug_file:
            self.debug_file.close()

    def log_debug(self, message: str) -> None:
        """Write message to debug log."""
        if self.debug_file:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.debug_file.write(f"[{timestamp}] {message}\n")
            self.debug_file.flush()

    async def run_suite(self, suite: WebdavTckTestSuite) -> list[TestResultInfo]:
        """Run a test suite and return results.

        Args:
            suite: The test suite to run

        Returns:
            List of test results
        """
        self.current_suite = suite.name
        suite_results: list[TestResultInfo] = []

        if not self.quiet:
            self.console.print(f"\n[bold cyan]Running {suite.name}[/bold cyan]")

        # Run setup
        try:
            suite.run_setup()
        except Exception as e:
            self.console.print(f"[bold red]Setup failed: {e}[/bold red]")
            return suite_results

        # Run tests
        context = WebdavTckContext()
        stop_suite = False

        for test in suite.tests:
            if stop_suite:
                result_info = TestResultInfo(
                    test.name, WebdavTckTestResult.SKIP, "Suite stopped"
                )
                suite_results.append(result_info)
                continue

            context.clear()
            result = await self._run_test(test, suite, context)

            result_info = TestResultInfo(
                test.name, result, context.error_message, context.warnings
            )
            suite_results.append(result_info)
            self.results.append(result_info)

            self._print_result(test.name, result_info)

            if result.should_stop_suite():
                stop_suite = True

        # Run teardown
        try:
            suite.run_teardown()
        except Exception as e:
            self.console.print(f"[bold red]Teardown failed: {e}[/bold red]")

        return suite_results

    async def _run_test(
        self,
        test: WebdavTckTestCase,
        suite: WebdavTckTestSuite,
        context: WebdavTckContext,
    ) -> WebdavTckTestResult:
        """Run a single test.

        Args:
            test: The test to run
            suite: The parent suite
            context: Test context for warnings/errors

        Returns:
            Test result
        """
        self.log_debug(f"Running test: {suite.name}.{test.name}")

        try:
            # Call test function with session if available
            if suite.session:
                call_result = test.func(suite.session, context)
            else:
                call_result = test.func(context)

            # Await if the result is a coroutine
            if inspect.iscoroutine(call_result):
                awaited_result = await call_result
            else:
                awaited_result = call_result

            # Convert int to WebdavTckTestResult
            if isinstance(awaited_result, int):
                result = WebdavTckTestResult(awaited_result)
            elif isinstance(awaited_result, WebdavTckTestResult):
                result = awaited_result
            else:
                result = WebdavTckTestResult.FAIL

            self.log_debug(f"Test {test.name} result: {result.name}")
            return result

        except Exception as e:
            self.log_debug(f"Test {test.name} exception: {e}")
            context.context(f"Exception: {e}")
            return WebdavTckTestResult.FAIL

    def _print_result(self, name: str, result: TestResultInfo) -> None:
        """Print test result to console.

        Args:
            name: Test name
            result: Test result info
        """
        if self.quiet:
            # Abbreviated output
            symbol = self._get_result_symbol(result.result)
            self.console.print(symbol, end="")
            return

        # Full output
        status_text = self._get_result_text(result.result)
        self.console.print(f"  {name}: {status_text}")

        # Print warnings
        for warning in result.warnings:
            self.console.print(f"    [yellow]Warning: {warning}[/yellow]")

        # Print error message
        if result.message:
            self.console.print(f"    [red]{result.message}[/red]")

    def _get_result_symbol(self, result: WebdavTckTestResult) -> str:
        """Get single-character symbol for result."""
        symbols = {
            WebdavTckTestResult.OK: "[green].[/green]",
            WebdavTckTestResult.FAIL: "[red]F[/red]",
            WebdavTckTestResult.FAILHARD: "[red]![/red]",
            WebdavTckTestResult.SKIP: "[yellow]s[/yellow]",
            WebdavTckTestResult.SKIPREST: "[yellow]S[/yellow]",
        }
        return symbols.get(result, "?")

    def _get_result_text(self, result: WebdavTckTestResult) -> str:
        """Get colored text for result."""
        texts = {
            WebdavTckTestResult.OK: "[green]PASS[/green]",
            WebdavTckTestResult.FAIL: "[red]FAIL[/red]",
            WebdavTckTestResult.FAILHARD: "[red]FAIL (hard)[/red]",
            WebdavTckTestResult.SKIP: "[yellow]SKIP[/yellow]",
            WebdavTckTestResult.SKIPREST: "[yellow]SKIP (rest)[/yellow]",
        }
        return texts.get(result, "[dim]UNKNOWN[/dim]")

    def print_summary(self) -> None:
        """Print summary of all test results."""
        if not self.results:
            return

        if self.quiet:
            self.console.print()  # Newline after dots

        # Count results
        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == WebdavTckTestResult.OK)
        failed = sum(1 for r in self.results if r.result.is_failure())
        skipped = sum(1 for r in self.results if r.result.is_skip())

        # Create summary table
        table = Table(title="\nTest Summary", show_header=True)
        table.add_column("Status", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Percentage", justify="right")

        table.add_row("Total", str(total), "100%")
        table.add_row(
            "Passed",
            str(passed),
            f"{passed * 100 // total}%" if total > 0 else "0%",
            style="green",
        )

        if failed > 0:
            table.add_row(
                "Failed",
                str(failed),
                f"{failed * 100 // total}%" if total > 0 else "0%",
                style="red",
            )

        if skipped > 0:
            table.add_row(
                "Skipped",
                str(skipped),
                f"{skipped * 100 // total}%" if total > 0 else "0%",
                style="yellow",
            )

        self.console.print(table)

        # Print failed tests details
        failed_tests = [r for r in self.results if r.result.is_failure()]
        if failed_tests and not self.quiet:
            self.console.print("\n[bold red]Failed Tests:[/bold red]")
            for result in failed_tests:
                self.console.print(f"  • {result.name}")
                if result.message:
                    self.console.print(f"    {result.message}")

    def get_exit_code(self) -> int:
        """Get exit code based on test results.

        Returns:
            0 if all tests passed, 1 otherwise
        """
        return 1 if any(r.result.is_failure() for r in self.results) else 0
