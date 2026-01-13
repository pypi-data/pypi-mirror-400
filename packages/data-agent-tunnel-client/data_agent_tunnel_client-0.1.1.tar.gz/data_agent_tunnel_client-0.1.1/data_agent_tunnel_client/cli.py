#!/usr/bin/env python3
"""
Command line interface
"""
import argparse
import logging
import sys

from .client import run_tunnel
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        description="Data Agent Tunnel Client - Proxy local services to public network"
    )
    parser.add_argument(
        "-t", "--tunnel-url",
        required=True,
        help="Tunnel WebSocket URL, e.g. wss://dataagent.eigenai.com/_tunnel/ws"
    )
    parser.add_argument(
        "-l", "--local-url",
        required=True,
        help="Local service URL, e.g. http://localhost:5000"
    )
    parser.add_argument(
        "-k", "--secret-key",
        default="",
        help="Authentication key (optional)"
    )
    parser.add_argument(
        "-s", "--session-id",
        default="",
        help="Specify session ID (optional)"
    )
    parser.add_argument(
        "--no-reconnect",
        action="store_true",
        help="Disable auto reconnect on disconnect"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose logs"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print(f"Data Agent Tunnel Client v{__version__}")
    print(f"Local service: {args.local_url}")
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
        print("\nDisconnected")
        sys.exit(0)


if __name__ == "__main__":
    main()