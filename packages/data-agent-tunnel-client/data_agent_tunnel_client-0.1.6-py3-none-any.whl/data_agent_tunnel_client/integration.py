"""
Web framework integration module

Provides simple ways to integrate TunnelClient with various frameworks:
- Flask/Django: TunnelRunner, connect_tunnel()
- FastAPI: create_tunnel_lifespan()
"""
import asyncio
import logging
import threading
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import Optional, Callable, Any, AsyncIterator, TypeVar

# Type variable for FastAPI app
AppType = TypeVar("AppType")

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
        self._loop: Optional[asyncio.AbstractEventLoop] = None
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

    def stop(self):
        """
        Stop the tunnel client gracefully.

        This method can be called from the main thread to stop the background tunnel.
        """
        if not self._started or not self._client:
            return

        if self._loop and self._loop.is_running():
            # Schedule disconnect in the background thread's event loop
            future = asyncio.run_coroutine_threadsafe(
                self._client.disconnect(),
                self._loop
            )
            try:
                future.result(timeout=5.0)  # Wait up to 5 seconds
            except Exception as e:
                logger.warning(f"Error stopping tunnel: {e}")

        self._started = False

    def _run_in_thread(self):
        """Run async client in thread"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._async_run())
        finally:
            self._loop.close()
            self._loop = None

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
            # Append home_path to the end of URL (for URLs like http://xxx?session=123&path=)
            public_url = public_url + "/" + self.home_path.lstrip("/")
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
        home_path: str = "/",
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


# Store tunnel client for FastAPI lifespan
_fastapi_tunnel_client: Optional[TunnelClient] = None


def create_tunnel_lifespan(
        tunnel_url: str,
        local_url: str,
        secret_key: str = "",
        session_id: str = "",
        home_path: str = "/",
        on_connect: Optional[Callable[[TunnelClient], Any]] = None,
        on_disconnect: Optional[Callable[[TunnelClient], Any]] = None,
        **kwargs
) -> Callable[[AppType], AbstractAsyncContextManager[None]]:
    """
    Create a lifespan context manager for FastAPI integration.

    Usage:
        from fastapi import FastAPI
        from data_agent_tunnel_client import create_tunnel_lifespan

        app = FastAPI(lifespan=create_tunnel_lifespan(
            tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
            local_url="http://localhost:8000",
            secret_key="your-secret-key",
            home_path="/dashboard",
        ))

        @app.get("/")
        async def root():
            return {"message": "Hello from FastAPI!"}

    Args:
        tunnel_url: Tunnel WebSocket URL
        local_url: Local service URL
        secret_key: Authentication key (optional)
        session_id: Specify session ID (optional)
        home_path: Home path for display (optional)
        on_connect: On connect callback (async or sync function)
        on_disconnect: On disconnect callback (async or sync function)
        **kwargs: Additional arguments for TunnelClient

    Returns:
        A lifespan context manager function for FastAPI
    """

    @asynccontextmanager
    async def lifespan(app: Any) -> AsyncIterator[None]:
        global _fastapi_tunnel_client

        # Build public URL with home_path for display
        def get_display_url(client: TunnelClient) -> str:
            public_url = client.public_url or ""
            if home_path and home_path != "/":
                # Append home_path to the end of URL (for URLs like http://xxx?session=123&path=)
                # Ensure home_path starts with /
                return public_url + "/" + home_path.lstrip("/")
            return public_url

        # Default on_connect handler
        async def default_on_connect(client: TunnelClient):
            print()
            print("=" * 60)
            print("Tunnel connected!")
            print(f"  Session ID: {client.connected_session_id}")
            print(f"  Public URL: {get_display_url(client)}")
            print("=" * 60)
            print()

            if on_connect:
                result = on_connect(client)
                if asyncio.iscoroutine(result):
                    await result

        # Default on_disconnect handler
        async def default_on_disconnect(client: TunnelClient):
            logger.warning("Tunnel disconnected, reconnecting...")

            if on_disconnect:
                result = on_disconnect(client)
                if asyncio.iscoroutine(result):
                    await result

        _fastapi_tunnel_client = TunnelClient(
            tunnel_url=tunnel_url,
            local_url=local_url,
            secret_key=secret_key,
            session_id=session_id,
            on_connect=default_on_connect,
            on_disconnect=default_on_disconnect,
            **kwargs
        )

        # Start tunnel in background
        task = asyncio.create_task(_fastapi_tunnel_client.connect())

        yield

        # Cleanup
        await _fastapi_tunnel_client.disconnect()
        task.cancel()
        _fastapi_tunnel_client = None

    return lifespan


def get_tunnel_client() -> Optional[TunnelClient]:
    """
    Get the current FastAPI tunnel client instance.

    Usage:
        from data_agent_tunnel_client import get_tunnel_client

        @app.get("/tunnel-info")
        async def tunnel_info():
            client = get_tunnel_client()
            return {
                "public_url": client.public_url if client else None,
                "is_connected": client.is_connected if client else False
            }

    Returns:
        TunnelClient instance or None if not connected
    """
    return _fastapi_tunnel_client
