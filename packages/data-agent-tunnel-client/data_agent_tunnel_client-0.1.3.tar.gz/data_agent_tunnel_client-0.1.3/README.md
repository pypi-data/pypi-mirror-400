# Data Agent Tunnel Client

Proxy local web services to the public network through Data Agent Tunnel.

## Installation

```bash
pip install data-agent-tunnel-client

# or with uv
uv add data-agent-tunnel-client
```

## Quick Start

### Option 1: Simple Integration (Recommended)

The easiest way to connect - runs in a background thread, perfect for Flask/Django:

```python
from flask import Flask
from data_agent_tunnel_client import connect_tunnel

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask!"

if __name__ == "__main__":
    # Start tunnel in background
    connect_tunnel(
        tunnel_url="wss://...",
        local_url="http://localhost:5000",
        secret_key="your-secret-key",  # optional
        home_path="/initial_path",     # optional
    )

    # Start Flask
    app.run(port=5000)
```


### Option 2: FastAPI Integration

For FastAPI, use `create_tunnel_lifespan()`:

```python
from fastapi import FastAPI
from data_agent_tunnel_client import create_tunnel_lifespan, get_tunnel_client

lifespan=create_tunnel_lifespan(
    tunnel_url="wss://...",
    local_url="http://localhost:8000",
    secret_key="your-secret-key",  # optional
    home_path="/dashboard",        # optional
)

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/tunnel-info")
async def tunnel_info():
    client = get_tunnel_client()
    return {"public_url": client.public_url if client else None}
```

## API Reference

### connect_tunnel()

Quick start function for synchronous frameworks:

```python
from data_agent_tunnel_client import connect_tunnel

runner = connect_tunnel(
    tunnel_url="wss://...",      # Tunnel WebSocket URL
    local_url="http://...",      # Local service URL
    secret_key="",               # Auth key (optional)
    home_path="/dashboard",      # Initial path appended to public URL (optional)
)

# Access connection info
print(runner.public_url)
print(runner.connected_session_id)
print(runner.is_connected)
```

**home_path parameter:**

The `home_path` parameter specifies the initial path to display after tunnel connection. This is useful when your app's entry point is not the root path.

```python
# Example: If public_url is https://xxx.com?session=abc123&_tunnel_path=,
# With home_path="/dashboard", the displayed URL will be:
# https://xxx.com?session=abc123&_tunnel_path=/dashboard
```

### create_tunnel_lifespan()

Create a lifespan context manager for FastAPI:

```python
from data_agent_tunnel_client import create_tunnel_lifespan

lifespan = create_tunnel_lifespan(
    tunnel_url="wss://...",      # Tunnel WebSocket URL
    local_url="http://...",      # Local service URL
    secret_key="",               # Auth key (optional)
    home_path="/",               # Home path for display (optional)
    on_connect=None,             # Connect callback (async or sync)
    on_disconnect=None,          # Disconnect callback (async or sync)
)

app = FastAPI(lifespan=lifespan)
```

Use `get_tunnel_client()` to access the client instance in your routes.

### TunnelRunner

For more control over the background runner:

```python
from data_agent_tunnel_client import TunnelRunner

runner = TunnelRunner(
    tunnel_url="wss://...",
    local_url="http://...",
    secret_key="",
    home_path="/",
    on_connect=lambda client: print(f"Connected: {client.public_url}"),
    on_disconnect=lambda client: print("Disconnected"),
)

runner.start()  # Non-blocking
```

### TunnelClient

Low-level async client:

```python
from data_agent_tunnel_client import TunnelClient

client = TunnelClient(
    tunnel_url: str,                    # Tunnel WebSocket URL
    local_url: str,                     # Local service URL
    secret_key: str = "",               # Auth key (optional)
    session_id: str = "",               # Session ID (optional)
    reconnect: bool = True,             # Auto reconnect on disconnect
    reconnect_interval: float = 5.0,    # Reconnect interval (seconds)
    ping_interval: float = 30.0,        # Heartbeat interval (seconds)
    request_timeout: float = 300.0,     # Request timeout (seconds)
    max_concurrent_requests: int = 100, # Max concurrent requests
    on_connect: Callable = None,        # Connect callback (async)
    on_disconnect: Callable = None,     # Disconnect callback (async)
)

# Properties
client.public_url           # Public URL
client.connected_session_id # Session ID
client.is_connected         # Connection status

# Methods
await client.connect()      # Connect and start proxying
await client.disconnect()   # Disconnect
```

## Proxy Support

The client automatically detects and uses system proxy settings (`http_proxy`, `https_proxy`, `socks_proxy`, etc.).

- If proxy is configured, it tries to connect via proxy first
- If proxy connection fails, it falls back to direct connection
- Use `disable_proxy=True` to skip proxy entirely

## License

MIT