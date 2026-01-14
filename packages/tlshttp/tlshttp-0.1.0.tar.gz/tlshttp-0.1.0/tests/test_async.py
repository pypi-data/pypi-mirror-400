"""Tests for AsyncClient class."""

import asyncio

import pytest

import tlshttp
from tlshttp import AsyncClient, Headers, Cookies


class TestAsyncClientCreation:
    """Test AsyncClient instantiation."""

    @pytest.mark.anyio
    async def test_default_creation(self):
        """AsyncClient should create with defaults."""
        async with AsyncClient() as client:
            assert client._sync_client._profile == "chrome_120"
            assert not client.is_closed

    @pytest.mark.anyio
    async def test_custom_profile(self):
        """AsyncClient should accept custom profile."""
        async with AsyncClient(profile="firefox_120") as client:
            assert client._sync_client._profile == "firefox_120"

    @pytest.mark.anyio
    async def test_max_concurrent(self):
        """AsyncClient should accept max_concurrent."""
        async with AsyncClient(max_concurrent=5) as client:
            assert client._limiter.total_tokens == 5


class TestAsyncClientContextManager:
    """Test AsyncClient context manager behavior."""

    @pytest.mark.anyio
    async def test_context_manager_closes(self):
        """AsyncClient should close when exiting context."""
        client = AsyncClient()
        async with client:
            assert not client.is_closed
        assert client.is_closed

    @pytest.mark.anyio
    async def test_aclose(self):
        """aclose() should close the client."""
        client = AsyncClient()
        assert not client.is_closed
        await client.aclose()
        assert client.is_closed


class TestAsyncClientProperties:
    """Test AsyncClient properties."""

    @pytest.mark.anyio
    async def test_headers_property(self, async_client):
        """headers property should return Headers instance."""
        assert isinstance(async_client.headers, Headers)

    @pytest.mark.anyio
    async def test_cookies_property(self, async_client):
        """cookies property should return Cookies instance."""
        assert isinstance(async_client.cookies, Cookies)
