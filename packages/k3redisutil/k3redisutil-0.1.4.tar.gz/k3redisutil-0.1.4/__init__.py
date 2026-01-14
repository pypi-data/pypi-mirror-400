"""
For using redis more easily.
"""

from importlib.metadata import version

__version__ = version("k3redisutil")

from .redisutil import (
    get_client,
    wait_serve,
    normalize_ip_port,
    RedisChannel,
)

from .redis_proxy_cli import (
    KeyNotFoundError,
    RedisProxyError,
    SendRequestError,
    ServerResponseError,
    RedisProxyClient,
)

__all__ = [
    "get_client",
    "wait_serve",
    "normalize_ip_port",
    "RedisChannel",
    "KeyNotFoundError",
    "RedisProxyError",
    "SendRequestError",
    "ServerResponseError",
    "RedisProxyClient",
]
