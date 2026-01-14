"""Request class for tlshttp."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse

from ._headers import Headers
from ._types import HttpMethod


@dataclass
class Request:
    """HTTP request object.

    This class represents an HTTP request with all its components.
    It's similar to httpx.Request.
    """

    method: HttpMethod
    url: str
    headers: Headers = field(default_factory=Headers)
    content: bytes | None = None
    params: dict[str, str] | None = None

    def __post_init__(self) -> None:
        # Ensure headers is a Headers instance
        if not isinstance(self.headers, Headers):
            self.headers = Headers(self.headers)

        # Apply query params to URL
        if self.params:
            self.url = self._apply_params(self.url, self.params)
            self.params = None

    @staticmethod
    def _apply_params(url: str, params: dict[str, str]) -> str:
        """Apply query parameters to a URL."""
        parsed = urlparse(url)
        if parsed.query:
            new_query = f"{parsed.query}&{urlencode(params)}"
        else:
            new_query = urlencode(params)
        return urlunparse(parsed._replace(query=new_query))

    @property
    def host(self) -> str:
        """Get the host from the URL."""
        parsed = urlparse(self.url)
        return parsed.netloc

    @property
    def scheme(self) -> str:
        """Get the scheme from the URL."""
        parsed = urlparse(self.url)
        return parsed.scheme

    @property
    def path(self) -> str:
        """Get the path from the URL."""
        parsed = urlparse(self.url)
        return parsed.path or "/"

    def __repr__(self) -> str:
        return f"<Request [{self.method} {self.url}]>"
