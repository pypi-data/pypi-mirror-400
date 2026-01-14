"""tlshttp - Modern Python wrapper for tls-client with httpx-like API.

A high-performance HTTP client with browser TLS fingerprinting to bypass
anti-bot detection systems.

Example:
    >>> import tlshttp
    >>>
    >>> # Synchronous usage
    >>> with tlshttp.Client(profile="chrome_120") as client:
    ...     response = client.get("https://httpbin.org/json")
    ...     print(response.json())
    >>>
    >>> # Asynchronous usage
    >>> async with tlshttp.AsyncClient() as client:
    ...     response = await client.get("https://httpbin.org/json")
    ...     print(response.json())
"""

from ._client import AsyncClient, Client
from ._cookies import Cookies
from ._exceptions import (
    ConnectError,
    CookieConflictError,
    HTTPStatusError,
    InvalidURLError,
    LibraryError,
    LibraryNotFoundError,
    ProxyError,
    RequestError,
    TimeoutError,
    TLSClientError,
    TLSError,
)
from ._headers import Headers
from ._request import Request
from ._response import Response
from ._types import ProxyConfig, Timeout
from .profiles import Android, Chrome, Firefox, Opera, Profile, Safari

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Clients
    "Client",
    "AsyncClient",
    # Request/Response
    "Request",
    "Response",
    "Headers",
    "Cookies",
    # Configuration
    "Timeout",
    "ProxyConfig",
    # Profiles
    "Profile",
    "Chrome",
    "Firefox",
    "Safari",
    "Opera",
    "Android",
    # Exceptions
    "TLSClientError",
    "RequestError",
    "TimeoutError",
    "ConnectError",
    "ProxyError",
    "TLSError",
    "HTTPStatusError",
    "LibraryNotFoundError",
    "LibraryError",
    "InvalidURLError",
    "CookieConflictError",
]
