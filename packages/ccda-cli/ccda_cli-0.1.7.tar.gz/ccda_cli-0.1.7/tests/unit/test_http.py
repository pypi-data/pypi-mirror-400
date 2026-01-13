"""Unit tests for HTTP client module."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest

from ccda_cli.core.http import (
    AsyncHTTPClient,
    GitHubClient,
    DepsDevClient,
    ClearlyDefinedClient,
    RateLimitInfo,
    APIResponse,
    HTTPError,
    RateLimitError,
)


class TestRateLimitInfo:
    """Test rate limit information parsing."""

    def test_from_headers(self):
        """Parse rate limit from response headers."""
        headers = httpx.Headers({
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4999",
            "x-ratelimit-reset": "1704312000",
            "x-ratelimit-used": "1",
        })
        info = RateLimitInfo.from_headers(headers)
        assert info.limit == 5000
        assert info.remaining == 4999
        assert info.used == 1
        assert info.reset_at is not None

    def test_from_headers_defaults(self):
        """Missing headers should use defaults."""
        headers = httpx.Headers({})
        info = RateLimitInfo.from_headers(headers)
        assert info.limit == 5000
        assert info.remaining == 5000
        assert info.used == 0
        assert info.reset_at is None


class TestAsyncHTTPClient:
    """Test async HTTP client."""

    def test_client_initialization(self):
        """Client should initialize with defaults."""
        client = AsyncHTTPClient()
        assert client.base_url == ""
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.retry_delay == 1.0

    def test_client_with_custom_settings(self):
        """Client should accept custom settings."""
        client = AsyncHTTPClient(
            base_url="https://api.example.com",
            headers={"Authorization": "Bearer test"},
            timeout=60.0,
            max_retries=5,
        )
        assert client.base_url == "https://api.example.com"
        assert "Authorization" in client.headers
        assert client.timeout == 60.0
        assert client.max_retries == 5

    @pytest.mark.asyncio
    async def test_session_context_manager(self):
        """Session should work as async context manager."""
        client = AsyncHTTPClient()
        async with client.session() as session:
            assert session._client is not None
        assert client._client is None

    @pytest.mark.asyncio
    async def test_request_without_session_raises(self):
        """Request without session should raise error."""
        client = AsyncHTTPClient()
        with pytest.raises(RuntimeError, match="not initialized"):
            await client.get("/test")

    @pytest.mark.asyncio
    async def test_successful_get_request(self):
        """Successful GET request should return APIResponse."""
        client = AsyncHTTPClient(base_url="https://api.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.text = '{"data": "test"}'
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.request.return_value = mock_response

            async with client.session():
                response = await client.get("/test")

            assert response.status_code == 200
            assert response.data == {"data": "test"}

    @pytest.mark.asyncio
    async def test_rate_limit_error(self):
        """Rate limit error should raise RateLimitError."""
        client = AsyncHTTPClient(base_url="https://api.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.headers = {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-limit": "5000",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.request.return_value = mock_response

            async with client.session():
                with pytest.raises(RateLimitError):
                    await client.get("/test")

    @pytest.mark.asyncio
    async def test_client_error_no_retry(self):
        """4xx errors should not retry."""
        client = AsyncHTTPClient(base_url="https://api.example.com", max_retries=3)

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.request.return_value = mock_response

            async with client.session():
                with pytest.raises(HTTPError) as exc_info:
                    await client.get("/test")

            assert exc_info.value.status_code == 404
            # Should only be called once (no retries)
            assert mock_instance.request.call_count == 1

    @pytest.mark.asyncio
    async def test_server_error_retries(self):
        """5xx errors should retry."""
        client = AsyncHTTPClient(
            base_url="https://api.example.com",
            max_retries=3,
            retry_delay=0.01,  # Fast for tests
        )

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.request.return_value = mock_response

            async with client.session():
                with pytest.raises(HTTPError):
                    await client.get("/test")

            # Should retry 3 times
            assert mock_instance.request.call_count == 3


class TestGitHubClient:
    """Test GitHub API client."""

    def test_github_client_initialization(self):
        """GitHub client should set proper headers."""
        with patch("ccda_cli.core.http.get_config") as mock_config:
            mock_config.return_value.github.max_retries = 3
            mock_config.return_value.github.retry_delay_seconds = 1

            client = GitHubClient(token="test-token")
            assert client.base_url == "https://api.github.com"
            assert "Authorization" in client.headers
            assert client.headers["Authorization"] == "Bearer test-token"
            assert "X-GitHub-Api-Version" in client.headers

    def test_github_client_without_token(self):
        """GitHub client should work without token."""
        with patch("ccda_cli.core.http.get_config") as mock_config:
            mock_config.return_value.github.max_retries = 3
            mock_config.return_value.github.retry_delay_seconds = 1

            client = GitHubClient()
            assert "Authorization" not in client.headers

    @pytest.mark.asyncio
    async def test_get_repo(self):
        """get_repo should call correct endpoint."""
        with patch("ccda_cli.core.http.get_config") as mock_config:
            mock_config.return_value.github.max_retries = 3
            mock_config.return_value.github.retry_delay_seconds = 1
            mock_config.return_value.github.rate_limit_buffer = 100

            client = GitHubClient(token="test-token")

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"name": "express"}
            mock_response.headers = {"x-ratelimit-remaining": "4999"}

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.request.return_value = mock_response

                async with client.session():
                    response = await client.get_repo("expressjs", "express")

                assert response.data["name"] == "express"
                mock_instance.request.assert_called_once()
                call_args = mock_instance.request.call_args
                assert "/repos/expressjs/express" in str(call_args)

    def test_check_rate_limit(self):
        """check_rate_limit should compare against buffer."""
        with patch("ccda_cli.core.http.get_config") as mock_config:
            mock_config.return_value.github.max_retries = 3
            mock_config.return_value.github.retry_delay_seconds = 1
            mock_config.return_value.github.rate_limit_buffer = 100

            client = GitHubClient()
            client._rate_limit = RateLimitInfo(remaining=101)
            assert client.check_rate_limit() is True

            client._rate_limit = RateLimitInfo(remaining=99)
            assert client.check_rate_limit() is False


class TestDepsDevClient:
    """Test deps.dev API client."""

    def test_depsdev_client_initialization(self):
        """deps.dev client should set proper base URL."""
        client = DepsDevClient()
        assert client.base_url == "https://api.deps.dev"

    @pytest.mark.asyncio
    async def test_get_package_url_encoding(self):
        """Package names should be URL encoded."""
        client = DepsDevClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "@babel/core"}
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.request.return_value = mock_response

            async with client.session():
                await client.get_package("npm", "@babel/core")

            call_args = mock_instance.request.call_args
            # @ should be encoded as %40
            assert "%40babel%2Fcore" in str(call_args)


class TestClearlyDefinedClient:
    """Test ClearlyDefined API client."""

    def test_clearlydefined_client_initialization(self):
        """ClearlyDefined client should set proper base URL."""
        client = ClearlyDefinedClient()
        assert client.base_url == "https://api.clearlydefined.io"

    @pytest.mark.asyncio
    async def test_get_definition_path(self):
        """get_definition should construct correct path."""
        client = ClearlyDefinedClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"licensed": {"declared": "MIT"}}
        mock_response.headers = {}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.request.return_value = mock_response

            async with client.session():
                await client.get_definition("npm", "npmjs", "-", "lodash", "4.17.21")

            call_args = mock_instance.request.call_args
            assert "/definitions/npm/npmjs/-/lodash/4.17.21" in str(call_args)


class TestHTTPError:
    """Test HTTP error classes."""

    def test_http_error(self):
        """HTTPError should store status code and response."""
        error = HTTPError("Test error", status_code=500, response={"error": "details"})
        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response == {"error": "details"}

    def test_rate_limit_error(self):
        """RateLimitError should store reset time."""
        reset_time = datetime.now()
        error = RateLimitError(reset_at=reset_time)
        assert error.status_code == 403
        assert error.reset_at == reset_time
