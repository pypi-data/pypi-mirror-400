"""Response class for tlshttp."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from ._cookies import Cookies
from ._exceptions import HTTPStatusError
from ._headers import Headers
from ._request import Request


@dataclass
class Response:
    """HTTP response object.

    This class represents an HTTP response with all its components.
    It's similar to httpx.Response.

    Example:
        >>> response = client.get("https://httpbin.org/json")
        >>> response.status_code
        200
        >>> response.headers["content-type"]
        'application/json'
        >>> response.json()
        {...}
    """

    status_code: int
    headers: Headers
    content: bytes
    url: str
    request: Request
    cookies: Cookies = field(default_factory=Cookies)
    http_version: str = "HTTP/1.1"
    elapsed: timedelta = field(default_factory=lambda: timedelta(0))

    _encoding: str | None = field(default=None, repr=False)

    @property
    def text(self) -> str:
        """Decode content using detected or specified encoding.

        Returns:
            Decoded content as string.
        """
        return self.content.decode(self.encoding)

    @property
    def encoding(self) -> str:
        """Detected encoding from headers or content.

        Returns:
            Encoding string (defaults to 'utf-8').
        """
        if self._encoding is not None:
            return self._encoding

        # Try to get from Content-Type header
        content_type = self.headers.get("content-type", "")
        if content_type:
            match = re.search(r"charset=([^\s;]+)", content_type, re.IGNORECASE)
            if match:
                return match.group(1).strip('"\'')

        # Default to UTF-8
        return "utf-8"

    @encoding.setter
    def encoding(self, value: str) -> None:
        """Set the encoding to use for text decoding."""
        self._encoding = value

    def json(self, **kwargs: Any) -> Any:
        """Parse response content as JSON.

        Args:
            **kwargs: Arguments passed to json.loads().

        Returns:
            Parsed JSON data.
        """
        return json.loads(self.content, **kwargs)

    @property
    def is_success(self) -> bool:
        """Check if response was successful (2xx status)."""
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        """Check if response is a redirect."""
        return self.status_code in (301, 302, 303, 307, 308)

    @property
    def is_client_error(self) -> bool:
        """Check if response is a client error (4xx status)."""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if response is a server error (5xx status)."""
        return 500 <= self.status_code < 600

    @property
    def is_error(self) -> bool:
        """Check if response is an error (4xx or 5xx)."""
        return self.status_code >= 400

    @property
    def ok(self) -> bool:
        """Alias for is_success."""
        return self.is_success

    @property
    def reason_phrase(self) -> str:
        """Get the HTTP reason phrase for the status code."""
        phrases = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }
        return phrases.get(self.status_code, "Unknown")

    def raise_for_status(self) -> Response:
        """Raise HTTPStatusError for 4xx/5xx responses.

        Returns:
            Self if successful.

        Raises:
            HTTPStatusError: If response status is 4xx or 5xx.
        """
        if self.is_error:
            raise HTTPStatusError(
                f"HTTP {self.status_code} {self.reason_phrase}",
                request=self.request,
                response=self,
            )
        return self

    def __repr__(self) -> str:
        return f"<Response [{self.status_code} {self.reason_phrase}]>"

    def __bool__(self) -> bool:
        """Response is truthy if successful."""
        return self.is_success
