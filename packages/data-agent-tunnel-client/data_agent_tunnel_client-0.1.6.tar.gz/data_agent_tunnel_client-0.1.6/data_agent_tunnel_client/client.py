import asyncio
import base64
import json
import logging
import os
from typing import Optional, Callable, Awaitable, Any

import aiohttp
import websockets

from .auth import create_auth_params

logger = logging.getLogger(__name__)


PROXY_ENV_KEYS = [
    "http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
    "all_proxy", "ALL_PROXY", "socks_proxy", "SOCKS_PROXY"
]


def _has_proxy_env() -> bool:
    """Check if proxy environment variables are set"""
    return any(os.environ.get(key) for key in PROXY_ENV_KEYS)


def _clear_proxy_env():
    """Clear proxy environment variables"""
    for key in PROXY_ENV_KEYS:
        os.environ.pop(key, None)


class TunnelClient:
    """
    Data Agent Tunnel Client

    Transparently proxies local web services to the Tunnel server.

    Usage:
        client = TunnelClient(
            tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
            local_url="http://localhost:5000",
            secret_key="your-secret-key"  # optional
        )
        await client.connect()
    """

    def __init__(
        self,
        tunnel_url: str,
        local_url: str,
        secret_key: str = "",
        session_id: str = "",
        reconnect: bool = True,
        reconnect_interval: float = 1.0,
        max_reconnect_interval: float = 60.0,
        ping_interval: float = 30.0,
        request_timeout: float = 300.0,
        max_concurrent_requests: int = 100,
        on_connect: Optional[Callable[["TunnelClient"], Awaitable[None]]] = None,
        on_disconnect: Optional[Callable[["TunnelClient"], Awaitable[None]]] = None,
    ):
        """
        Initialize Tunnel client

        Args:
            tunnel_url: Tunnel WebSocket URL, e.g. wss://dataagent.eigenai.com/_tunnel/ws
            local_url: Local service URL, e.g. http://localhost:5000
            secret_key: Authentication key (optional, skip auth if empty)
            session_id: Specify session ID (optional, server generates if empty)
            reconnect: Auto reconnect on disconnect
            reconnect_interval: Initial reconnect interval (seconds), default 1
            max_reconnect_interval: Max reconnect interval for exponential backoff (seconds), default 60
            ping_interval: Heartbeat interval (seconds)
            request_timeout: Local service request timeout (seconds), default 300
            max_concurrent_requests: Max concurrent requests, default 100
            on_connect: On connect callback
            on_disconnect: On disconnect callback
        """
        self.tunnel_url = tunnel_url
        self.local_url = local_url.rstrip("/")
        self.secret_key = secret_key
        self.session_id = session_id
        self.reconnect = reconnect
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_interval = max_reconnect_interval
        self.ping_interval = ping_interval
        self.request_timeout = request_timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

        self._ws: Optional[Any] = None
        self._http_session: Optional[aiohttp.ClientSession] = None
        self._running = False
        self._public_url: Optional[str] = None
        self._connected_session_id: Optional[str] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._current_reconnect_delay: float = reconnect_interval

    @property
    def public_url(self) -> Optional[str]:
        """Get public URL"""
        return self._public_url

    @property
    def connected_session_id(self) -> Optional[str]:
        """Get current session ID"""
        return self._connected_session_id

    @property
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._ws is not None and self._ws.open

    async def connect(self):
        """Connect to Tunnel server and start proxying"""
        self._running = True
        self._http_session = aiohttp.ClientSession()
        self._semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        self._current_reconnect_delay = self.reconnect_interval

        try:
            while self._running:
                try:
                    await self._connect_and_run()
                    # Reset delay on successful connection
                    self._current_reconnect_delay = self.reconnect_interval
                except (websockets.ConnectionClosed, ConnectionError, OSError) as e:
                    logger.warning(f"Connection closed: {e}")
                    if self.on_disconnect:
                        await self.on_disconnect(self)

                    if not self._running or not self.reconnect:
                        break

                    await self._reconnect_with_backoff()
                except Exception as e:
                    logger.error(f"Error occurred: {e}")
                    if not self._running or not self.reconnect:
                        break
                    await self._reconnect_with_backoff()
        finally:
            await self._cleanup()

    async def _reconnect_with_backoff(self):
        """Wait before reconnecting with exponential backoff"""
        logger.info(f"Reconnecting in {self._current_reconnect_delay:.1f} seconds...")
        await asyncio.sleep(self._current_reconnect_delay)
        # Exponential backoff: double the delay, but cap at max
        self._current_reconnect_delay = min(
            self._current_reconnect_delay * 2,
            self.max_reconnect_interval
        )

    async def disconnect(self):
        """Disconnect from server"""
        self._running = False
        if self._ws:
            await self._ws.close()

    async def _connect_and_run(self):
        """Establish connection and run message loop with auto proxy fallback"""
        ws = await self._try_connect()
        self._ws = ws

        try:
            # Send registration message
            await self._register()

            # Wait for registration response
            response = await ws.recv()
            data = json.loads(response)

            # Handle error response
            if data.get("type") == "error":
                reason = data.get("reason", "Unknown error")
                if "signature" in reason.lower() or "timestamp" in reason.lower():
                    logger.error(
                        f"Authentication failed: {reason}\n"
                        "  Please check:\n"
                        "  1. secret_key is correct\n"
                        "  2. System clock is synchronized (signature expires in 60 minutes)"
                    )
                else:
                    logger.error(f"Registration failed: {reason}")
                raise Exception(f"Registration failed: {reason}")

            if data.get("type") != "registered":
                raise Exception(f"Registration failed: {data}")

            self._connected_session_id = data.get("sessionId")
            self._public_url = data.get("publicUrl")

            logger.info("Registration successful!")
            logger.info(f"  Session ID: {self._connected_session_id}")

            if self.on_connect:
                await self.on_connect(self)

            # Message processing loop
            await self._message_loop()
        finally:
            await ws.close()

    async def _try_connect(self):
        """
        Try to connect with auto proxy fallback

        1. If proxy is set, try connecting via proxy first
        2. If proxy connection fails, fallback to direct connection
        3. If no proxy, connect directly
        """
        has_proxy = _has_proxy_env()
        connect_timeout = 10  # Connection timeout

        if has_proxy:
            # Try connecting via proxy first
            logger.info(f"Connecting via proxy to {self.tunnel_url}...")
            try:
                ws = await asyncio.wait_for(
                    websockets.connect(
                        self.tunnel_url,
                        ping_interval=self.ping_interval,
                        ping_timeout=self.ping_interval * 2,
                    ),
                    timeout=connect_timeout
                )
                logger.info("Connected via proxy successfully")
                return ws
            except Exception as e:
                logger.warning(f"Proxy connection failed: {e}")
                logger.info("Retrying with direct connection...")
                # Clear proxy environment variables
                _clear_proxy_env()

        # Direct connection (no proxy)
        logger.info(f"Connecting to {self.tunnel_url}...")
        ws = await websockets.connect(
            self.tunnel_url,
            ping_interval=self.ping_interval,
            ping_timeout=self.ping_interval * 2,
        )
        return ws

    async def _register(self):
        """Send registration message"""
        auth_params = create_auth_params(self.secret_key)

        # Use connected session ID for reconnection to maintain the same session
        session_id = self._connected_session_id or self.session_id

        register_msg = {
            "type": "register",
            "sessionId": session_id,
            **auth_params
        }

        await self._ws.send(json.dumps(register_msg))

    async def _message_loop(self):
        """Message processing loop"""
        async for message in self._ws:
            try:
                data = json.loads(message)

                msg_type = data.get("type")

                # Handle Ping
                if msg_type == "ping":
                    await self._ws.send(json.dumps({"type": "pong"}))
                    continue

                # Handle shutdown signal (graceful server shutdown)
                if msg_type == "shutdown":
                    reason = data.get("reason", "server is shutting down")
                    logger.info(f"Server shutdown signal received: {reason}")
                    logger.info("Will reconnect shortly...")
                    # Reset reconnect delay for immediate reconnect after server restart
                    self._current_reconnect_delay = self.reconnect_interval
                    continue

                # Handle proxy request
                if "id" in data and "method" in data:
                    asyncio.create_task(self._handle_request(data))

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON message: {message}")
            except Exception as e:
                logger.error(f"Failed to process message: {e}")

    async def _handle_request(self, request: dict):
        """Handle proxy request"""
        async with self._semaphore:  # Concurrency limit
            await self._do_handle_request(request)

    async def _do_handle_request(self, request: dict):
        """Actually handle proxy request"""
        request_id = request["id"]
        method = request["method"]
        path = request.get("path", "/")
        query = request.get("query", "")
        headers = request.get("headers", {})
        body = request.get("body")

        # Build local URL
        url = f"{self.local_url}{path}"
        if query:
            url = f"{url}?{query}"

        logger.debug(f"Proxying request: {method} {url}")

        try:
            # Handle body (Go's []byte is JSON serialized as base64 string)
            if body:
                if isinstance(body, str):
                    body = base64.b64decode(body)
                elif isinstance(body, list):
                    body = bytes(body)

            # Clean headers
            clean_headers = {}
            skip_headers = {"host", "content-length", "transfer-encoding"}
            for k, v in headers.items():
                if k.lower() not in skip_headers:
                    clean_headers[k] = v[0] if isinstance(v, list) else v

            # Send request to local service
            async with self._http_session.request(
                method=method,
                url=url,
                headers=clean_headers,
                data=body,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=self.request_timeout)
            ) as resp:
                response_body = await resp.read()
                response_headers = {k: [v] for k, v in resp.headers.items()}

                response = {
                    "id": request_id,
                    "status": resp.status,
                    "headers": response_headers,
                    "body": list(response_body)  # Convert to JSON serializable list
                }

        except aiohttp.ClientError as e:
            logger.error(f"Failed to request local service: {e}")
            response = {
                "id": request_id,
                "status": 502,
                "headers": {"Content-Type": ["text/plain"]},
                "body": list(f"Bad Gateway: {e}".encode())
            }
        except Exception as e:
            logger.error(f"Failed to handle request: {e}")
            response = {
                "id": request_id,
                "status": 500,
                "headers": {"Content-Type": ["text/plain"]},
                "body": list(f"Internal Server Error: {e}".encode())
            }

        # Send response
        try:
            await self._ws.send(json.dumps(response))
        except Exception as e:
            logger.error(f"Failed to send response: {e}")

    async def _cleanup(self):
        """Clean up resources"""
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
        self._ws = None
        self._public_url = None
        self._connected_session_id = None


def run_tunnel(
    tunnel_url: str,
    local_url: str,
    secret_key: str = "",
    session_id: str = "",
    **kwargs
):
    """
    Run Tunnel client (synchronous interface)

    Usage:
        from data_agent_tunnel_client import run_tunnel

        run_tunnel(
            tunnel_url="wss://data.eigenai.com/_tunnel/ws",
            local_url="http://localhost:5000"
        )
    """
    client = TunnelClient(
        tunnel_url=tunnel_url,
        local_url=local_url,
        secret_key=secret_key,
        session_id=session_id,
        **kwargs
    )

    try:
        asyncio.run(client.connect())
    except KeyboardInterrupt:
        logger.info("Interrupt received, disconnecting...")
