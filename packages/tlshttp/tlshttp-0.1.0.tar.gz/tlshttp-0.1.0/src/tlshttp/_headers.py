"""Case-insensitive headers implementation."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from typing import Any


class Headers(MutableMapping[str, str]):
    """Case-insensitive dictionary for HTTP headers.

    HTTP headers are case-insensitive per RFC 7230. This class provides
    a dict-like interface that handles case-insensitivity correctly.

    Example:
        >>> headers = Headers({"Content-Type": "application/json"})
        >>> headers["content-type"]
        'application/json'
        >>> headers["CONTENT-TYPE"]
        'application/json'
    """

    def __init__(
        self,
        headers: Mapping[str, str] | list[tuple[str, str]] | None = None,
    ) -> None:
        # Store as: lowered_key -> (original_key, value)
        self._store: dict[str, tuple[str, str]] = {}

        if headers is not None:
            if isinstance(headers, Mapping):
                for key, value in headers.items():
                    self[key] = value
            else:
                for key, value in headers:
                    self[key] = value

    def __getitem__(self, key: str) -> str:
        return self._store[key.lower()][1]

    def __setitem__(self, key: str, value: str) -> None:
        self._store[key.lower()] = (key, str(value))

    def __delitem__(self, key: str) -> None:
        del self._store[key.lower()]

    def __iter__(self) -> Iterator[str]:
        return (original for original, _ in self._store.values())

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str):
            return key.lower() in self._store
        return False

    def __repr__(self) -> str:
        items = ", ".join(f"{k!r}: {v!r}" for k, v in self.items())
        return f"Headers({{{items}}})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Headers):
            # Compare by lowered keys and values only (ignore original key case)
            self_items = {k: v for k, v in self._store.items()}
            other_items = {k: v for k, v in other._store.items()}
            # Only compare the values, not the original keys
            return {k: v[1] for k, v in self_items.items()} == {k: v[1] for k, v in other_items.items()}
        if isinstance(other, Mapping):
            # Compare case-insensitively
            self_lower = {k.lower(): v for k, v in self.items()}
            other_lower = {k.lower(): v for k, v in other.items()}
            return self_lower == other_lower
        return NotImplemented

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get header value, or default if not present."""
        try:
            return self[key]
        except KeyError:
            return default

    def get_list(self, key: str) -> list[str]:
        """Get all values for a header (splits comma-separated values).

        Example:
            >>> headers = Headers({"Accept": "text/html, application/json"})
            >>> headers.get_list("Accept")
            ['text/html', 'application/json']
        """
        value = self.get(key)
        if value is None:
            return []
        return [v.strip() for v in value.split(",")]

    def copy(self) -> Headers:
        """Return a shallow copy."""
        new = Headers()
        new._store = self._store.copy()
        return new

    def update(self, other: Mapping[str, str] | None = None, **kwargs: str) -> None:
        """Update headers from a mapping or keyword arguments."""
        if other is not None:
            for key, value in other.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def to_dict(self) -> dict[str, str]:
        """Convert to a regular dictionary."""
        return {k: v for k, v in self.items()}

    def items(self) -> Iterator[tuple[str, str]]:  # type: ignore[override]
        """Return iterator of (key, value) pairs."""
        return iter((k, v) for k, v in self._store.values())

    def keys(self) -> Iterator[str]:  # type: ignore[override]
        """Return iterator of header names."""
        return iter(k for k, _ in self._store.values())

    def values(self) -> Iterator[str]:  # type: ignore[override]
        """Return iterator of header values."""
        return iter(v for _, v in self._store.values())

    @classmethod
    def from_go_response(cls, headers: dict[str, list[str]] | None) -> Headers:
        """Create Headers from Go library response format.

        The Go library returns headers as dict[str, list[str]],
        where each header can have multiple values.
        """
        result = cls()
        if headers is None:
            return result
        for key, values in headers.items():
            # Join multiple values with comma (per HTTP spec)
            result[key] = ", ".join(values)
        return result


def merge_headers(
    base: Headers | dict[str, str] | None,
    override: Headers | dict[str, str] | None,
) -> Headers:
    """Merge two header sets, with override taking precedence."""
    result = Headers()

    if base is not None:
        for key, value in base.items():
            result[key] = value

    if override is not None:
        for key, value in override.items():
            result[key] = value

    return result
