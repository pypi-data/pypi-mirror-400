"""Type definitions for tlshttp."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict


# HTTP method types
HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

# Content types
ContentType = bytes | str | dict[str, Any] | None


class TimeoutConfig(TypedDict, total=False):
    """Timeout configuration."""

    connect: float
    read: float
    write: float
    pool: float


@dataclass
class Timeout:
    """Timeout settings for requests."""

    connect: float | None = 10.0
    read: float | None = 30.0
    write: float | None = 30.0
    pool: float | None = None

    def __init__(
        self,
        timeout: float | Timeout | TimeoutConfig | None = None,
        *,
        connect: float | None = None,
        read: float | None = None,
        write: float | None = None,
        pool: float | None = None,
    ) -> None:
        if isinstance(timeout, Timeout):
            self.connect = timeout.connect
            self.read = timeout.read
            self.write = timeout.write
            self.pool = timeout.pool
        elif isinstance(timeout, dict):
            self.connect = timeout.get("connect", 10.0)
            self.read = timeout.get("read", 30.0)
            self.write = timeout.get("write", 30.0)
            self.pool = timeout.get("pool")
        elif timeout is not None:
            self.connect = timeout
            self.read = timeout
            self.write = timeout
            self.pool = None
        else:
            self.connect = connect if connect is not None else 10.0
            self.read = read if read is not None else 30.0
            self.write = write if write is not None else 30.0
            self.pool = pool

    @property
    def total(self) -> float:
        """Total timeout for the request."""
        values = [v for v in (self.connect, self.read, self.write) if v is not None]
        return sum(values) if values else 30.0


# Go library protocol types
class TLSConfig(TypedDict, total=False):
    """TLS configuration for Go library."""

    ja3String: str
    h2Settings: dict[str, int]
    h2SettingsOrder: list[str]
    pseudoHeaderOrder: list[str]
    connectionFlow: int
    priorityFrames: list[dict[str, Any]]
    headerPriority: dict[str, Any]
    certCompressionAlgo: str
    supportedVersions: list[str]
    supportedSignatureAlgorithms: list[str]
    keyShareCurves: list[str]
    alpnProtocols: list[str]


class TransportOptions(TypedDict, total=False):
    """HTTP transport options."""

    disableKeepAlives: bool
    disableCompression: bool
    maxIdleConns: int
    maxIdleConnsPerHost: int
    maxConnsPerHost: int
    maxResponseHeaderBytes: int
    writeBufferSize: int
    readBufferSize: int
    idleConnTimeout: int


class RequestPayload(TypedDict, total=False):
    """Request payload for Go library."""

    sessionId: str
    tlsClientIdentifier: str
    customTlsClient: TLSConfig
    followRedirects: bool
    forceHttp1: bool
    insecureSkipVerify: bool
    isByteRequest: bool
    isByteResponse: bool
    withDebug: bool
    withRandomTLSExtensionOrder: bool
    timeoutSeconds: int
    timeoutMilliseconds: int
    proxyUrl: str
    headers: dict[str, str]
    headerOrder: list[str]
    requestUrl: str
    requestMethod: str
    requestBody: str
    requestCookies: list[dict[str, str]]


class ResponsePayload(TypedDict, total=False):
    """Response payload from Go library."""

    id: str
    sessionId: str
    status: int
    target: str
    body: str
    headers: dict[str, list[str]]
    cookies: dict[str, str]
    usedProtocol: str


@dataclass
class ProxyConfig:
    """Proxy configuration."""

    url: str
    username: str | None = None
    password: str | None = None

    def to_url(self) -> str:
        """Convert to proxy URL string."""
        if self.username and self.password:
            # Parse the URL and insert credentials
            if "://" in self.url:
                scheme, rest = self.url.split("://", 1)
                return f"{scheme}://{self.username}:{self.password}@{rest}"
            return f"http://{self.username}:{self.password}@{self.url}"
        return self.url


@dataclass
class ClientConfig:
    """Configuration for TLS client."""

    profile: str | None = "chrome_120"
    timeout: Timeout = field(default_factory=lambda: Timeout(30.0))
    follow_redirects: bool = True
    max_redirects: int = 10
    proxy: str | ProxyConfig | None = None
    verify: bool = True
    http2: bool = True
    http3: bool = False
    random_tls_extension_order: bool = True
    headers: dict[str, str] | None = None
    cookies: dict[str, str] | None = None
    base_url: str | None = None
