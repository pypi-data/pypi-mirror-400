"""
FastAPI integration example

Run with:
    uv run examples/fastapi_example.py
"""
import os

from fastapi import FastAPI

from data_agent_tunnel_client import create_tunnel_lifespan, get_tunnel_client

# Configuration
lifespan=create_tunnel_lifespan(
    tunnel_url="wss://data.eigenai.com/_tunnel/ws",
    local_url="http://localhost:8002",
    home_path="/api/data",
    secret_key=os.environ.get("DATA_AGENT_TUNNEL_SECRET_KEY", "123")
)

# Create FastAPI app with tunnel lifespan - much simpler!
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}


@app.get("/api/data")
async def get_data():
    return {
        "status": "ok",
        "data": [1, 2, 3, 4, 5],
        "message": "This is proxied through tunnel"
    }


@app.get("/tunnel-info")
async def tunnel_info():
    client = get_tunnel_client()
    return {
        "public_url": client.public_url if client else None,
        "session_id": client.connected_session_id if client else None,
        "is_connected": client.is_connected if client else False
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)