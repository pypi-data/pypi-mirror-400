#!/usr/bin/env python3
"""
Antigravity Claude Proxy - Main Entry Point
"""

import os
import sys

# Ensure the package directory is in the path
package_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(package_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def main():
    """Main entry point."""
    import argparse
    
    # Import after path fix
    from antigravity_proxy.config import DEFAULT_PORT, logger
    
    args = sys.argv[1:]
    
    # Handle help flags
    if "--help" in args or "-h" in args:
        show_help()
        return
    
    # Handle version flags
    if "--version" in args or "-v" in args:
        show_version()
        return
    
    # Determine command
    command = args[0] if args else "start"
    
    if command == "help":
        show_help()
        return
    
    if command == "version":
        show_version()
        return
    
    # Handle 'accounts' command
    if command == "accounts":
        from antigravity_proxy.cli import run_cli
        sys.argv = [sys.argv[0]] + args[1:]
        run_cli()
        return
    
    # Handle 'start' command (or default)
    if command == "start" or command not in ("accounts", "help", "version"):
        remaining_args = args[1:] if command == "start" else args
        
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--port", type=int, default=None)
        parser.add_argument("--debug", action="store_true")
        parser.add_argument("--fallback", action="store_true")
        
        parsed, _ = parser.parse_known_args(remaining_args)
        
        port = parsed.port or int(os.environ.get("PORT", DEFAULT_PORT))
        debug = parsed.debug or os.environ.get("DEBUG", "").lower() == "true"
        fallback = parsed.fallback or os.environ.get("FALLBACK", "").lower() == "true"
        
        from antigravity_proxy.server import run_server
        run_server(port=port, debug=debug, fallback=fallback)
        return
    
    print(f"Unknown command: {command}")
    print('Run "ag-cc-proxy --help" for usage information.')
    sys.exit(1)


def show_help():
    """Display help message."""
    print("""
ag-cc-proxy - Antigravity Claude Proxy

Proxy server for using Antigravity's Claude/Gemini models with Claude Code CLI.

USAGE:
  ag-cc-proxy [command] [options]

COMMANDS:
  start                 Start the proxy server (default)
  accounts              Manage Google accounts (interactive)
  accounts add          Add a new Google account via OAuth
  accounts list         List all configured accounts
  accounts remove       Remove accounts interactively
  accounts verify       Verify account tokens are valid
  accounts clear        Remove all accounts

OPTIONS:
  --help, -h            Show this help message
  --version, -v         Show version number
  --port PORT           Server port (default: 8080)
  --debug               Enable debug logging
  --fallback            Enable model fallback on quota exhaustion
  --no-browser          Manual OAuth code input (for headless servers)

EXAMPLES:
  ag-cc-proxy                           # Start server on port 8080
  ag-cc-proxy --port 3000 --debug       # Start with custom port and debug
  ag-cc-proxy accounts add              # Add Google account
  ag-cc-proxy accounts add --no-browser # Add account (headless mode)
  ag-cc-proxy accounts list             # List accounts

CONFIGURATION:
  Set in Claude Code (~/.claude/settings.json):
    {
      "env": {
        "ANTHROPIC_BASE_URL": "http://localhost:8080"
      }
    }
""")


def show_version():
    """Display version."""
    print("0.1.0")


if __name__ == "__main__":
    main()
