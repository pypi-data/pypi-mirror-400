"""
Tests for integration module
"""
import asyncio
import threading
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from data_agent_tunnel_client.integration import (
    TunnelRunner,
    connect_tunnel,
    create_tunnel_lifespan,
    get_tunnel_client,
    _fastapi_tunnel_client,
)
from data_agent_tunnel_client.client import TunnelClient


class TestTunnelRunnerInit:
    """Tests for TunnelRunner initialization"""

    def test_init_with_required_params(self, tunnel_config):
        """Should initialize with required parameters"""
        runner = TunnelRunner(
            tunnel_url=tunnel_config["tunnel_url"],
            local_url=tunnel_config["local_url"],
        )

        assert runner.tunnel_url == tunnel_config["tunnel_url"]
        assert runner.local_url == tunnel_config["local_url"]
        assert runner.secret_key == ""
        assert runner._session_id == ""
        assert runner.home_path == "/"
        assert runner.disable_proxy is False

    def test_init_with_all_params(self, tunnel_config):
        """Should initialize with all parameters"""
        on_connect = MagicMock()
        on_disconnect = MagicMock()

        runner = TunnelRunner(
            tunnel_url=tunnel_config["tunnel_url"],
            local_url=tunnel_config["local_url"],
            secret_key=tunnel_config["secret_key"],
            session_id=tunnel_config["session_id"],
            home_path="/dashboard",
            disable_proxy=True,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            ping_interval=60.0,
        )

        assert runner.secret_key == tunnel_config["secret_key"]
        assert runner._session_id == tunnel_config["session_id"]
        assert runner.home_path == "/dashboard"
        assert runner.disable_proxy is True
        assert runner._user_on_connect == on_connect
        assert runner._user_on_disconnect == on_disconnect
        assert runner._client_kwargs == {"ping_interval": 60.0}


class TestTunnelRunnerProperties:
    """Tests for TunnelRunner properties"""

    def test_client_returns_none_before_start(self, tunnel_config):
        """Should return None before start"""
        runner = TunnelRunner(**tunnel_config)

        assert runner.client is None

    def test_public_url_returns_none_when_no_client(self, tunnel_config):
        """Should return None when client is None"""
        runner = TunnelRunner(**tunnel_config)

        assert runner.public_url is None

    def test_public_url_returns_client_public_url(self, tunnel_config):
        """Should return client's public_url when available"""
        runner = TunnelRunner(**tunnel_config)
        mock_client = MagicMock()
        mock_client.public_url = "https://public.example.com"
        runner._client = mock_client

        assert runner.public_url == "https://public.example.com"

    def test_connected_session_id_returns_none_when_no_client(self, tunnel_config):
        """Should return None when client is None"""
        runner = TunnelRunner(**tunnel_config)

        assert runner.connected_session_id is None

    def test_is_connected_returns_false_when_no_client(self, tunnel_config):
        """Should return False when client is None"""
        runner = TunnelRunner(**tunnel_config)

        assert runner.is_connected is False

    def test_is_connected_returns_client_status(self, tunnel_config):
        """Should return client's is_connected status"""
        runner = TunnelRunner(**tunnel_config)
        mock_client = MagicMock()
        mock_client.is_connected = True
        runner._client = mock_client

        assert runner.is_connected is True


class TestTunnelRunnerStart:
    """Tests for TunnelRunner start method"""

    def test_start_creates_daemon_thread(self, tunnel_config):
        """Should create daemon thread by default"""
        runner = TunnelRunner(**tunnel_config)

        with patch.object(runner, "_run_in_thread"):
            runner.start()

        assert runner._started is True
        assert runner._thread is not None
        assert runner._thread.daemon is True

    def test_start_can_create_non_daemon_thread(self, tunnel_config):
        """Should create non-daemon thread when specified"""
        runner = TunnelRunner(**tunnel_config)

        with patch.object(runner, "_run_in_thread"):
            runner.start(daemon=False)

        assert runner._thread.daemon is False

    def test_start_returns_self_for_chaining(self, tunnel_config):
        """Should return self for method chaining"""
        runner = TunnelRunner(**tunnel_config)

        with patch.object(runner, "_run_in_thread"):
            result = runner.start()

        assert result is runner

    def test_start_warns_if_already_started(self, tunnel_config):
        """Should warn if already started"""
        runner = TunnelRunner(**tunnel_config)
        runner._started = True

        with patch("data_agent_tunnel_client.integration.logger") as mock_logger:
            runner.start()

        mock_logger.warning.assert_called_once_with("TunnelRunner already started")

    def test_start_clears_proxy_when_disabled(self, tunnel_config):
        """Should clear proxy env when disable_proxy is True"""
        runner = TunnelRunner(**tunnel_config, disable_proxy=True)

        with patch("data_agent_tunnel_client.integration._clear_proxy_env") as mock_clear:
            with patch.object(runner, "_run_in_thread"):
                runner.start()

        mock_clear.assert_called_once()


