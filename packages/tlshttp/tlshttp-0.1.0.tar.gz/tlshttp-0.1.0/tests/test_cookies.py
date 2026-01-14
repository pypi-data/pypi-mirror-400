"""Tests for Cookies class - especially the clear() fix."""

import pytest

from tlshttp import Cookies
from tlshttp._cookies import merge_cookies


class TestCookies:
    """Test Cookies class functionality."""

    def test_basic_get_set(self, cookies):
        """Basic cookie get/set operations."""
        assert cookies["session"] == "abc123"
        assert cookies["user"] == "john"

    def test_set_with_domain(self):
        """Setting cookies with domain."""
        cookies = Cookies()
        cookies.set("session", "abc123", domain="example.com")

        assert cookies.get("session") == "abc123"
        assert cookies.get("session", domain="example.com") == "abc123"

    def test_dict_style_access(self, cookies):
        """Dictionary-style access."""
        cookies["new"] = "value"
        assert cookies["new"] == "value"

    def test_get_with_default(self, cookies):
        """get() should return default for missing cookies."""
        assert cookies.get("session") == "abc123"
        assert cookies.get("missing") is None
        assert cookies.get("missing", "default") == "default"

    def test_len(self, cookies):
        """len() should return cookie count."""
        assert len(cookies) == 2

    def test_iteration(self, cookies):
        """Iteration should yield cookie names."""
        names = list(cookies)
        assert "session" in names
        assert "user" in names

    def test_contains(self, cookies):
        """Containment check should work."""
        assert "session" in cookies
        assert "missing" not in cookies

    def test_bool(self):
        """Empty cookies should be falsy."""
        assert not Cookies()
        assert Cookies({"a": "1"})

    # CRITICAL TEST: This was broken in existing wrappers!
    def test_clear_actually_works(self):
        """clear() should actually remove all cookies.

        This is the FIX for the bug in existing wrappers where
        cookies.clear() didn't actually clear the cookies.
        """
        cookies = Cookies()
        cookies.set("session", "abc123", domain="example.com")
        cookies.set("user", "john", domain="example.com")
        cookies.set("other", "value", domain="other.com")

        # Verify cookies exist
        assert len(cookies) == 3

        # Clear all cookies
        cookies.clear()

        # THIS SHOULD PASS - but failed in existing wrappers!
        assert len(cookies) == 0
        assert "session" not in cookies
        assert "user" not in cookies
        assert "other" not in cookies

    def test_clear_by_domain(self):
        """clear(domain=...) should only clear cookies for that domain."""
        cookies = Cookies()
        cookies.set("a", "1", domain="example.com")
        cookies.set("b", "2", domain="example.com")
        cookies.set("c", "3", domain="other.com")

        cookies.clear(domain="example.com")

        assert len(cookies) == 1
        assert "a" not in cookies
        assert "b" not in cookies
        assert "c" in cookies

    def test_delete(self):
        """delete() should remove specific cookie."""
        cookies = Cookies({"a": "1", "b": "2"})
        cookies.delete("a")

        assert "a" not in cookies
        assert "b" in cookies

    def test_delete_nonexistent(self):
        """delete() on nonexistent cookie should not raise."""
        cookies = Cookies()
        cookies.delete("nonexistent")  # Should not raise

    def test_to_dict(self, cookies):
        """to_dict() should return simple dictionary."""
        d = cookies.to_dict()

        assert isinstance(d, dict)
        assert d == {"session": "abc123", "user": "john"}

    def test_to_request_format(self):
        """to_request_format() should return Go library format."""
        cookies = Cookies({"session": "abc123"})
        result = cookies.to_request_format()

        assert result == [{"name": "session", "value": "abc123"}]

    def test_to_request_format_strips_quotes(self):
        """to_request_format() should strip double quotes (fhttp limitation)."""
        cookies = Cookies({"session": '"quoted"'})
        result = cookies.to_request_format()

        assert result == [{"name": "session", "value": "quoted"}]

    def test_copy(self, cookies):
        """copy() should create independent copy."""
        copy = cookies.copy()
        copy.set("new", "value")

        assert "new" in copy
        assert "new" not in cookies

    def test_copy_from_cookies(self):
        """Cookies(other_cookies) should copy."""
        original = Cookies({"a": "1"})
        copy = Cookies(original)

        assert copy["a"] == "1"

        # Modifications shouldn't affect original
        copy["b"] = "2"
        assert "b" not in original

    def test_update_from_response(self):
        """update_from_response() should add cookies."""
        cookies = Cookies()
        cookies.update_from_response(
            {"session": "abc", "user": "john"},
            "https://example.com/path"
        )

        assert cookies.get("session") == "abc"
        assert cookies.get("user") == "john"

    def test_for_url(self):
        """for_url() should return applicable cookies."""
        cookies = Cookies()
        cookies.set("session", "abc", domain="example.com", path="/")

        applicable = cookies.for_url("https://example.com/page")
        assert applicable.get("session") == "abc"


class TestMergeCookies:
    """Test merge_cookies function."""

    def test_merge_none_base(self):
        """Merging with None base should return override only."""
        override = Cookies({"a": "1"})
        result = merge_cookies(None, override)

        assert result["a"] == "1"

    def test_merge_none_override(self):
        """Merging with None override should return base only."""
        base = Cookies({"a": "1"})
        result = merge_cookies(base, None)

        assert result["a"] == "1"

    def test_merge_both_none(self):
        """Merging two Nones should return empty Cookies."""
        result = merge_cookies(None, None)
        assert len(result) == 0

    def test_merge_override_takes_precedence(self):
        """Override values should replace base values."""
        base = Cookies({"a": "1", "b": "2"})
        override = Cookies({"b": "override", "c": "3"})

        result = merge_cookies(base, override)

        assert result["a"] == "1"
        assert result["b"] == "override"
        assert result["c"] == "3"

    def test_merge_with_dicts(self):
        """merge_cookies should accept plain dicts."""
        result = merge_cookies({"a": "1"}, {"b": "2"})

        assert result["a"] == "1"
        assert result["b"] == "2"
