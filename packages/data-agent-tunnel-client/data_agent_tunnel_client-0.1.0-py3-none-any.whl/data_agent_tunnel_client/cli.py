#!/usr/bin/env python3
"""
命令行接口
"""
import argparse
import logging
import sys

from .client import run_tunnel


def main():
    parser = argparse.ArgumentParser(
        description="Data Agent Tunnel Client - 将本地服务代理到公网"
    )
    parser.add_argument(
        "-t", "--tunnel-url",
        required=True,
        help="Tunnel WebSocket 地址，如 wss://data.eigenai.com/_tunnel/ws"
    )
    parser.add_argument(
        "-l", "--local-url",
        required=True,
        help="本地服务地址，如 http://localhost:5000"
    )
    parser.add_argument(
        "-k", "--secret-key",
        default="",
        help="认证密钥（可选）"
    )
    parser.add_argument(
        "-s", "--session-id",
        default="",
        help="指定会话 ID（可选）"
    )
    parser.add_argument(
        "--no-reconnect",
        action="store_true",
        help="断开后不自动重连"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志"
    )

    args = parser.parse_args()

    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print(f"Data Agent Tunnel Client v0.1.0")
    print(f"本地服务: {args.local_url}")
    print(f"Tunnel: {args.tunnel_url}")
    print()

    try:
        run_tunnel(
            tunnel_url=args.tunnel_url,
            local_url=args.local_url,
            secret_key=args.secret_key,
            session_id=args.session_id,
            reconnect=not args.no_reconnect,
        )
    except KeyboardInterrupt:
        print("\n已断开连接")
        sys.exit(0)


if __name__ == "__main__":
    main()