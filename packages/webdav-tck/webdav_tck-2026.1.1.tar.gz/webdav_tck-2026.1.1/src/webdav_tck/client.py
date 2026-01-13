"""WebDAV client wrapper around httpx."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import httpx
from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, Iterable
    from types import TracebackType


class WebDAVResponse:
    """Wrapper for HTTP responses with WebDAV-specific helpers."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        """Get HTTP status code."""
        return self._response.status_code

    @property
    def headers(self) -> httpx.Headers:
        """Get response headers."""
        return self._response.headers

    @property
    def content(self) -> bytes:
        """Get response body as bytes."""
        return self._response.content

    @property
    def text(self) -> str:
        """Get response body as text."""
        return self._response.text

    def raise_for_status(self) -> None:
        """Raise exception for 4xx/5xx status codes."""
        self._response.raise_for_status()

    def __repr__(self) -> str:
        return f"WebDAVResponse(status={self.status_code})"


class WebDAVClient:
    """WebDAV-aware HTTP client.

    Wraps httpx.AsyncClient with WebDAV-specific methods and headers.
    """

    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        verify_ssl: bool = True,
        proxy: str | None = None,
        client_cert: str | None = None,
        tck_header: str = "X-WebdavTck",
        timeout: float = 30.0,
    ) -> None:
        """Initialize WebDAV client.

        Args:
            base_url: Base URL for WebDAV server
            username: Optional username for authentication
            password: Optional password for authentication
            verify_ssl: Whether to verify SSL certificates
            proxy: Optional proxy URL
            client_cert: Optional path to client certificate
            tck_header: Header name for test identification
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.tck_header = tck_header

        # Build auth
        auth = None
        if username and password:
            auth = httpx.BasicAuth(username, password)

        # Build client config
        client_kwargs: dict[str, Any] = {
            "auth": auth,
            "verify": verify_ssl,
            "timeout": timeout,
            "follow_redirects": True,  # Follow 301/302 redirects (e.g., Apache collection redirects)
        }

        if proxy:
            client_kwargs["proxies"] = proxy

        if client_cert:
            client_kwargs["cert"] = client_cert

        self._client = httpx.AsyncClient(**client_kwargs)
        self._test_counter = 0

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self._client.__aexit__(exc_type, exc_value, traceback)

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.aclose()

    def _make_url(self, path: str) -> str:
        """Make full URL from path.

        Args:
            path: Path relative to base URL

        Returns:
            Full URL
        """
        if path.startswith(("http://", "https://")):
            return path
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _make_headers(self, test_name: str = "", **extra: str) -> dict[str, str]:
        """Make request headers with TCK identification.

        Args:
            test_name: Name of the test being run
            **extra: Additional headers

        Returns:
            Dictionary of headers
        """
        headers = {self.tck_header: test_name or f"test-{self._test_counter}"}
        headers.update(extra)
        self._test_counter += 1
        return headers

    async def request(
        self,
        method: str,
        path: str,
        test_name: str = "",
        headers: dict[str, str] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> WebDAVResponse:
        """Make an HTTP request.

        Args:
            method: HTTP method
            path: Path or full URL
            test_name: Name of test for header
            headers: Optional additional headers
            **kwargs: Additional arguments for httpx

        Returns:
            WebDAV response wrapper
        """
        url = self._make_url(path)
        req_headers = self._make_headers(test_name, **(headers or {}))

        response = await self._client.request(
            method, url, headers=req_headers, **kwargs
        )
        return WebDAVResponse(response)

    async def options(self, path: str, test_name: str = "") -> WebDAVResponse:
        """Send OPTIONS request.

        Args:
            path: Path to query
            test_name: Name of test

        Returns:
            Response with Allow and DAV headers
        """
        return await self.request("OPTIONS", path, test_name=test_name)

    async def get(
        self, path: str, test_name: str = "", headers: dict[str, str] | None = None
    ) -> WebDAVResponse:
        """Send GET request.

        Args:
            path: Path to resource
            test_name: Name of test
            headers: Optional additional headers

        Returns:
            Response with resource content
        """
        return await self.request("GET", path, test_name=test_name, headers=headers)

    async def put(
        self,
        path: str,
        content: bytes | Iterable[bytes] | AsyncIterable[bytes],
        test_name: str = "",
        headers: dict[str, str] | None = None,
        if_header: str | None = None,
    ) -> WebDAVResponse:
        """Send PUT request to create/update resource.

        Args:
            path: Path to resource
            content: Content to upload (bytes, iterable, or async iterable for streaming)
            test_name: Name of test
            headers: Optional additional headers
            if_header: Optional If: header for conditional requests

        Returns:
            Response (typically 201 Created or 204 No Content)
        """
        all_headers = headers.copy() if headers else {}
        if if_header:
            all_headers["If"] = if_header
        return await self.request(
            "PUT", path, test_name=test_name, headers=all_headers, content=content
        )

    async def delete(self, path: str, test_name: str = "") -> WebDAVResponse:
        """Send DELETE request.

        Args:
            path: Path to resource
            test_name: Name of test

        Returns:
            Response (typically 204 No Content)
        """
        return await self.request("DELETE", path, test_name=test_name)

    async def mkcol(
        self, path: str, test_name: str = "", body: bytes | None = None
    ) -> WebDAVResponse:
        """Send MKCOL request to create a collection.

        Args:
            path: Path to new collection
            test_name: Name of test
            body: Optional request body (should typically be empty)

        Returns:
            Response (typically 201 Created)
        """
        return await self.request("MKCOL", path, test_name=test_name, content=body)

    async def copy(
        self,
        src: str,
        dest: str,
        overwrite: bool = True,
        depth: str = "infinity",
        test_name: str = "",
    ) -> WebDAVResponse:
        """Send COPY request.

        Args:
            src: Source path
            dest: Destination path (can be absolute or relative URL)
            overwrite: Whether to overwrite existing resource
            depth: Depth header value (0, 1, infinity)
            test_name: Name of test

        Returns:
            Response (typically 201 Created or 204 No Content)
        """
        headers = {
            "Destination": self._make_url(dest)
            if not dest.startswith("http")
            else dest,
            "Overwrite": "T" if overwrite else "F",
            "Depth": depth,
        }
        return await self.request("COPY", src, test_name=test_name, headers=headers)

    async def move(
        self,
        src: str,
        dest: str,
        overwrite: bool = True,
        test_name: str = "",
    ) -> WebDAVResponse:
        """Send MOVE request.

        Args:
            src: Source path
            dest: Destination path (can be absolute or relative URL)
            overwrite: Whether to overwrite existing resource
            test_name: Name of test

        Returns:
            Response (typically 201 Created or 204 No Content)
        """
        headers = {
            "Destination": self._make_url(dest)
            if not dest.startswith("http")
            else dest,
            "Overwrite": "T" if overwrite else "F",
        }
        return await self.request("MOVE", src, test_name=test_name, headers=headers)

    async def propfind(
        self,
        path: str,
        depth: int = 0,
        body: bytes | None = None,
        test_name: str = "",
    ) -> WebDAVResponse:
        """Send PROPFIND request.

        Args:
            path: Path to resource
            depth: Depth header value (0, 1, infinity)
            body: XML body with property names
            test_name: Name of test

        Returns:
            Response with multistatus XML
        """
        headers = {"Depth": str(depth)}
        return await self.request(
            "PROPFIND", path, test_name=test_name, headers=headers, content=body or b""
        )

    async def proppatch(
        self,
        path: str,
        body: bytes,
        test_name: str = "",
        if_header: str | None = None,
    ) -> WebDAVResponse:
        """Send PROPPATCH request.

        Args:
            path: Path to resource
            body: XML body with property updates
            test_name: Name of test
            if_header: Optional If: header for conditional requests

        Returns:
            Response with multistatus XML
        """
        headers = {"If": if_header} if if_header else None
        return await self.request(
            "PROPPATCH", path, test_name=test_name, headers=headers, content=body
        )

    async def lock(
        self,
        path: str,
        body: bytes | None,
        timeout: str = "Second-3600",
        depth: str = "0",
        if_header: str | None = None,
        test_name: str = "",
    ) -> WebDAVResponse:
        """Send LOCK request.

        Args:
            path: Path to resource
            body: XML body with lock info (None for lock refresh)
            timeout: Timeout header value
            depth: Depth header value
            if_header: Optional If header for lock refresh
            test_name: Name of test

        Returns:
            Response with lock token
        """
        headers = {"Timeout": timeout, "Depth": depth}
        if if_header:
            headers["If"] = if_header

        return await self.request(
            "LOCK", path, test_name=test_name, headers=headers, content=body
        )

    async def unlock(
        self,
        path: str,
        lock_token: str,
        test_name: str = "",
    ) -> WebDAVResponse:
        """Send UNLOCK request.

        Args:
            path: Path to resource
            lock_token: Lock token to release
            test_name: Name of test

        Returns:
            Response (typically 204 No Content)
        """
        headers = {"Lock-Token": f"<{lock_token}>"}
        return await self.request("UNLOCK", path, test_name=test_name, headers=headers)
