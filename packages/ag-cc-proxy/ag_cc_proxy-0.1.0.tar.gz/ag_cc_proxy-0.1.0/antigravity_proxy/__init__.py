"""
ag-cc-proxy - Antigravity Claude Proxy

A Python proxy server that translates Anthropic's Messages API to Google's
Cloud Code API via Antigravity, enabling multi-account load balancing,
automatic failover, and rate limit handling.

Usage:
    # Start the server
    ag-cc-proxy
    ag-cc-proxy --port 3000 --debug
    
    # Manage accounts
    ag-cc-proxy accounts add
    ag-cc-proxy accounts list

Based on: https://github.com/badrisnarayanan/antigravity-claude-proxy
"""

__version__ = "0.1.0"
__author__ = "Catalyst"
__email__ = "tutralabs@gmail.com"

from .config import (
    DEFAULT_PORT,
    ACCOUNT_CONFIG_PATH,
    ANTIGRAVITY_DB_PATH,
    logger,
)
from .accounts import AccountManager
from .server import create_app, run_server

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "DEFAULT_PORT",
    "ACCOUNT_CONFIG_PATH",
    "ANTIGRAVITY_DB_PATH",
    "logger",
    "AccountManager",
    "create_app",
    "run_server",
]
