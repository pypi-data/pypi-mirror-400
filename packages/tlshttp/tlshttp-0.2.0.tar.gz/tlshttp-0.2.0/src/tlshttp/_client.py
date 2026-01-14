"""Client and AsyncClient implementations."""

from __future__ import annotations

import base64
import functools
import json
import logging
import time
from datetime import timedelta
from typing import Any, Callable
from urllib.parse import urljoin

import anyio

from ._cookies import Cookies, merge_cookies
from ._exceptions import (
    ConnectError,
    RequestError,
    TimeoutError,
    TLSError,
)
from ._headers import Headers, merge_headers
from ._internal._library import get_library
from ._internal._protocol import build_request_payload, parse_response
from ._internal._session import SessionManager
from ._request import Request
from ._response import Response
from ._types import ContentType, HttpMethod, ProxyConfig, Timeout
from .profiles import Profile, get_profile

logger = logging.getLogger(__name__)


class Client:
    """Synchronous HTTP client with TLS fingerprinting.

    This client provides an httpx-like API for making HTTP requests
    with browser TLS fingerprinting to bypass anti-bot detection.

    Example:
        >>> with tlshttp.Client(profile="chrome_120") as client:
        ...     response = client.get("https://httpbin.org/json")
        ...     print(response.json())

    Args:
        profile: Browser profile for TLS fingerprinting (default: chrome_120).
        timeout: Request timeout in seconds or Timeout object.
        follow_redirects: Whether to follow redirects.
        max_redirects: Maximum number of redirects to follow.
        proxy: Proxy URL or ProxyConfig.
        verify: Whether to verify SSL certificates.
        http2: Whether to use HTTP/2.
        headers: Default headers for all requests.
        cookies: Default cookies for all requests.
        base_url: Base URL for relative URLs.
    """

    def __init__(
        self,
        *,
        profile: str | Profile | None = "chrome_120",
        timeout: float | Timeout | None = 30.0,
        follow_redirects: bool = True,
        max_redirects: int = 10,
        proxy: str | ProxyConfig | None = None,
        verify: bool = True,
        http2: bool = True,
        http3: bool = False,
        random_tls_extension_order: bool = True,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        base_url: str | None = None,
    ) -> None:
        # Store configuration
        self._profile = get_profile(profile)
        self._timeout = Timeout(timeout) if not isinstance(timeout, Timeout) else timeout
        self._follow_redirects = follow_redirects
        self._max_redirects = max_redirects
        self._verify = verify
        self._http2 = http2
        self._http3 = http3
        self._random_tls_extension_order = random_tls_extension_order
        self._base_url = base_url

        # Handle proxy
        if isinstance(proxy, ProxyConfig):
            self._proxy = proxy.to_url()
        else:
            self._proxy = proxy

        # Initialize headers and cookies
        self._headers = Headers(headers) if headers else Headers()
        self._cookies = Cookies(cookies) if isinstance(cookies, dict) else (cookies or Cookies())

        # Create session
        self._session_id = SessionManager.create_session()
        SessionManager.register_client(self, self._session_id)

        # Get library reference (downloads if needed)
        self._library = get_library()

        self._closed = False
        logger.debug(f"Created client with session: {self._session_id}")

    @property
    def headers(self) -> Headers:
        """Default headers for all requests."""
        return self._headers

    @property
    def cookies(self) -> Cookies:
        """Cookie jar for this client."""
        return self._cookies

    @property
    def is_closed(self) -> bool:
        """Whether the client has been closed."""
        return self._closed

    def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send an HTTP request.

        Args:
            method: HTTP method.
            url: Request URL.
            content: Raw request body.
            data: Form data (will be URL-encoded).
            json: JSON request body.
            params: URL query parameters.
            headers: Request headers (merged with defaults).
            cookies: Request cookies (merged with defaults).
            auth: Basic auth credentials as (username, password) tuple.
            timeout: Request timeout (overrides default).
            follow_redirects: Whether to follow redirects (overrides default).

        Returns:
            Response object.

        Raises:
            RequestError: If request fails.
            TimeoutError: If request times out.
            ConnectError: If connection fails.
        """
        if self._closed:
            raise RequestError("Client is closed")

        # Build full URL
        if self._base_url and not url.startswith(("http://", "https://")):
            url = urljoin(self._base_url, url)

        # Merge headers
        request_headers = merge_headers(self._headers, headers)

        # Add Basic auth header if provided
        if auth is not None:
            username, password = auth
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            request_headers["Authorization"] = f"Basic {credentials}"

        # Merge cookies
        request_cookies = merge_cookies(self._cookies, cookies)

        # Prepare content
        request_content: bytes | None = None
        json_data: Any | None = None

        if content is not None:
            request_content = content
        elif data is not None:
            # URL-encode form data
            from urllib.parse import urlencode
            request_content = urlencode(data).encode("utf-8")
            if "content-type" not in {k.lower() for k in request_headers}:
                request_headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif json is not None:
            json_data = json

        # Build Request object
        request = Request(
            method=method,
            url=url,
            headers=request_headers,
            content=request_content,
            params=params,
        )

        # Build payload
        payload = build_request_payload(
            session_id=self._session_id,
            method=method,
            url=request.url,
            headers=request_headers.to_dict(),
            content=request_content,
            json_data=json_data,
            cookies=request_cookies.to_request_format() if request_cookies else None,
            timeout=timeout if isinstance(timeout, Timeout) else (
                Timeout(timeout) if timeout else self._timeout
            ),
            follow_redirects=follow_redirects if follow_redirects is not None else self._follow_redirects,
            proxy=self._proxy,
            verify=self._verify,
            http2=self._http2,
            profile=self._profile,
            random_tls_extension_order=self._random_tls_extension_order,
        )

        # Execute request
        start_time = time.monotonic()
        response_data = self._library.request(payload)
        elapsed = timedelta(seconds=time.monotonic() - start_time)

        # Parse response with guaranteed memory cleanup
        response_id = response_data.get("id", "")

        with SessionManager.response_memory(self._session_id, response_id):
            parsed = parse_response(response_data)

            # Check for errors
            if "error" in parsed:
                error_msg = parsed["error"]
                if "timeout" in error_msg.lower():
                    raise TimeoutError(error_msg, request)
                elif any(x in error_msg.lower() for x in ["connection", "dial", "connect"]):
                    raise ConnectError(error_msg, request)
                elif "tls" in error_msg.lower() or "ssl" in error_msg.lower():
                    raise TLSError(error_msg, request)
                else:
                    raise RequestError(error_msg, request)

            # Build response
            response_headers = Headers.from_go_response(parsed["headers"])
            response_cookies = Cookies()
            if parsed.get("cookies"):
                response_cookies.update_from_response(parsed["cookies"], url)

            # Update client cookies from response
            if parsed.get("cookies"):
                self._cookies.update_from_response(parsed["cookies"], url)

            response = Response(
                status_code=parsed["status_code"],
                headers=response_headers,
                content=parsed["content"],
                url=parsed["url"] or url,
                request=request,
                cookies=response_cookies,
                http_version=parsed["http_version"],
                elapsed=elapsed,
            )

        logger.debug(f"{method} {url} -> {response.status_code}")
        return response

    def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a GET request."""
        return self.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def post(
        self,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a POST request."""
        return self.request(
            "POST",
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def put(
        self,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a PUT request."""
        return self.request(
            "PUT",
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def patch(
        self,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a PATCH request."""
        return self.request(
            "PATCH",
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def delete(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a DELETE request."""
        return self.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def head(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a HEAD request."""
        return self.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def options(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send an OPTIONS request."""
        return self.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    def close(self) -> None:
        """Close the client and release resources."""
        if self._closed:
            return

        self._closed = True
        SessionManager.destroy_session(self._session_id)
        logger.debug(f"Closed client with session: {self._session_id}")

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __del__(self) -> None:
        # Weak reference finalizer handles cleanup, but be explicit
        if not self._closed:
            try:
                self.close()
            except Exception:
                pass

    def __repr__(self) -> str:
        return f"<Client [{self._profile or 'custom'}]>"


class AsyncClient:
    """Asynchronous HTTP client with TLS fingerprinting.

    This client provides an httpx-like async API for making HTTP requests
    with browser TLS fingerprinting. It uses a thread pool internally
    since the underlying Go library is synchronous.

    Example:
        >>> async with tlshttp.AsyncClient(profile="chrome_120") as client:
        ...     response = await client.get("https://httpbin.org/json")
        ...     print(response.json())

    All constructor arguments are the same as Client.
    """

    def __init__(
        self,
        *,
        profile: str | Profile | None = "chrome_120",
        timeout: float | Timeout | None = 30.0,
        follow_redirects: bool = True,
        max_redirects: int = 10,
        proxy: str | ProxyConfig | None = None,
        verify: bool = True,
        http2: bool = True,
        http3: bool = False,
        random_tls_extension_order: bool = True,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        base_url: str | None = None,
        max_concurrent: int = 10,
    ) -> None:
        # Create sync client internally
        self._sync_client = Client(
            profile=profile,
            timeout=timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            proxy=proxy,
            verify=verify,
            http2=http2,
            http3=http3,
            random_tls_extension_order=random_tls_extension_order,
            headers=headers,
            cookies=cookies,
            base_url=base_url,
        )

        # Limit concurrent requests to avoid overwhelming the thread pool
        self._limiter = anyio.CapacityLimiter(max_concurrent)

    @property
    def headers(self) -> Headers:
        """Default headers for all requests."""
        return self._sync_client.headers

    @property
    def cookies(self) -> Cookies:
        """Cookie jar for this client."""
        return self._sync_client.cookies

    @property
    def is_closed(self) -> bool:
        """Whether the client has been closed."""
        return self._sync_client.is_closed

    async def _run_sync(
        self,
        func: Callable[..., Response],
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Run a sync function in a thread pool."""
        return await anyio.to_thread.run_sync(
            functools.partial(func, *args, **kwargs),
            limiter=self._limiter,
            abandon_on_cancel=True,
        )

    async def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send an HTTP request asynchronously."""
        return await self._run_sync(
            self._sync_client.request,
            method,
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a GET request asynchronously."""
        return await self._run_sync(
            self._sync_client.get,
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def post(
        self,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a POST request asynchronously."""
        return await self._run_sync(
            self._sync_client.post,
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def put(
        self,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a PUT request asynchronously."""
        return await self._run_sync(
            self._sync_client.put,
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def patch(
        self,
        url: str,
        *,
        content: bytes | None = None,
        data: dict[str, Any] | None = None,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a PATCH request asynchronously."""
        return await self._run_sync(
            self._sync_client.patch,
            url,
            content=content,
            data=data,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def delete(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a DELETE request asynchronously."""
        return await self._run_sync(
            self._sync_client.delete,
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def head(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send a HEAD request asynchronously."""
        return await self._run_sync(
            self._sync_client.head,
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def options(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | Headers | None = None,
        cookies: dict[str, str] | Cookies | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | Timeout | None = None,
        follow_redirects: bool | None = None,
    ) -> Response:
        """Send an OPTIONS request asynchronously."""
        return await self._run_sync(
            self._sync_client.options,
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def aclose(self) -> None:
        """Close the client and release resources."""
        self._sync_client.close()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"<AsyncClient [{self._sync_client._profile or 'custom'}]>"
