"""
Data Agent Tunnel Client

Transparently proxy local web services to the Tunnel server
"""

from .client import TunnelClient, run_tunnel
from .auth import generate_signature, create_auth_params
from .integration import (
    TunnelRunner,
    connect_tunnel,
    create_tunnel_lifespan,
    get_tunnel_client,
)

__version__ = "0.1.6"
__all__ = [
    "TunnelClient",
    "run_tunnel",
    "TunnelRunner",
    "connect_tunnel",
    "create_tunnel_lifespan",
    "get_tunnel_client",
    "generate_signature",
    "create_auth_params",
]