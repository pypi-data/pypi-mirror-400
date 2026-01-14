"""JSON protocol for communicating with the Go library."""

from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import urlencode, urljoin, urlparse

from .._types import RequestPayload, Timeout


def build_request_payload(
    *,
    session_id: str,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    content: bytes | None = None,
    json_data: Any | None = None,
    params: dict[str, str] | None = None,
    cookies: list[dict[str, str]] | None = None,
    timeout: Timeout | None = None,
    follow_redirects: bool = True,
    proxy: str | None = None,
    verify: bool = True,
    http2: bool = True,
    profile: str | None = None,
    random_tls_extension_order: bool = True,
    header_order: list[str] | None = None,
) -> RequestPayload:
    """Build a request payload for the Go library.

    Args:
        session_id: Session identifier.
        method: HTTP method.
        url: Request URL.
        headers: Request headers.
        content: Raw request body.
        json_data: JSON request body (will be serialized).
        params: URL query parameters.
        cookies: Request cookies.
        timeout: Timeout configuration.
        follow_redirects: Whether to follow redirects.
        proxy: Proxy URL.
        verify: Whether to verify SSL certificates.
        http2: Whether to use HTTP/2.
        profile: Browser profile identifier.
        random_tls_extension_order: Randomize TLS extension order.
        header_order: Custom header order.

    Returns:
        Request payload dictionary for the Go library.
    """
    # Build the full URL with params
    if params:
        parsed = urlparse(url)
        separator = "&" if parsed.query else "?"
        url = f"{url}{separator}{urlencode(params)}"

    # Prepare request body
    request_body: str | None = None
    is_byte_request = False

    if json_data is not None:
        request_body = json.dumps(json_data)
        if headers is None:
            headers = {}
        if "content-type" not in {k.lower() for k in headers}:
            headers["Content-Type"] = "application/json"
    elif content is not None:
        if isinstance(content, bytes):
            request_body = base64.b64encode(content).decode("ascii")
            is_byte_request = True
        else:
            request_body = content

    # Build payload
    payload: RequestPayload = {
        "sessionId": session_id,
        "requestMethod": method.upper(),
        "requestUrl": url,
        "followRedirects": follow_redirects,
        "insecureSkipVerify": not verify,
        "withRandomTLSExtensionOrder": random_tls_extension_order,
        "isByteRequest": is_byte_request,
        "isByteResponse": True,  # Always get bytes for proper handling
    }

    # Add optional fields
    if profile:
        payload["tlsClientIdentifier"] = profile

    if headers:
        payload["headers"] = headers

    if header_order:
        payload["headerOrder"] = header_order

    if request_body:
        payload["requestBody"] = request_body

    if cookies:
        payload["requestCookies"] = cookies

    if proxy:
        payload["proxyUrl"] = proxy

    if timeout:
        # Use total timeout in seconds
        total_seconds = int(timeout.total)
        if total_seconds > 0:
            payload["timeoutSeconds"] = total_seconds

    if not http2:
        payload["forceHttp1"] = True

    return payload


def parse_response(response_data: dict[str, Any]) -> dict[str, Any]:
    """Parse the response from the Go library.

    Args:
        response_data: Raw response from the Go library.

    Returns:
        Parsed response dictionary.
    """
    result = {
        "id": response_data.get("id", ""),
        "session_id": response_data.get("sessionId", ""),
        "status_code": response_data.get("status", 0),
        "url": response_data.get("target", ""),
        "http_version": _normalize_protocol(response_data.get("usedProtocol", "")),
        "headers": response_data.get("headers", {}),
        "cookies": response_data.get("cookies", {}),
    }

    # Decode body - handle various formats
    body = response_data.get("body", "")
    if body:
        result["content"] = _decode_body(body)
    else:
        result["content"] = b""

    # Check for errors
    if "errorMessage" in response_data or "error" in response_data:
        result["error"] = response_data.get("errorMessage") or response_data.get("error")

    return result


def _decode_body(body: str) -> bytes:
    """Decode response body from various formats.

    The Go library can return body in different formats:
    - Plain text
    - Base64 encoded
    - Data URL format (data:text/plain;charset=utf-8;base64,...)

    Args:
        body: Raw body string from the library.

    Returns:
        Decoded body as bytes.
    """
    # Check for data URL format
    if body.startswith("data:"):
        # Parse data URL: data:[<mediatype>][;base64],<data>
        try:
            # Find the comma that separates metadata from data
            comma_idx = body.index(",")
            metadata = body[:comma_idx]
            data = body[comma_idx + 1:]

            if ";base64" in metadata:
                return base64.b64decode(data)
            else:
                # URL-encoded data
                from urllib.parse import unquote
                return unquote(data).encode("utf-8")
        except (ValueError, Exception):
            # If parsing fails, return as-is
            return body.encode("utf-8")

    # Try base64 decode (the library sometimes returns raw base64)
    try:
        # Check if it looks like base64 (alphanumeric + /+ with optional = padding)
        import re
        if re.match(r'^[A-Za-z0-9+/]+=*$', body) and len(body) % 4 == 0:
            return base64.b64decode(body)
    except Exception:
        pass

    # Return as plain text
    return body.encode("utf-8")


def _normalize_protocol(protocol: str) -> str:
    """Normalize protocol string to HTTP version."""
    protocol = protocol.lower()
    if protocol in ("h2", "http2", "http/2"):
        return "HTTP/2"
    elif protocol in ("h3", "http3", "http/3"):
        return "HTTP/3"
    else:
        return "HTTP/1.1"


def encode_cookies_for_request(cookies: dict[str, str]) -> list[dict[str, str]]:
    """Encode cookies for the Go library request format.

    Args:
        cookies: Dictionary of cookie name -> value.

    Returns:
        List of cookie dictionaries for the Go library.
    """
    result = []
    for name, value in cookies.items():
        # Remove double quotes (fhttp library limitation)
        clean_value = value.replace('"', "")
        result.append({"name": name, "value": clean_value})
    return result
