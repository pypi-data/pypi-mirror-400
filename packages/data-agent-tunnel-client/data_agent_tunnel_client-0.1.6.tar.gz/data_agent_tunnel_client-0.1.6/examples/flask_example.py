#!/usr/bin/env python3
"""
Flask 示例：多路由 + HTML 表单 + 表单提交
"""
import logging
import os

from flask import Flask, request, jsonify, render_template_string

from data_agent_tunnel_client import connect_tunnel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============== Flask 应用 ==============
app = Flask(__name__)

# 存储提交的数据
submissions = []

# 首页 HTML 模板
INDEX_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Agent Tunnel Demo</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #333; margin-bottom: 10px; }
        h2 { color: #555; margin-bottom: 20px; font-size: 18px; }
        .subtitle { color: #888; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        input, textarea, select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea { resize: vertical; min-height: 100px; }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav a {
            padding: 10px 20px;
            background: #f0f0f0;
            border-radius: 8px;
            text-decoration: none;
            color: #555;
            transition: background 0.3s;
        }
        .nav a:hover { background: #e0e0e0; }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .info-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 14px;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🚀 Data Agent Tunnel Demo</h1>
            <p class="subtitle">通过 Tunnel 代理访问本地 Flask 服务</p>

            <div class="nav">
                <a href="/">首页</a>
                <a href="/api/status">API 状态</a>
                <a href="/api/submissions">查看提交</a>
                <a href="/about">关于</a>
            </div>

            {% if success %}
            <div class="success">
                ✅ 表单提交成功！
            </div>
            {% endif %}

            <h2>📝 提交表单</h2>
            <form method="POST" action="/submit">
                <div class="form-group">
                    <label for="name">姓名</label>
                    <input type="text" id="name" name="name" placeholder="请输入姓名" required>
                </div>

                <div class="form-group">
                    <label for="email">邮箱</label>
                    <input type="email" id="email" name="email" placeholder="请输入邮箱" required>
                </div>

                <div class="form-group">
                    <label for="category">分类</label>
                    <select id="category" name="category">
                        <option value="feedback">反馈建议</option>
                        <option value="bug">Bug 报告</option>
                        <option value="feature">功能请求</option>
                        <option value="other">其他</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="message">消息内容</label>
                    <textarea id="message" name="message" placeholder="请输入详细内容..." required></textarea>
                </div>

                <button type="submit">提交表单</button>
            </form>

            <div class="info-box">
                <strong>请求信息:</strong><br>
                Method: {{ request.method }}<br>
                Path: {{ request.path }}<br>
                Host: {{ request.host }}<br>
                User-Agent: {{ request.user_agent.string[:50] }}...
            </div>
        </div>
    </div>
</body>
</html>
"""

# 提交列表 HTML 模板
SUBMISSIONS_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>提交记录 - Data Agent Tunnel Demo</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #333; margin-bottom: 20px; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav a {
            padding: 10px 20px;
            background: #f0f0f0;
            border-radius: 8px;
            text-decoration: none;
            color: #555;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
        .empty { text-align: center; color: #888; padding: 40px; }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
        }
        .badge-feedback { background: #d1ecf1; color: #0c5460; }
        .badge-bug { background: #f8d7da; color: #721c24; }
        .badge-feature { background: #d4edda; color: #155724; }
        .badge-other { background: #e2e3e5; color: #383d41; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📋 提交记录</h1>

            <div class="nav">
                <a href="/">← 返回首页</a>
                <a href="/api/submissions">JSON 格式</a>
            </div>

            {% if submissions %}
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>姓名</th>
                        <th>邮箱</th>
                        <th>分类</th>
                        <th>消息</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody>
                    {% for s in submissions %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ s.name }}</td>
                        <td>{{ s.email }}</td>
                        <td><span class="badge badge-{{ s.category }}">{{ s.category }}</span></td>
                        <td>{{ s.message[:30] }}{% if s.message|length > 30 %}...{% endif %}</td>
                        <td>{{ s.timestamp }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty">
                暂无提交记录，去<a href="/">首页</a>提交一条吧！
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# 关于页面 HTML
ABOUT_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>关于 - Data Agent Tunnel Demo</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #333; margin-bottom: 20px; }
        h2 { color: #555; margin: 20px 0 10px; }
        p { color: #666; line-height: 1.8; margin-bottom: 15px; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav a {
            padding: 10px 20px;
            background: #f0f0f0;
            border-radius: 8px;
            text-decoration: none;
            color: #555;
        }
        code {
            background: #f4f4f4;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📖 关于 Data Agent Tunnel</h1>

            <div class="nav">
                <a href="/">← 返回首页</a>
            </div>

            <h2>什么是 Data Agent Tunnel？</h2>
            <p>
                Data Agent Tunnel 是一个反向隧道代理服务，可以将你的本地 Web 服务暴露到公网，
                无需配置路由器、防火墙或购买公网 IP。
            </p>

            <h2>工作原理</h2>
            <p>
                1. 本地客户端通过 WebSocket 连接到 Tunnel 服务器<br>
                2. 服务器分配一个唯一的公网 URL<br>
                3. 外部请求通过 Tunnel 转发到本地服务<br>
                4. 本地服务的响应通过 Tunnel 返回给用户
            </p>

            <h2>快速开始</h2>
            <pre>from data_agent_tunnel_client import TunnelClient

client = TunnelClient(
    tunnel_url="wss://your-tunnel-server/_tunnel/ws",
    local_url="http://localhost:5000"
)
await client.connect()</pre>

            <h2>API 端点</h2>
            <p>
                <code>GET /</code> - 首页（表单）<br>
                <code>POST /submit</code> - 提交表单<br>
                <code>GET /api/status</code> - 服务状态<br>
                <code>GET /api/submissions</code> - 提交记录 (JSON)<br>
                <code>GET /submissions</code> - 提交记录 (HTML)<br>
                <code>GET /about</code> - 关于页面
            </p>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    """首页 - 显示表单"""
    success = request.args.get("success") == "1"
    return render_template_string(INDEX_HTML, request=request, success=success)


@app.route("/submit", methods=["POST"])
def submit():
    """处理表单提交"""
    from datetime import datetime

    data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "category": request.form.get("category"),
        "message": request.form.get("message"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr
    }

    submissions.append(data)
    logger.info(f"收到表单提交: {data['name']} <{data['email']}>")

    # 重定向回首页，显示成功消息
    from flask import redirect
    return redirect("/?success=1")


@app.route("/submissions")
def submissions_page():
    """提交记录页面 (HTML)"""
    return render_template_string(SUBMISSIONS_HTML, submissions=submissions)


@app.route("/about")
def about():
    """关于页面"""
    return render_template_string(ABOUT_HTML)


@app.route("/api/status")
def api_status():
    """API: 服务状态"""
    return jsonify({
        "status": "running",
        "service": "Flask Demo",
        "version": "1.0.0",
        "submissions_count": len(submissions),
        "endpoints": [
            {"method": "GET", "path": "/", "description": "首页"},
            {"method": "POST", "path": "/submit", "description": "提交表单"},
            {"method": "GET", "path": "/api/status", "description": "服务状态"},
            {"method": "GET", "path": "/api/submissions", "description": "提交记录"},
            {"method": "GET", "path": "/submissions", "description": "提交记录页面"},
            {"method": "GET", "path": "/about", "description": "关于页面"},
        ]
    })


@app.route("/api/submissions")
def api_submissions():
    """API: 获取所有提交记录"""
    return jsonify({
        "total": len(submissions),
        "submissions": submissions
    })


@app.route("/api/echo", methods=["GET", "POST", "PUT", "DELETE"])
def api_echo():
    """API: 回显请求信息"""
    return jsonify({
        "method": request.method,
        "path": request.path,
        "query": dict(request.args),
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True),
        "json": request.get_json(silent=True),
        "form": dict(request.form),
    })


# ============== 主程序 ==============
if __name__ == "__main__":
    local_port = 5001

    print()
    print("=" * 60)
    print("  Flask + Data Agent Tunnel Demo")
    print("=" * 60)
    print()

    # 一行代码启动 Tunnel 客户端（后台运行）
    connect_tunnel(
        tunnel_url="wss://data.eigenai.com/_tunnel/ws",
        local_url=f"http://127.0.0.1:{local_port}",
        home_path="/api/echo",
        secret_key=os.environ.get("DATA_AGENT_TUNNEL_SECRET_KEY", "123")
    )

    # 启动 Flask（主线程）
    print(f"启动本地 Flask 服务: http://127.0.0.1:{local_port}")
    print()

    app.run(
        host="127.0.0.1",
        port=local_port,
        debug=False,
        use_reloader=False
    )
