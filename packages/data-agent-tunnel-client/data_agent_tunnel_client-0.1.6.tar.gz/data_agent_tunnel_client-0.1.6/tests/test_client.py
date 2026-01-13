"""
Tests for client module
"""
import asyncio
import base64
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from data_agent_tunnel_client.client import (
    TunnelClient,
    run_tunnel,
    _has_proxy_env,
    _clear_proxy_env,
    PROXY_ENV_KEYS,
)


class TestProxyEnvHelpers:
    """Tests for proxy environment variable helpers"""

    def test_has_proxy_env_returns_false_when_no_proxy(self):
        """Should return False when no proxy env vars are set"""
        # Clear all proxy env vars
        for key in PROXY_ENV_KEYS:
            os.environ.pop(key, None)

        assert _has_proxy_env() is False

    def test_has_proxy_env_returns_true_when_http_proxy_set(self):
        """Should return True when http_proxy is set"""
        os.environ["http_proxy"] = "http://proxy:8080"
        try:
            assert _has_proxy_env() is True
        finally:
            os.environ.pop("http_proxy", None)

    def test_has_proxy_env_returns_true_when_https_proxy_set(self):
        """Should return True when HTTPS_PROXY is set"""
        os.environ["HTTPS_PROXY"] = "http://proxy:8080"
        try:
            assert _has_proxy_env() is True
        finally:
            os.environ.pop("HTTPS_PROXY", None)

    def test_clear_proxy_env_removes_all_proxy_vars(self):
        """Should remove all proxy environment variables"""
        # Set some proxy vars
        os.environ["http_proxy"] = "http://proxy:8080"
        os.environ["HTTPS_PROXY"] = "http://proxy:8080"

        _clear_proxy_env()

        for key in PROXY_ENV_KEYS:
            assert key not in os.environ


class TestTunnelClientInit:
    """Tests for TunnelClient initialization"""

    def test_init_with_required_params(self, tunnel_config):
        """Should initialize with required parameters"""
        client = TunnelClient(
            tunnel_url=tunnel_config["tunnel_url"],
            local_url=tunnel_config["local_url"],
        )

        assert client.tunnel_url == tunnel_config["tunnel_url"]
        assert client.local_url == tunnel_config["local_url"]
        assert client.secret_key == ""
        assert client.session_id == ""
        assert client.reconnect is True

    def test_init_with_all_params(self, tunnel_config):
        """Should initialize with all parameters"""
        client = TunnelClient(
            tunnel_url=tunnel_config["tunnel_url"],
            local_url=tunnel_config["local_url"],
            secret_key=tunnel_config["secret_key"],
            session_id=tunnel_config["session_id"],
            reconnect=False,
            reconnect_interval=2.0,
            max_reconnect_interval=120.0,
            ping_interval=60.0,
            request_timeout=600.0,
            max_concurrent_requests=50,
        )

        assert client.secret_key == tunnel_config["secret_key"]
        assert client.session_id == tunnel_config["session_id"]
        assert client.reconnect is False
        assert client.reconnect_interval == 2.0
        assert client.max_reconnect_interval == 120.0
        assert client.ping_interval == 60.0
        assert client.request_timeout == 600.0
        assert client.max_concurrent_requests == 50

    def test_init_strips_trailing_slash_from_local_url(self):
        """Should strip trailing slash from local_url"""
        client = TunnelClient(
            tunnel_url="wss://test.com/ws",
            local_url="http://localhost:5000/",
        )

        assert client.local_url == "http://localhost:5000"

    def test_default_values(self, tunnel_config):
        """Should have correct default values"""
        client = TunnelClient(
            tunnel_url=tunnel_config["tunnel_url"],
            local_url=tunnel_config["local_url"],
        )

        assert client.reconnect_interval == 1.0
        assert client.max_reconnect_interval == 60.0
        assert client.ping_interval == 30.0
        assert client.request_timeout == 300.0
        assert client.max_concurrent_requests == 100


