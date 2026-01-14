"""Tests for Client class."""

import pytest

import tlshttp
from tlshttp import Client, Headers, Cookies, Response
from tlshttp._types import Timeout


class TestClientCreation:
    """Test Client instantiation."""

    def test_default_creation(self):
        """Client should create with defaults."""
        with Client() as client:
            assert client._profile == "chrome_120"
            assert not client.is_closed

    def test_custom_profile(self):
        """Client should accept custom profile."""
        with Client(profile="firefox_120") as client:
            assert client._profile == "firefox_120"

    def test_profile_constant(self):
        """Client should accept Profile constants."""
        with Client(profile=tlshttp.Chrome.V133) as client:
            assert client._profile == "chrome_133"

    def test_custom_timeout_float(self):
        """Client should accept float timeout."""
        with Client(timeout=60.0) as client:
            assert client._timeout.total == 180.0  # connect + read + write

    def test_custom_timeout_object(self):
        """Client should accept Timeout object."""
        timeout = Timeout(connect=5.0, read=30.0, write=10.0)
        with Client(timeout=timeout) as client:
            assert client._timeout.connect == 5.0
            assert client._timeout.read == 30.0

    def test_custom_headers(self):
        """Client should accept default headers."""
        with Client(headers={"X-Custom": "value"}) as client:
            assert client.headers["X-Custom"] == "value"

    def test_custom_cookies(self):
        """Client should accept default cookies."""
        with Client(cookies={"session": "abc"}) as client:
            assert client.cookies["session"] == "abc"

    def test_base_url(self):
        """Client should store base_url."""
        with Client(base_url="https://api.example.com") as client:
            assert client._base_url == "https://api.example.com"

    def test_proxy_string(self):
        """Client should accept proxy as string."""
        with Client(proxy="http://proxy.example.com:8080") as client:
            assert client._proxy == "http://proxy.example.com:8080"

    def test_proxy_config(self):
        """Client should accept ProxyConfig."""
        proxy = tlshttp.ProxyConfig(
            url="http://proxy.example.com:8080",
            username="user",
            password="pass"
        )
        with Client(proxy=proxy) as client:
            assert "user:pass@" in client._proxy


class TestClientContextManager:
    """Test Client context manager behavior."""

    def test_context_manager_closes(self):
        """Client should close when exiting context."""
        client = Client()
        with client:
            assert not client.is_closed
        assert client.is_closed

    def test_double_close(self):
        """Double close should not raise."""
        with Client() as client:
            client.close()
            client.close()  # Should not raise


class TestClientProperties:
    """Test Client properties."""

    def test_headers_property(self, client):
        """headers property should return Headers instance."""
        assert isinstance(client.headers, Headers)

    def test_cookies_property(self, client):
        """cookies property should return Cookies instance."""
        assert isinstance(client.cookies, Cookies)

    def test_is_closed_property(self, client):
        """is_closed should reflect client state."""
        assert not client.is_closed


class TestTimeout:
    """Test Timeout class."""

    def test_float_init(self):
        """Timeout should accept single float."""
        t = Timeout(30.0)
        assert t.connect == 30.0
        assert t.read == 30.0
        assert t.write == 30.0

    def test_kwargs_init(self):
        """Timeout should accept keyword args."""
        t = Timeout(connect=5.0, read=30.0, write=10.0)
        assert t.connect == 5.0
        assert t.read == 30.0
        assert t.write == 10.0

    def test_dict_init(self):
        """Timeout should accept dict."""
        t = Timeout({"connect": 5.0, "read": 30.0})
        assert t.connect == 5.0
        assert t.read == 30.0

    def test_timeout_init(self):
        """Timeout should accept another Timeout."""
        t1 = Timeout(connect=5.0, read=30.0)
        t2 = Timeout(t1)
        assert t2.connect == 5.0
        assert t2.read == 30.0

    def test_total(self):
        """total should sum all timeouts."""
        t = Timeout(connect=5.0, read=30.0, write=10.0)
        assert t.total == 45.0


class TestResponse:
    """Test Response class."""

    def test_response_properties(self):
        """Response should have expected properties."""
        request = tlshttp.Request(method="GET", url="https://example.com")
        response = Response(
            status_code=200,
            headers=Headers({"Content-Type": "application/json"}),
            content=b'{"key": "value"}',
            url="https://example.com",
            request=request,
        )

        assert response.status_code == 200
        assert response.is_success
        assert not response.is_error
        assert response.ok
        assert response.reason_phrase == "OK"

    def test_response_json(self):
        """Response.json() should parse JSON."""
        request = tlshttp.Request(method="GET", url="https://example.com")
        response = Response(
            status_code=200,
            headers=Headers(),
            content=b'{"key": "value"}',
            url="https://example.com",
            request=request,
        )

        assert response.json() == {"key": "value"}

    def test_response_text(self):
        """Response.text should decode content."""
        request = tlshttp.Request(method="GET", url="https://example.com")
        response = Response(
            status_code=200,
            headers=Headers({"Content-Type": "text/plain; charset=utf-8"}),
            content=b"Hello, World!",
            url="https://example.com",
            request=request,
        )

        assert response.text == "Hello, World!"

    def test_response_encoding_from_header(self):
        """Response should detect encoding from Content-Type."""
        request = tlshttp.Request(method="GET", url="https://example.com")
        response = Response(
            status_code=200,
            headers=Headers({"Content-Type": "text/html; charset=iso-8859-1"}),
            content=b"Hello",
            url="https://example.com",
            request=request,
        )

        assert response.encoding == "iso-8859-1"

    def test_response_status_checks(self):
        """Response status checks should work."""
        request = tlshttp.Request(method="GET", url="https://example.com")

        # Success
        r200 = Response(status_code=200, headers=Headers(), content=b"",
                        url="", request=request)
        assert r200.is_success
        assert not r200.is_error

        # Redirect
        r302 = Response(status_code=302, headers=Headers(), content=b"",
                        url="", request=request)
        assert r302.is_redirect

        # Client error
        r404 = Response(status_code=404, headers=Headers(), content=b"",
                        url="", request=request)
        assert r404.is_client_error
        assert r404.is_error

        # Server error
        r500 = Response(status_code=500, headers=Headers(), content=b"",
                        url="", request=request)
        assert r500.is_server_error
        assert r500.is_error

    def test_raise_for_status(self):
        """raise_for_status should raise for error codes."""
        request = tlshttp.Request(method="GET", url="https://example.com")

        # Success should return self
        r200 = Response(status_code=200, headers=Headers(), content=b"",
                        url="", request=request)
        assert r200.raise_for_status() is r200

        # Error should raise
        r404 = Response(status_code=404, headers=Headers(), content=b"",
                        url="", request=request)
        with pytest.raises(tlshttp.HTTPStatusError) as exc_info:
            r404.raise_for_status()

        assert exc_info.value.response.status_code == 404
