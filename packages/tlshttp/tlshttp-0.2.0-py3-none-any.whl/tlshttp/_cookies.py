"""Cookie jar implementation with working clear() method."""

from __future__ import annotations

import http.cookiejar
import time
from collections.abc import Iterator, MutableMapping
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request


class Cookies(MutableMapping[str, str]):
    """Cookie jar with proper domain/path handling.

    This implementation fixes the cookie clearing bug in existing wrappers
    by properly syncing state with the underlying cookie jar.

    Example:
        >>> cookies = Cookies()
        >>> cookies.set("session", "abc123", domain="example.com")
        >>> cookies["session"]
        'abc123'
        >>> cookies.clear()  # Actually clears cookies (unlike existing wrappers)
        >>> len(cookies)
        0
    """

    def __init__(
        self,
        cookies: dict[str, str] | Cookies | None = None,
    ) -> None:
        self._jar = http.cookiejar.CookieJar()

        if cookies is not None:
            if isinstance(cookies, Cookies):
                # Copy from another Cookies instance
                for cookie in cookies._jar:
                    self._jar.set_cookie(cookie)
            else:
                # Simple dict: set cookies without domain
                for name, value in cookies.items():
                    self.set(name, value)

    def __getitem__(self, name: str) -> str:
        for cookie in self._jar:
            if cookie.name == name:
                return cookie.value
        raise KeyError(name)

    def __setitem__(self, name: str, value: str) -> None:
        self.set(name, value)

    def __delitem__(self, name: str) -> None:
        self.delete(name)

    def __iter__(self) -> Iterator[str]:
        seen: set[str] = set()
        for cookie in self._jar:
            if cookie.name not in seen:
                seen.add(cookie.name)
                yield cookie.name

    def __len__(self) -> int:
        return len(list(self._jar))

    def __bool__(self) -> bool:
        return len(self) > 0

    def __repr__(self) -> str:
        items = ", ".join(f"{c.name!r}: {c.value!r}" for c in self._jar)
        return f"Cookies({{{items}}})"

    def set(
        self,
        name: str,
        value: str,
        domain: str = "",
        path: str = "/",
        expires: int | None = None,
        secure: bool = False,
        httponly: bool = False,
    ) -> None:
        """Set a cookie with full attributes.

        Args:
            name: Cookie name.
            value: Cookie value.
            domain: Cookie domain (empty for any domain).
            path: Cookie path.
            expires: Expiration timestamp (Unix epoch).
            secure: Secure flag.
            httponly: HTTPOnly flag.
        """
        # Remove existing cookie with same name/domain/path
        self._remove_cookie(name, domain, path)

        # Create new cookie
        cookie = http.cookiejar.Cookie(
            version=0,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain=domain,
            domain_specified=bool(domain),
            domain_initial_dot=domain.startswith(".") if domain else False,
            path=path,
            path_specified=True,
            secure=secure,
            expires=expires,
            discard=expires is None,
            comment=None,
            comment_url=None,
            rest={"HttpOnly": httponly} if httponly else {},
            rfc2109=False,
        )
        self._jar.set_cookie(cookie)

    def get(
        self,
        name: str,
        default: str | None = None,
        domain: str | None = None,
        path: str | None = None,
    ) -> str | None:
        """Get cookie value, optionally filtering by domain/path.

        Args:
            name: Cookie name.
            default: Default value if not found.
            domain: Filter by domain.
            path: Filter by path.

        Returns:
            Cookie value or default.
        """
        for cookie in self._jar:
            if cookie.name != name:
                continue
            if domain is not None and cookie.domain != domain:
                continue
            if path is not None and cookie.path != path:
                continue
            return cookie.value
        return default

    def delete(
        self,
        name: str,
        domain: str | None = None,
        path: str | None = None,
    ) -> None:
        """Delete a cookie by name, optionally filtering by domain/path.

        Args:
            name: Cookie name.
            domain: Filter by domain.
            path: Filter by path.
        """
        self._remove_cookie(name, domain, path)

    def clear(
        self,
        domain: str | None = None,
        path: str | None = None,
    ) -> None:
        """Clear cookies.

        This is the FIX for the bug in existing wrappers - this actually works!

        Args:
            domain: Only clear cookies for this domain.
            path: Only clear cookies for this path.
        """
        if domain is None and path is None:
            # Clear all cookies
            self._jar.clear()
        else:
            # Clear specific cookies
            to_remove = []
            for cookie in self._jar:
                if domain is not None and cookie.domain != domain:
                    continue
                if path is not None and cookie.path != path:
                    continue
                to_remove.append((cookie.domain, cookie.path, cookie.name))

            for d, p, n in to_remove:
                try:
                    self._jar.clear(d, p, n)
                except KeyError:
                    pass

    def _remove_cookie(
        self,
        name: str,
        domain: str | None = None,
        path: str | None = None,
    ) -> None:
        """Remove a cookie from the jar."""
        to_remove = []
        for cookie in self._jar:
            if cookie.name != name:
                continue
            if domain is not None and cookie.domain != domain:
                continue
            if path is not None and cookie.path != path:
                continue
            to_remove.append((cookie.domain, cookie.path, cookie.name))

        for d, p, n in to_remove:
            try:
                self._jar.clear(d, p, n)
            except KeyError:
                pass

    def for_url(self, url: str) -> dict[str, str]:
        """Get cookies applicable to a URL.

        Args:
            url: URL to get cookies for.

        Returns:
            Dictionary of applicable cookies.
        """
        # Use the cookie jar's built-in URL matching
        request = Request(url)
        self._jar.add_cookie_header(request)
        cookie_header = request.get_header("Cookie")

        if not cookie_header:
            return {}

        # Parse the Cookie header
        result = {}
        for part in cookie_header.split(";"):
            part = part.strip()
            if "=" in part:
                name, value = part.split("=", 1)
                result[name.strip()] = value.strip()
        return result

    def update_from_response(
        self,
        cookies: dict[str, str],
        url: str,
    ) -> None:
        """Update cookies from a response.

        Args:
            cookies: Cookies from response.
            url: Request URL (used for domain/path defaults).
        """
        parsed = urlparse(url)
        domain = parsed.netloc.split(":")[0]  # Remove port

        for name, value in cookies.items():
            self.set(name, value, domain=domain)

    def to_dict(self) -> dict[str, str]:
        """Convert to a simple dictionary.

        Note: This loses domain/path information.

        Returns:
            Dictionary of cookie name -> value.
        """
        result = {}
        for cookie in self._jar:
            # Last value wins for duplicate names
            result[cookie.name] = cookie.value
        return result

    def to_request_format(self) -> list[dict[str, str]]:
        """Convert to format expected by the Go library.

        Returns:
            List of cookie dictionaries.
        """
        result = []
        for cookie in self._jar:
            # Remove double quotes (fhttp library limitation)
            value = cookie.value.replace('"', "")
            result.append({
                "name": cookie.name,
                "value": value,
            })
        return result

    def copy(self) -> Cookies:
        """Create a copy of this cookie jar.

        Returns:
            New Cookies instance with same cookies.
        """
        return Cookies(self)


def merge_cookies(
    base: Cookies | dict[str, str] | None,
    override: Cookies | dict[str, str] | None,
) -> Cookies:
    """Merge two cookie sets, with override taking precedence.

    Args:
        base: Base cookies.
        override: Override cookies.

    Returns:
        Merged Cookies instance.
    """
    result = Cookies()

    if base is not None:
        if isinstance(base, Cookies):
            for cookie in base._jar:
                result._jar.set_cookie(cookie)
        else:
            for name, value in base.items():
                result.set(name, value)

    if override is not None:
        if isinstance(override, Cookies):
            for cookie in override._jar:
                result._jar.set_cookie(cookie)
        else:
            for name, value in override.items():
                result.set(name, value)

    return result