class TestTunnelClientProperties:
    """Tests for TunnelClient properties"""

    def test_public_url_returns_none_when_not_connected(self, tunnel_config):
        """Should return None when not connected"""
        client = TunnelClient(**tunnel_config)

        assert client.public_url is None

    def test_connected_session_id_returns_none_when_not_connected(self, tunnel_config):
        """Should return None when not connected"""
        client = TunnelClient(**tunnel_config)

        assert client.connected_session_id is None

    def test_is_connected_returns_false_when_ws_is_none(self, tunnel_config):
        """Should return False when WebSocket is None"""
        client = TunnelClient(**tunnel_config)

        assert client.is_connected is False

    def test_is_connected_returns_false_when_ws_not_open(self, tunnel_config, mock_websocket):
        """Should return False when WebSocket is not open"""
        client = TunnelClient(**tunnel_config)
        mock_websocket.open = False
        client._ws = mock_websocket

        assert client.is_connected is False

    def test_is_connected_returns_true_when_ws_open(self, tunnel_config, mock_websocket):
        """Should return True when WebSocket is open"""
        client = TunnelClient(**tunnel_config)
        mock_websocket.open = True
        client._ws = mock_websocket

        assert client.is_connected is True


class TestTunnelClientRegister:
    """Tests for TunnelClient registration"""

    @pytest.mark.asyncio
    async def test_register_sends_correct_message(self, tunnel_config, mock_websocket):
        """Should send correct registration message"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket

        with patch("data_agent_tunnel_client.client.create_auth_params") as mock_auth:
            mock_auth.return_value = {
                "timestamp": "1234567890",
                "signature": "test-sig",
            }
            await client._register()

        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])

        assert sent_data["type"] == "register"
        assert sent_data["sessionId"] == tunnel_config["session_id"]
        assert sent_data["timestamp"] == "1234567890"
        assert sent_data["signature"] == "test-sig"

    @pytest.mark.asyncio
    async def test_register_uses_connected_session_id_for_reconnect(
        self, tunnel_config, mock_websocket
    ):
        """Should use connected session ID for reconnection"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._connected_session_id = "reconnect-session-456"

        with patch("data_agent_tunnel_client.client.create_auth_params") as mock_auth:
            mock_auth.return_value = {"timestamp": "123", "signature": "sig"}
            await client._register()

        sent_data = json.loads(mock_websocket.send.call_args[0][0])

        assert sent_data["sessionId"] == "reconnect-session-456"


