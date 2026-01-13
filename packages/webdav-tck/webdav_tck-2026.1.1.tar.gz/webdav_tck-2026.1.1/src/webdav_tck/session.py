"""Session management for WebDAV TCK tests."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

from typing_extensions import Self

from webdav_tck.client import WebDAVClient
from webdav_tck.xml_utils import extract_dav_header

if TYPE_CHECKING:
    from pathlib import Path


class WebdavTckSession:
    """Manages test session state.

    Corresponds to the global session state in the C implementation
    (i_session, i_session2, i_origin, etc.).
    """

    def __init__(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        verify_ssl: bool = True,
        proxy: str | None = None,
        client_cert: str | None = None,
        debug_log: Path | None = None,
    ) -> None:
        """Initialize TCK session.

        Args:
            url: Base URL for WebDAV server
            username: Optional username for authentication
            password: Optional password for authentication
            verify_ssl: Whether to verify SSL certificates
            proxy: Optional proxy URL
            client_cert: Optional path to client certificate
            debug_log: Optional path to debug log file
        """
        self.origin: ParseResult = urlparse(url)
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.proxy = proxy
        self.client_cert = client_cert
        self.debug_log = debug_log

        # WebDAV capabilities
        self.class2 = False  # WebDAV Class 2 (locking) support
        self.capabilities: dict[str, bool] = {}

        # Test collection path
        self.base_path = self.origin.path.rstrip("/") + "/webdav-tck"

        # Clients (primary and secondary for multi-user tests)
        self.client: WebDAVClient | None = None
        self.client2: WebDAVClient | None = None

        # State tracking
        self.locks: dict[str, str] = {}  # path -> lock token
        self.etags: dict[str, str] = {}  # path -> etag

    @property
    def hostname(self) -> str:
        """Get hostname from origin."""
        return self.origin.hostname or "localhost"

    @property
    def port(self) -> int:
        """Get port from origin."""
        return self.origin.port or (443 if self.origin.scheme == "https" else 80)

    @property
    def base_url(self) -> str:
        """Get base URL for the server."""
        return f"{self.origin.scheme}://{self.origin.netloc}"

    async def __aenter__(self) -> Self:
        """Async context manager entry - create clients."""
        await self.begin()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit - close clients."""
        await self.finish()

    async def begin(self) -> None:
        """Initialize session and create WebDAV clients.

        Creates primary and secondary clients for testing.
        """
        # Create primary client
        self.client = WebDAVClient(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
            verify_ssl=self.verify_ssl,
            proxy=self.proxy,
            client_cert=self.client_cert,
            tck_header="X-WebdavTck",
        )
        # Manually enter context for lifecycle management
        self.client = await self.client.__aenter__()  # noqa: PLC2801

        # Create secondary client for multi-user tests (locks)
        self.client2 = WebDAVClient(
            base_url=self.base_url,
            username=self.username,
            password=self.password,
            verify_ssl=self.verify_ssl,
            proxy=self.proxy,
            client_cert=self.client_cert,
            tck_header="X-WebdavTck-Second",
        )
        # Manually enter context for lifecycle management
        self.client2 = await self.client2.__aenter__()  # noqa: PLC2801

    async def finish(self) -> None:
        """Clean up session and close clients."""
        if self.client:
            await self.client.close()
        if self.client2:
            await self.client2.close()

    async def discover_capabilities(self) -> None:
        """Discover WebDAV server capabilities via OPTIONS.

        Sets self.class2 and self.capabilities based on DAV header.
        """
        if not self.client:
            msg = "Session not initialized - call begin() first"
            raise RuntimeError(msg)

        response = await self.client.options(self.base_path, test_name="options")

        # Parse DAV header
        dav_header = response.headers.get("DAV", "")
        if dav_header:
            self.capabilities = extract_dav_header(dav_header)
            # WebDAV Class 2 means locking support
            self.class2 = "2" in self.capabilities

    async def create_test_collection(self) -> None:
        """Create the TCK test collection.

        Creates the base collection where all test resources will be created.
        """
        if not self.client:
            msg = "Session not initialized - call begin() first"
            raise RuntimeError(msg)

        # Delete if exists (cleanup from previous run)
        with contextlib.suppress(Exception):
            await self.client.delete(self.base_path, test_name="cleanup")

        # Create fresh collection
        response = await self.client.mkcol(self.base_path, test_name="setup")
        if response.status_code not in (201, 405):  # 405 = already exists
            msg = f"Failed to create test collection: {response.status_code}"
            raise RuntimeError(msg)

    async def cleanup_test_collection(self) -> None:
        """Remove the TCK test collection.

        Cleans up all test resources created during the test run.
        """
        if not self.client:
            return

        with contextlib.suppress(Exception):
            await self.client.delete(self.base_path, test_name="cleanup")

    def store_lock(self, path: str, token: str) -> None:
        """Store a lock token for a resource.

        Args:
            path: Resource path
            token: Lock token
        """
        self.locks[path] = token

    def get_lock(self, path: str) -> str | None:
        """Get stored lock token for a resource.

        Args:
            path: Resource path

        Returns:
            Lock token or None if not locked
        """
        return self.locks.get(path)

    def remove_lock(self, path: str) -> None:
        """Remove stored lock token.

        Args:
            path: Resource path
        """
        self.locks.pop(path, None)

    def store_etag(self, path: str, etag: str) -> None:
        """Store ETag for a resource.

        Args:
            path: Resource path
            etag: ETag value
        """
        self.etags[path] = etag

    def get_etag(self, path: str) -> str | None:
        """Get stored ETag for a resource.

        Args:
            path: Resource path

        Returns:
            ETag or None if not stored
        """
        return self.etags.get(path)

    def make_path(self, *parts: str) -> str:
        """Make a path within the test collection.

        Args:
            *parts: Path components

        Returns:
            Full path relative to base
        """
        return "/".join([self.base_path] + list(parts))
