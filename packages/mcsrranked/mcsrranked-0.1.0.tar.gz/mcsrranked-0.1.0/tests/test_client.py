"""Tests for the client module."""

import httpx
import pytest
import respx

from mcsrranked import (
    AsyncMCSRRanked,
    MCSRRanked,
    NotFoundError,
    RateLimitError,
    User,
)


class TestMCSRRanked:
    """Tests for the synchronous client."""

    def test_client_initialization(self) -> None:
        """Test client can be initialized."""
        client = MCSRRanked()
        assert client is not None
        client.close()

    def test_client_with_options(self) -> None:
        """Test client with_options creates new client."""
        client = MCSRRanked(timeout=10.0)
        new_client = client.with_options(timeout=60.0)

        assert new_client is not client
        assert new_client._timeout == 60.0
        assert client._timeout == 10.0

        client.close()
        new_client.close()

    def test_client_context_manager(self) -> None:
        """Test client can be used as context manager."""
        with MCSRRanked() as client:
            assert client is not None

    def test_client_has_resources(self) -> None:
        """Test client has all expected resources."""
        client = MCSRRanked()

        assert hasattr(client, "users")
        assert hasattr(client, "matches")
        assert hasattr(client, "leaderboards")
        assert hasattr(client, "live")
        assert hasattr(client, "weekly_races")

        client.close()

    @respx.mock
    def test_get_user(self) -> None:
        """Test getting a user."""
        respx.get("https://api.mcsrranked.com/users/test_user").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "success",
                    "data": {
                        "uuid": "abc123",
                        "nickname": "TestUser",
                        "roleType": 0,
                        "eloRate": 1500,
                        "eloRank": 100,
                        "country": "us",
                    },
                },
            )
        )

        with MCSRRanked() as client:
            user = client.users.get("test_user")

            assert isinstance(user, User)
            assert user.uuid == "abc123"
            assert user.nickname == "TestUser"
            assert user.elo_rate == 1500

    @respx.mock
    def test_not_found_error(self) -> None:
        """Test NotFoundError is raised for 404 responses."""
        respx.get("https://api.mcsrranked.com/users/nonexistent").mock(
            return_value=httpx.Response(
                404,
                json={"status": "error", "data": None},
            )
        )

        with MCSRRanked() as client, pytest.raises(NotFoundError):
            client.users.get("nonexistent")

    @respx.mock
    def test_rate_limit_error(self) -> None:
        """Test RateLimitError is raised for 429 responses."""
        respx.get("https://api.mcsrranked.com/users/test").mock(
            return_value=httpx.Response(
                429,
                json={"status": "error", "data": "Too many requests"},
            )
        )

        with MCSRRanked() as client, pytest.raises(RateLimitError):
            client.users.get("test")


class TestAsyncMCSRRanked:
    """Tests for the asynchronous client."""

    @pytest.mark.asyncio
    async def test_async_client_initialization(self) -> None:
        """Test async client can be initialized."""
        client = AsyncMCSRRanked()
        assert client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self) -> None:
        """Test async client can be used as context manager."""
        async with AsyncMCSRRanked() as client:
            assert client is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_user(self) -> None:
        """Test getting a user asynchronously."""
        respx.get("https://api.mcsrranked.com/users/test_user").mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "success",
                    "data": {
                        "uuid": "abc123",
                        "nickname": "TestUser",
                        "roleType": 0,
                        "eloRate": 1500,
                        "eloRank": 100,
                        "country": "us",
                    },
                },
            )
        )

        async with AsyncMCSRRanked() as client:
            user = await client.users.get("test_user")

            assert isinstance(user, User)
            assert user.uuid == "abc123"
            assert user.nickname == "TestUser"
