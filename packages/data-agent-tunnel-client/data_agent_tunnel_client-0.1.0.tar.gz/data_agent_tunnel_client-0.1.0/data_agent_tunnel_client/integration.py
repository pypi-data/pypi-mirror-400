"""
Flask/Web framework integration module

Provides a simple way to run TunnelClient in a background thread
"""
import asyncio
import logging
import threading
from typing import Optional, Callable
from urllib.parse import urljoin

from .client import TunnelClient, _clear_proxy_env

logger = logging.getLogger(__name__)


class TunnelRunner:
    """
    Tunnel client runner

    Runs TunnelClient in a background thread, suitable for integration with
    synchronous frameworks like Flask.

    Usage:
        runner = TunnelRunner(
            tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
            local_url="http://localhost:5000",
            secret_key="your-secret-key"
        )
        runner.start()  # Non-blocking, runs in background thread

        # Start Flask
        app.run(port=5000)
    """

    def __init__(
            self,
            tunnel_url: str,
            local_url: str,
            secret_key: str = "",
            session_id: str = "",
            home_path: str = "/",
            disable_proxy: bool = False,
            on_connect: Optional[Callable[[TunnelClient], None]] = None,
            on_disconnect: Optional[Callable[[TunnelClient], None]] = None,
            **kwargs
    ):
        """
        Initialize Tunnel runner

        Args:
            tunnel_url: Tunnel WebSocket URL
            local_url: Local service URL
            secret_key: Authentication key (optional)
            session_id: Specify session ID (optional)
            disable_proxy: Disable proxy environment variables (default False)
            on_connect: On connect callback (sync function)
            on_disconnect: On disconnect callback (sync function)
            **kwargs: Additional arguments for TunnelClient
        """
        self.tunnel_url = tunnel_url
        self.local_url = local_url
        self.secret_key = secret_key
        self._session_id = session_id
        self.home_path = home_path
        self.disable_proxy = disable_proxy
        self._user_on_connect = on_connect
        self._user_on_disconnect = on_disconnect
        self._client_kwargs = kwargs

        self._client: Optional[TunnelClient] = None
        self._thread: Optional[threading.Thread] = None
        self._started = False

    @property
    def client(self) -> Optional[TunnelClient]:
        """Get TunnelClient instance"""
        return self._client

    @property
    def public_url(self) -> Optional[str]:
        """Get public URL"""
        return self._client.public_url if self._client else None

    @property
    def connected_session_id(self) -> Optional[str]:
        """Get current connected session ID"""
        return self._client.connected_session_id if self._client else None

    @property
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._client.is_connected if self._client else False

    def start(self, daemon: bool = True) -> "TunnelRunner":
        """
        Start Tunnel client (non-blocking)

        Args:
            daemon: Run as daemon thread (default True)

        Returns:
            self, supports method chaining
        """
        if self._started:
            logger.warning("TunnelRunner already started")
            return self

        if self.disable_proxy:
            _clear_proxy_env()

        self._thread = threading.Thread(
            target=self._run_in_thread,
            daemon=daemon
        )
        self._thread.start()
        self._started = True

        return self

    def _run_in_thread(self):
        """Run async client in thread"""
        asyncio.run(self._async_run())

    async def _async_run(self):
        """Async run logic"""

        # Wrap user callbacks as async functions
        async def on_connect(client: TunnelClient):
            self._default_on_connect(client)
            if self._user_on_connect:
                self._user_on_connect(client)

        async def on_disconnect(client: TunnelClient):
            self._default_on_disconnect(client)
            if self._user_on_disconnect:
                self._user_on_disconnect(client)

        self._client = TunnelClient(
            tunnel_url=self.tunnel_url,
            local_url=self.local_url,
            secret_key=self.secret_key,
            session_id=self._session_id,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            **self._client_kwargs
        )

        await self._client.connect()

    def _default_on_connect(self, client: TunnelClient):
        """Default on_connect callback"""
        public_url = client.public_url or ""
        if self.home_path and self.home_path != "/":
            public_url = urljoin(public_url + "/", self.home_path.lstrip("/"))
        print()
        print("=" * 60)
        print("Tunnel connected!")
        print(f"  Session ID: {client.connected_session_id}")
        print(f"  Public URL: {public_url}")
        print("=" * 60)
        print()

    def _default_on_disconnect(self, client: TunnelClient):
        """Default on_disconnect callback"""
        logger.warning("Tunnel disconnected, reconnecting...")


def connect_tunnel(
        tunnel_url: str,
        local_url: str,
        secret_key: str = "",
        session_id: str = "",
        home_path: str = "",
        **kwargs
) -> TunnelRunner:
    """
    Quick start Tunnel client (non-blocking)

    The simplest way to connect - just one line of code.

    Usage:
        from data_agent_tunnel_client import connect_tunnel

        # Start Tunnel (runs in background)
        runner = connect_tunnel(
            tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
            local_url="http://localhost:5000",
            secret_key="your-secret-key"
        )

        # Start your web service
        app.run(port=5000)

    Args:
        tunnel_url: Tunnel WebSocket URL
        local_url: Local service URL
        secret_key: Authentication key (optional)
        session_id: Specify session ID (optional)
        home_path: Home path after tunnel connection
        **kwargs: Additional arguments for TunnelRunner

    Returns:
        TunnelRunner instance
    """
    runner = TunnelRunner(
        tunnel_url=tunnel_url,
        local_url=local_url,
        secret_key=secret_key,
        session_id=session_id,
        home_path=home_path,
        **kwargs
    )
    runner.start()
    return runner