class TestTunnelRunnerStop:
    """Tests for TunnelRunner stop method"""

    def test_stop_does_nothing_when_not_started(self, tunnel_config):
        """Should do nothing when not started"""
        runner = TunnelRunner(**tunnel_config)

        # Should not raise
        runner.stop()

    def test_stop_disconnects_client(self, tunnel_config):
        """Should call disconnect on client"""
        runner = TunnelRunner(**tunnel_config)
        runner._started = True

        mock_client = AsyncMock()
        runner._client = mock_client

        mock_loop = MagicMock()
        mock_loop.is_running.return_value = True
        runner._loop = mock_loop

        mock_future = MagicMock()
        mock_future.result.return_value = None

        with patch("asyncio.run_coroutine_threadsafe", return_value=mock_future):
            runner.stop()

        assert runner._started is False


class TestTunnelRunnerDefaultCallbacks:
    """Tests for TunnelRunner default callbacks"""

    def test_default_on_connect_prints_info(self, tunnel_config, capsys):
        """Should print connection info"""
        runner = TunnelRunner(**tunnel_config, home_path="/dashboard")

        mock_client = MagicMock()
        mock_client.public_url = "https://public.example.com?session=123&_tunnel_path="
        mock_client.connected_session_id = "session-123"

        runner._default_on_connect(mock_client)

        captured = capsys.readouterr()
        assert "Tunnel connected!" in captured.out
        assert "session-123" in captured.out
        assert "/dashboard" in captured.out

    def test_default_on_connect_with_root_home_path(self, tunnel_config, capsys):
        """Should not append home_path when it's root"""
        runner = TunnelRunner(**tunnel_config, home_path="/")

        mock_client = MagicMock()
        mock_client.public_url = "https://public.example.com"
        mock_client.connected_session_id = "session-123"

        runner._default_on_connect(mock_client)

        captured = capsys.readouterr()
        # Should not have double slash or extra path
        assert "https://public.example.com" in captured.out


class TestConnectTunnel:
    """Tests for connect_tunnel function"""

    def test_creates_and_starts_runner(self, tunnel_config):
        """Should create TunnelRunner and start it"""
        with patch.object(TunnelRunner, "start", return_value=MagicMock()) as mock_start:
            runner = connect_tunnel(**tunnel_config)

        mock_start.assert_called_once()
        assert isinstance(runner, TunnelRunner)

    def test_passes_home_path(self, tunnel_config):
        """Should pass home_path to runner"""
        with patch.object(TunnelRunner, "start", return_value=MagicMock()):
            runner = connect_tunnel(**tunnel_config, home_path="/custom")

        assert runner.home_path == "/custom"


class TestCreateTunnelLifespan:
    """Tests for create_tunnel_lifespan function"""

    def test_returns_context_manager(self, tunnel_config):
        """Should return a lifespan context manager"""
        lifespan = create_tunnel_lifespan(**tunnel_config)

        assert callable(lifespan)

    @pytest.mark.asyncio
    async def test_lifespan_creates_and_starts_client(self, tunnel_config, registered_response):
        """Should create client and start connection"""
        lifespan = create_tunnel_lifespan(**tunnel_config)

        mock_app = MagicMock()

        with patch("data_agent_tunnel_client.integration.TunnelClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.connect = AsyncMock()
            mock_instance.disconnect = AsyncMock()
            MockClient.return_value = mock_instance

            async with lifespan(mock_app):
                # Client should be created
                MockClient.assert_called_once()

            # Disconnect should be called on exit
            mock_instance.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_sets_global_client(self, tunnel_config):
        """Should set global _fastapi_tunnel_client"""
        import data_agent_tunnel_client.integration as integration

        lifespan = create_tunnel_lifespan(**tunnel_config)

        mock_app = MagicMock()

        with patch("data_agent_tunnel_client.integration.TunnelClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.connect = AsyncMock()
            mock_instance.disconnect = AsyncMock()
            MockClient.return_value = mock_instance

            async with lifespan(mock_app):
                assert integration._fastapi_tunnel_client is mock_instance

            # Should be cleared after exit
            assert integration._fastapi_tunnel_client is None


class TestGetTunnelClient:
    """Tests for get_tunnel_client function"""

    def test_returns_none_when_not_connected(self):
        """Should return None when no client is set"""
        import data_agent_tunnel_client.integration as integration
        integration._fastapi_tunnel_client = None

        assert get_tunnel_client() is None

    def test_returns_client_when_set(self):
        """Should return client when set"""
        import data_agent_tunnel_client.integration as integration

        mock_client = MagicMock()
        integration._fastapi_tunnel_client = mock_client

        try:
            assert get_tunnel_client() is mock_client
        finally:
            integration._fastapi_tunnel_client = None