class TestTunnelClientMessageLoop:
    """Tests for TunnelClient message loop"""

    @pytest.mark.asyncio
    async def test_handles_ping_message(self, tunnel_config, mock_websocket):
        """Should respond to ping with pong"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket

        # Simulate ping message then stop
        mock_websocket.__aiter__ = lambda self: self
        mock_websocket.__anext__ = AsyncMock(
            side_effect=[json.dumps({"type": "ping"}), StopAsyncIteration]
        )

        await client._message_loop()

        # Verify pong was sent
        mock_websocket.send.assert_called_with(json.dumps({"type": "pong"}))

    @pytest.mark.asyncio
    async def test_handles_shutdown_message(self, tunnel_config, mock_websocket, shutdown_response):
        """Should handle shutdown message and reset reconnect delay"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._current_reconnect_delay = 30.0  # Simulating backoff state

        mock_websocket.__aiter__ = lambda self: self
        mock_websocket.__anext__ = AsyncMock(
            side_effect=[json.dumps(shutdown_response), StopAsyncIteration]
        )

        await client._message_loop()

        # Verify reconnect delay was reset
        assert client._current_reconnect_delay == client.reconnect_interval

    @pytest.mark.asyncio
    async def test_handles_proxy_request(self, tunnel_config, mock_websocket, proxy_request):
        """Should create task for proxy request"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._semaphore = asyncio.Semaphore(100)

        mock_websocket.__aiter__ = lambda self: self
        mock_websocket.__anext__ = AsyncMock(
            side_effect=[json.dumps(proxy_request), StopAsyncIteration]
        )

        with patch.object(client, "_handle_request", new_callable=AsyncMock) as mock_handle:
            await client._message_loop()
            # Give time for task to be created
            await asyncio.sleep(0.01)

            mock_handle.assert_called_once_with(proxy_request)


class TestTunnelClientHandleRequest:
    """Tests for TunnelClient request handling"""

    @pytest.mark.asyncio
    async def test_handles_get_request(self, tunnel_config, mock_websocket, proxy_request):
        """Should handle GET request correctly"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._semaphore = asyncio.Semaphore(100)

        # Mock HTTP session
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.read = AsyncMock(return_value=b'{"result": "ok"}')

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=None),
        ))
        client._http_session = mock_session

        await client._do_handle_request(proxy_request)

        # Verify response was sent
        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])

        assert sent_data["id"] == "req-123"
        assert sent_data["status"] == 200
        assert sent_data["body"] == list(b'{"result": "ok"}')

    @pytest.mark.asyncio
    async def test_handles_post_request_with_body(self, tunnel_config, mock_websocket):
        """Should handle POST request with body"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._semaphore = asyncio.Semaphore(100)

        # Request with base64 encoded body
        request = {
            "id": "req-456",
            "method": "POST",
            "path": "/api/data",
            "query": "",
            "headers": {"Content-Type": ["application/json"]},
            "body": base64.b64encode(b'{"name": "test"}').decode(),
        }

        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.headers = {}
        mock_response.read = AsyncMock(return_value=b"created")

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock(return_value=None),
        ))
        client._http_session = mock_session

        await client._do_handle_request(request)

        # Verify request was made with decoded body
        call_kwargs = mock_session.request.call_args[1]
        assert call_kwargs["data"] == b'{"name": "test"}'

    @pytest.mark.asyncio
    async def test_returns_502_on_client_error(self, tunnel_config, mock_websocket, proxy_request):
        """Should return 502 on client error"""
        import aiohttp

        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._semaphore = asyncio.Semaphore(100)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(side_effect=aiohttp.ClientError("Connection failed"))
        client._http_session = mock_session

        await client._do_handle_request(proxy_request)

        sent_data = json.loads(mock_websocket.send.call_args[0][0])

        assert sent_data["status"] == 502
        assert b"Bad Gateway" in bytes(sent_data["body"])

    @pytest.mark.asyncio
    async def test_returns_500_on_unexpected_error(self, tunnel_config, mock_websocket, proxy_request):
        """Should return 500 on unexpected error"""
        client = TunnelClient(**tunnel_config)
        client._ws = mock_websocket
        client._semaphore = asyncio.Semaphore(100)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(side_effect=Exception("Unexpected error"))
        client._http_session = mock_session

        await client._do_handle_request(proxy_request)

        sent_data = json.loads(mock_websocket.send.call_args[0][0])

        assert sent_data["status"] == 500
        assert b"Internal Server Error" in bytes(sent_data["body"])


class TestTunnelClientReconnect:
    """Tests for TunnelClient reconnection with backoff"""

    @pytest.mark.asyncio
    async def test_reconnect_with_backoff_doubles_delay(self, tunnel_config):
        """Should double the delay on each reconnect"""
        client = TunnelClient(**tunnel_config)
        client._current_reconnect_delay = 1.0

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await client._reconnect_with_backoff()

        mock_sleep.assert_called_once_with(1.0)
        assert client._current_reconnect_delay == 2.0

    @pytest.mark.asyncio
    async def test_reconnect_with_backoff_caps_at_max(self, tunnel_config):
        """Should cap delay at max_reconnect_interval"""
        client = TunnelClient(**tunnel_config)
        client._current_reconnect_delay = 50.0

        with patch("asyncio.sleep", new_callable=AsyncMock):
            await client._reconnect_with_backoff()

        assert client._current_reconnect_delay == 60.0  # Capped at max

    @pytest.mark.asyncio
    async def test_exponential_backoff_sequence(self, tunnel_config):
        """Should follow exponential backoff sequence"""
        client = TunnelClient(**tunnel_config)
        client._current_reconnect_delay = 1.0

        delays = []
        with patch("asyncio.sleep", new_callable=AsyncMock):
            for _ in range(7):
                delays.append(client._current_reconnect_delay)
                await client._reconnect_with_backoff()

        # 1, 2, 4, 8, 16, 32, 60 (capped)
        assert delays == [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 60.0]


class TestTunnelClientCleanup:
    """Tests for TunnelClient cleanup"""

    @pytest.mark.asyncio
    async def test_cleanup_closes_http_session(self, tunnel_config):
        """Should close HTTP session on cleanup"""
        client = TunnelClient(**tunnel_config)
        mock_session = AsyncMock()
        client._http_session = mock_session
        client._public_url = "https://test.com"
        client._connected_session_id = "session-123"

        await client._cleanup()

        mock_session.close.assert_called_once()
        assert client._http_session is None
        assert client._ws is None
        assert client._public_url is None
        assert client._connected_session_id is None


class TestRunTunnel:
    """Tests for run_tunnel function"""

    def test_creates_client_and_runs(self, tunnel_config):
        """Should create TunnelClient and run connect"""
        with patch("data_agent_tunnel_client.client.TunnelClient") as MockClient:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            MockClient.return_value = mock_instance

            with patch("asyncio.run") as mock_run:
                run_tunnel(**tunnel_config)

            MockClient.assert_called_once_with(
                tunnel_url=tunnel_config["tunnel_url"],
                local_url=tunnel_config["local_url"],
                secret_key=tunnel_config["secret_key"],
                session_id=tunnel_config["session_id"],
            )
            mock_run.assert_called_once()