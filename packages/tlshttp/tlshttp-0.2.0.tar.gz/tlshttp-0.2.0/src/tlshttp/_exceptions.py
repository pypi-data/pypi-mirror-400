"""Exception classes for tlshttp."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._request import Request
    from ._response import Response


class TLSClientError(Exception):
    """Base exception for all tlshttp errors."""

    pass


class RequestError(TLSClientError):
    """Error during request execution."""

    def __init__(self, message: str, request: Request | None = None) -> None:
        self.request = request
        super().__init__(message)


class TimeoutError(RequestError):
    """Request timed out."""

    pass


class ConnectError(RequestError):
    """Failed to establish connection."""

    pass


class ProxyError(ConnectError):
    """Proxy connection failed."""

    pass


class TLSError(ConnectError):
    """TLS/SSL handshake failed."""

    pass


class HTTPStatusError(RequestError):
    """Response had error status code (4xx/5xx)."""

    def __init__(
        self,
        message: str,
        *,
        request: Request,
        response: Response,
    ) -> None:
        self.response = response
        super().__init__(message, request)


class LibraryNotFoundError(TLSClientError):
    """Shared library not found and couldn't be downloaded."""

    pass


class LibraryError(TLSClientError):
    """Error from the Go tls-client library."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        self.error_code = error_code
        super().__init__(message)


class InvalidURLError(TLSClientError):
    """Invalid URL provided."""

    pass


class CookieConflictError(TLSClientError):
    """Cookie conflict (e.g., setting conflicting domains)."""

    pass
