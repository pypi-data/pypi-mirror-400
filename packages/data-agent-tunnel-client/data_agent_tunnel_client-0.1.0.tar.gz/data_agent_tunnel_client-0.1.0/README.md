# Data Agent Tunnel Client

将本地 Web 服务透明代理到 Data Agent Tunnel，获得公网访问地址。

## 安装

```bash
pip install -e .
```

## 快速开始

### 方式一：Python 代码集成

```python
import asyncio
from data_agent_tunnel_client import TunnelClient

async def main():
    client = TunnelClient(
        tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
        local_url="http://localhost:5000",
        secret_key="your-secret-key",  # 可选
    )

    # 连接成功后的回调
    async def on_connect(c: TunnelClient):
        print(f"已连接! 公网地址: {c.public_url}")

    client.on_connect = on_connect

    await client.connect()

asyncio.run(main())
```

### 方式二：命令行工具

```bash
tunnel-client \
    -t wss://dataagent.eigenai.com/_tunnel/ws \
    -l http://localhost:5000 \
    -k your-secret-key
```

### 方式三：同步接口

```python
from data_agent_tunnel_client import run_tunnel

run_tunnel(
    tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
    local_url="http://localhost:5000"
)
```

## 与 Flask 集成

```python
from flask import Flask
from data_agent_tunnel_client import TunnelClient
import asyncio
import threading

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask!"

@app.route("/api/data")
def data():
    return {"message": "This is proxied through tunnel"}

def start_tunnel():
    async def run():
        client = TunnelClient(
            tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
            local_url="http://localhost:5000"
        )
        async def on_connect(c):
            print(f"Tunnel 已连接: {c.public_url}")
        client.on_connect = on_connect
        await client.connect()

    asyncio.run(run())

if __name__ == "__main__":
    # 在后台线程启动 tunnel
    tunnel_thread = threading.Thread(target=start_tunnel, daemon=True)
    tunnel_thread.start()

    # 启动 Flask
    app.run(port=5000)
```

## 与 FastAPI 集成

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from data_agent_tunnel_client import TunnelClient
import asyncio

tunnel_client: TunnelClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global tunnel_client

    tunnel_client = TunnelClient(
        tunnel_url="wss://dataagent.eigenai.com/_tunnel/ws",
        local_url="http://localhost:8000"
    )

    async def on_connect(c):
        print(f"Tunnel 已连接: {c.public_url}")

    tunnel_client.on_connect = on_connect

    # 在后台启动 tunnel
    task = asyncio.create_task(tunnel_client.connect())

    yield

    # 关闭 tunnel
    await tunnel_client.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/tunnel-url")
async def get_tunnel_url():
    return {"public_url": tunnel_client.public_url}
```

## API 参考

### TunnelClient

```python
TunnelClient(
    tunnel_url: str,           # Tunnel WebSocket 地址
    local_url: str,            # 本地服务地址
    secret_key: str = "",      # 认证密钥（可选）
    session_id: str = "",      # 指定会话 ID（可选）
    reconnect: bool = True,    # 断开后自动重连
    reconnect_interval: float = 5.0,  # 重连间隔（秒）
    ping_interval: float = 30.0,      # 心跳间隔（秒）
    on_connect: Callable = None,      # 连接成功回调
    on_disconnect: Callable = None,   # 断开连接回调
)
```

**属性:**
- `public_url`: 公网访问地址
- `connected_session_id`: 当前会话 ID
- `is_connected`: 是否已连接

**方法:**
- `await connect()`: 连接并开始代理
- `await disconnect()`: 断开连接

## 命令行参数

```
usage: tunnel-client [-h] -t TUNNEL_URL -l LOCAL_URL [-k SECRET_KEY]
                     [-s SESSION_ID] [--no-reconnect] [-v]

options:
  -t, --tunnel-url    Tunnel WebSocket 地址
  -l, --local-url     本地服务地址
  -k, --secret-key    认证密钥（可选）
  -s, --session-id    指定会话 ID（可选）
  --no-reconnect      断开后不自动重连
  -v, --verbose       显示详细日志
```

## License

MIT