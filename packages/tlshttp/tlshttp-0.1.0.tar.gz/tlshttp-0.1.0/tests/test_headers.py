"""Tests for case-insensitive Headers class."""

import pytest

from tlshttp import Headers
from tlshttp._headers import merge_headers


class TestHeaders:
    """Test Headers class functionality."""

    def test_case_insensitive_get(self, headers):
        """Headers should be case-insensitive for lookups."""
        assert headers["Content-Type"] == "application/json"
        assert headers["content-type"] == "application/json"
        assert headers["CONTENT-TYPE"] == "application/json"
        assert headers["Content-type"] == "application/json"

    def test_case_insensitive_set(self):
        """Setting a header should be case-insensitive."""
        headers = Headers()
        headers["Content-Type"] = "text/html"
        headers["content-type"] = "application/json"

        assert len(headers) == 1
        assert headers["Content-Type"] == "application/json"

    def test_case_insensitive_contains(self, headers):
        """Containment check should be case-insensitive."""
        assert "Content-Type" in headers
        assert "content-type" in headers
        assert "CONTENT-TYPE" in headers
        assert "Not-Present" not in headers

    def test_case_insensitive_delete(self):
        """Deletion should be case-insensitive."""
        headers = Headers({"Content-Type": "application/json"})
        del headers["content-type"]

        assert "Content-Type" not in headers
        assert len(headers) == 0

    def test_get_with_default(self, headers):
        """get() should return default for missing keys."""
        assert headers.get("Content-Type") == "application/json"
        assert headers.get("Missing") is None
        assert headers.get("Missing", "default") == "default"

    def test_get_list(self):
        """get_list() should split comma-separated values."""
        headers = Headers({"Accept": "text/html, application/json, text/plain"})

        result = headers.get_list("Accept")
        assert result == ["text/html", "application/json", "text/plain"]

        # Non-existent header returns empty list
        assert headers.get_list("Missing") == []

    def test_iteration(self, headers):
        """Iteration should return original key names."""
        keys = list(headers.keys())
        assert "Content-Type" in keys
        assert "X-Custom" in keys

    def test_items(self, headers):
        """items() should return original keys and values."""
        items = dict(headers.items())
        assert items["Content-Type"] == "application/json"
        assert items["X-Custom"] == "value"

    def test_to_dict(self, headers):
        """to_dict() should return a regular dictionary."""
        d = headers.to_dict()
        assert isinstance(d, dict)
        assert not isinstance(d, Headers)
        assert d["Content-Type"] == "application/json"

    def test_copy(self, headers):
        """copy() should create an independent copy."""
        copy = headers.copy()
        copy["New-Header"] = "new-value"

        assert "New-Header" in copy
        assert "New-Header" not in headers

    def test_update(self):
        """update() should merge headers."""
        headers = Headers({"A": "1"})
        headers.update({"B": "2", "C": "3"})

        assert headers["A"] == "1"
        assert headers["B"] == "2"
        assert headers["C"] == "3"

    def test_from_list(self):
        """Headers should accept list of tuples."""
        headers = Headers([("Content-Type", "application/json"), ("X-Custom", "value")])

        assert headers["content-type"] == "application/json"
        assert headers["x-custom"] == "value"

    def test_from_go_response(self):
        """from_go_response() should handle Go library format."""
        go_headers = {
            "Content-Type": ["application/json"],
            "Set-Cookie": ["a=1", "b=2"],
        }

        headers = Headers.from_go_response(go_headers)

        assert headers["Content-Type"] == "application/json"
        assert headers["Set-Cookie"] == "a=1, b=2"

    def test_equality(self):
        """Headers should compare equal regardless of key case."""
        h1 = Headers({"Content-Type": "application/json"})
        h2 = Headers({"content-type": "application/json"})

        assert h1 == h2

    def test_repr(self, headers):
        """repr() should show header contents."""
        r = repr(headers)
        assert "Headers(" in r
        assert "Content-Type" in r


class TestMergeHeaders:
    """Test merge_headers function."""

    def test_merge_none_base(self):
        """Merging with None base should return override only."""
        override = Headers({"A": "1"})
        result = merge_headers(None, override)

        assert result["A"] == "1"

    def test_merge_none_override(self):
        """Merging with None override should return base only."""
        base = Headers({"A": "1"})
        result = merge_headers(base, None)

        assert result["A"] == "1"

    def test_merge_both_none(self):
        """Merging two Nones should return empty Headers."""
        result = merge_headers(None, None)
        assert len(result) == 0

    def test_merge_override_takes_precedence(self):
        """Override values should replace base values."""
        base = Headers({"A": "1", "B": "2"})
        override = Headers({"B": "override", "C": "3"})

        result = merge_headers(base, override)

        assert result["A"] == "1"
        assert result["B"] == "override"
        assert result["C"] == "3"

    def test_merge_with_dicts(self):
        """merge_headers should accept plain dicts."""
        result = merge_headers({"A": "1"}, {"B": "2"})

        assert result["A"] == "1"
        assert result["B"] == "2"
