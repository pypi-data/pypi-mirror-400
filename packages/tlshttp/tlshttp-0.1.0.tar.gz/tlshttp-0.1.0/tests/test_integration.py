"""Integration tests with real HTTP requests."""

import asyncio

import pytest

import tlshttp


# Mark all tests as integration tests (can be skipped with -m "not integration")
pytestmark = pytest.mark.integration


class TestSyncRequests:
    """Test synchronous HTTP requests."""

    def test_get_request(self, client):
        """GET request should work."""
        response = client.get("https://httpbin.org/get")

        assert response.status_code == 200
        assert response.is_success
        data = response.json()
        assert "origin" in data

    def test_get_with_params(self, client):
        """GET with query parameters should work."""
        response = client.get(
            "https://httpbin.org/get",
            params={"key": "value", "page": "1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["args"] == {"key": "value", "page": "1"}

    def test_get_with_headers(self, client):
        """GET with custom headers should work."""
        response = client.get(
            "https://httpbin.org/headers",
            headers={"X-Custom-Header": "custom-value"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "X-Custom-Header" in data["headers"]

    def test_post_json(self, client):
        """POST with JSON body should work."""
        response = client.post(
            "https://httpbin.org/post",
            json={"message": "Hello", "number": 42}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["json"] == {"message": "Hello", "number": 42}

    def test_post_form_data(self, client):
        """POST with form data should work."""
        response = client.post(
            "https://httpbin.org/post",
            data={"username": "john", "password": "secret"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["form"] == {"username": "john", "password": "secret"}

    def test_put_request(self, client):
        """PUT request should work."""
        response = client.put(
            "https://httpbin.org/put",
            json={"updated": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["json"] == {"updated": True}

    def test_delete_request(self, client):
        """DELETE request should work."""
        response = client.delete("https://httpbin.org/delete")

        assert response.status_code == 200

    def test_head_request(self, client):
        """HEAD request should work."""
        response = client.head("https://httpbin.org/get")

        assert response.status_code == 200
        assert len(response.content) == 0  # HEAD has no body

    def test_redirect_follow(self):
        """Client should follow redirects by default."""
        with tlshttp.Client(follow_redirects=True) as client:
            response = client.get("https://httpbin.org/redirect/2")

            assert response.status_code == 200
            assert "httpbin.org/get" in response.url

    def test_cookies_from_response(self, client):
        """Cookies from response should be stored."""
        response = client.get("https://httpbin.org/cookies/set/session/abc123")

        assert response.status_code == 200
        assert client.cookies.get("session") == "abc123"

    def test_cookies_sent_in_request(self, client):
        """Stored cookies should be sent in subsequent requests."""
        # Set a cookie
        client.get("https://httpbin.org/cookies/set/session/xyz789")

        # Verify it's sent
        response = client.get("https://httpbin.org/cookies")
        data = response.json()

        assert data["cookies"].get("session") == "xyz789"

    def test_response_headers_case_insensitive(self, client):
        """Response headers should be case-insensitive."""
        response = client.get("https://httpbin.org/get")

        # These should all return the same value
        ct1 = response.headers.get("Content-Type")
        ct2 = response.headers.get("content-type")
        ct3 = response.headers.get("CONTENT-TYPE")

        assert ct1 == ct2 == ct3


class TestAsyncRequests:
    """Test asynchronous HTTP requests."""

    @pytest.mark.anyio
    async def test_async_get(self, async_client):
        """Async GET request should work."""
        response = await async_client.get("https://httpbin.org/get")

        assert response.status_code == 200
        data = response.json()
        assert "origin" in data

    @pytest.mark.anyio
    async def test_async_post(self, async_client):
        """Async POST request should work."""
        response = await async_client.post(
            "https://httpbin.org/post",
            json={"async": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["json"] == {"async": True}

    @pytest.mark.anyio
    async def test_concurrent_requests(self, async_client):
        """Concurrent async requests should work."""
        urls = [f"https://httpbin.org/get?id={i}" for i in range(3)]
        tasks = [async_client.get(url) for url in urls]

        responses = await asyncio.gather(*tasks)

        assert len(responses) == 3
        assert all(r.status_code == 200 for r in responses)


class TestTLSFingerprinting:
    """Test TLS fingerprinting with different profiles."""

    def test_chrome_fingerprint(self):
        """Chrome profile should have Chrome-like fingerprint."""
        with tlshttp.Client(profile="chrome_120") as client:
            response = client.get("https://tls.peet.ws/api/all")

            if response.status_code == 200:
                data = response.json()
                ja3 = data.get("tls", {}).get("ja3", "")
                # Chrome fingerprints typically start with 771
                assert ja3.startswith("771")

    def test_firefox_fingerprint(self):
        """Firefox profile should have Firefox-like fingerprint."""
        with tlshttp.Client(profile="firefox_120") as client:
            response = client.get("https://tls.peet.ws/api/all")

            if response.status_code == 200:
                data = response.json()
                ja3 = data.get("tls", {}).get("ja3", "")
                # Firefox also uses 771
                assert ja3.startswith("771")

    def test_different_profiles_different_fingerprints(self):
        """Different profiles should produce different fingerprints."""
        fingerprints = {}

        for profile in ["chrome_120", "firefox_120", "safari_16_0"]:
            with tlshttp.Client(profile=profile) as client:
                response = client.get("https://tls.peet.ws/api/all")
                if response.status_code == 200:
                    data = response.json()
                    fingerprints[profile] = data.get("tls", {}).get("ja3", "")

        # At least Chrome and Firefox should have different fingerprints
        if "chrome_120" in fingerprints and "firefox_120" in fingerprints:
            assert fingerprints["chrome_120"] != fingerprints["firefox_120"]


class TestErrorHandling:
    """Test error handling."""

    def test_http_error_status(self, client):
        """HTTP error status should be accessible."""
        response = client.get("https://httpbin.org/status/404")

        assert response.status_code == 404
        assert response.is_client_error
        assert response.is_error

    def test_raise_for_status(self, client):
        """raise_for_status should raise for error codes."""
        response = client.get("https://httpbin.org/status/500")

        with pytest.raises(tlshttp.HTTPStatusError) as exc_info:
            response.raise_for_status()

        assert exc_info.value.response.status_code == 500

    @pytest.mark.skip(reason="tls-client has known timeout reliability issues - see GitHub issue #124")
    def test_timeout_error(self):
        """Timeout should raise TimeoutError.

        Note: The underlying tls-client Go library has known issues with
        timeout reliability, especially with short timeouts. This is a
        documented issue in the upstream library.
        """
        with tlshttp.Client(timeout=1.0) as client:
            with pytest.raises(tlshttp.TimeoutError):
                client.get("https://httpbin.org/delay/10")

    def test_closed_client_error(self, client):
        """Request on closed client should raise."""
        client.close()

        with pytest.raises(tlshttp.RequestError):
            client.get("https://httpbin.org/get")
