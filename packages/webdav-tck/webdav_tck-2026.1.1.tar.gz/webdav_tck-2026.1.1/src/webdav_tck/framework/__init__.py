"""Test framework for WebDAV TCK."""

from __future__ import annotations

from webdav_tck.framework.result import WebdavTckTestResult
from webdav_tck.framework.runner import TestRunner
from webdav_tck.framework.suite import (
    WebdavTckContext,
    WebdavTckTestCase,
    WebdavTckTestSuite,
)

# For backwards compatibility, export as TestResult too
TestResult = WebdavTckTestResult

__all__ = [
    "TestResult",
    "TestRunner",
    "WebdavTckContext",
    "WebdavTckTestCase",
    "WebdavTckTestResult",
    "WebdavTckTestSuite",
]
