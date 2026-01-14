"""
Antigravity Claude Proxy - CLI Module

Interactive CLI for adding and managing Google accounts
for the Antigravity Claude Proxy.

Usage:
    python -m antigravity_proxy accounts          # Interactive mode (add)
    python -m antigravity_proxy accounts add      # Add new account(s)
    python -m antigravity_proxy accounts list     # List all accounts
    python -m antigravity_proxy accounts remove   # Remove accounts interactively
    python -m antigravity_proxy accounts verify   # Verify account tokens
    python -m antigravity_proxy accounts clear    # Remove all accounts

Options:
    --no-browser    Manual authorization code input (for headless servers)

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import os
import sys
import json
import socket
import asyncio
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from .config import (
    ACCOUNT_CONFIG_PATH,
    DEFAULT_PORT,
    MAX_ACCOUNTS,
    logger
)
from .auth import (
    get_authorization_url,
    start_callback_server,
    complete_oauth_flow,
    refresh_access_token,
    get_user_email,
    extract_code_from_input
)


# =============================================================================
# UTILITIES
# =============================================================================

def is_server_running(port: int = DEFAULT_PORT) -> bool:
    """
    Check if the Antigravity Proxy server is running.
    
    Args:
        port: Port to check
        
    Returns:
        True if port is occupied (server running)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(("localhost", port))
        return result == 0
    except Exception:
        return False
    finally:
        sock.close()


def ensure_server_stopped(port: int = DEFAULT_PORT) -> None:
    """
    Enforce that server is stopped before proceeding.
    
    Args:
        port: Port to check
        
    Raises:
        SystemExit: If server is running
    """
    if is_server_running(port):
        print(f"""
\x1b[31mError: Antigravity Proxy server is currently running on port {port}.\x1b[0m

Please stop the server (Ctrl+C) before adding or managing accounts.
This ensures that your account changes are loaded correctly when you restart the server.
""")
        sys.exit(1)


def open_browser(url: str) -> None:
    """
    Open URL in default browser.
    
    Args:
        url: URL to open
    """
    system = platform.system()
    
    try:
        if system == "Darwin":
            subprocess.run(["open", url], check=True)
        elif system == "Windows":
            subprocess.run(["start", "", url], shell=True, check=True)
        else:
            subprocess.run(["xdg-open", url], check=True)
    except Exception as e:
        print(f"\n⚠ Could not open browser automatically.")
        print(f"Please open this URL manually: {url}")


# =============================================================================
# ACCOUNT STORAGE
# =============================================================================

def load_accounts() -> List[Dict[str, Any]]:
    """
    Load existing accounts from config.
    
    Returns:
        List of account dictionaries
    """
    try:
        if ACCOUNT_CONFIG_PATH.exists():
            with open(ACCOUNT_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("accounts", [])
    except Exception as e:
        print(f"Error loading accounts: {e}")
    return []


def save_accounts(accounts: List[Dict[str, Any]], settings: Optional[Dict[str, Any]] = None) -> None:
    """
    Save accounts to config.
    
    Args:
        accounts: List of account dictionaries
        settings: Optional settings dictionary
    """
    try:
        # Ensure directory exists
        ACCOUNT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "accounts": [
                {
                    "email": acc.get("email"),
                    "source": "oauth",
                    "refreshToken": acc.get("refreshToken") or acc.get("refresh_token"),
                    "projectId": acc.get("projectId") or acc.get("project_id"),
                    "addedAt": acc.get("addedAt") or datetime.now().isoformat(),
                    "lastUsed": acc.get("lastUsed"),
                    "modelRateLimits": acc.get("modelRateLimits", {})
                }
                for acc in accounts
            ],
            "settings": {
                "cooldownDurationMs": 60000,
                "maxRetries": 5,
                **(settings or {})
            },
            "activeIndex": 0
        }
        
        with open(ACCOUNT_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✓ Saved {len(accounts)} account(s) to {ACCOUNT_CONFIG_PATH}")
        
    except Exception as e:
        print(f"Error saving accounts: {e}")
        raise


def display_accounts(accounts: List[Dict[str, Any]]) -> None:
    """
    Display current accounts.
    
    Args:
        accounts: List of account dictionaries
    """
    if not accounts:
        print("\nNo accounts configured.")
        return
    
    print(f"\n{len(accounts)} account(s) saved:")
    for i, acc in enumerate(accounts):
        # Check for any active model-specific rate limits
        import time
        now = time.time()
        model_limits = acc.get("modelRateLimits", {})
        has_active_limit = any(
            limit.get("isRateLimited") and limit.get("resetTime", 0) > now
            for limit in model_limits.values()
        )
        status = " (rate-limited)" if has_active_limit else ""
        print(f"  {i + 1}. {acc.get('email')}{status}")


# =============================================================================
# ADD ACCOUNT (with browser)
# =============================================================================

async def add_account(existing_accounts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Add a new account via OAuth with automatic callback.
    
    Args:
        existing_accounts: List of existing account dictionaries
        
    Returns:
        New account dictionary or None if failed/duplicate
    """
    print("\n=== Add Google Account ===\n")
    
    # Generate authorization URL
    auth_data = get_authorization_url()
    url = auth_data["url"]
    verifier = auth_data["verifier"]
    state = auth_data["state"]
    
    print("Opening browser for Google sign-in...")
    print("(If browser does not open, copy this URL manually)\n")
    print(f"   {url}\n")
    
    # Open browser
    open_browser(url)
    
    # Start callback server and wait for code
    print("Waiting for authentication (timeout: 2 minutes)...\n")
    
    try:
        code = start_callback_server(state, timeout_seconds=120)
        
        print("Received authorization code. Exchanging for tokens...")
        result = await complete_oauth_flow(code, verifier)
        
        # Check if account already exists
        existing = next(
            (a for a in existing_accounts if a.get("email") == result["email"]),
            None
        )
        if existing:
            print(f"\n⚠ Account {result['email']} already exists. Updating tokens.")
            existing["refreshToken"] = result["refresh_token"]
            existing["projectId"] = result["project_id"]
            existing["addedAt"] = datetime.now().isoformat()
            return None  # Don't add duplicate
        
        print(f"\n✓ Successfully authenticated: {result['email']}")
        if result.get("project_id"):
            print(f"  Project ID: {result['project_id']}")
        
        return {
            "email": result["email"],
            "refreshToken": result["refresh_token"],
            "projectId": result["project_id"],
            "addedAt": datetime.now().isoformat(),
            "modelRateLimits": {}
        }
        
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return None


# =============================================================================
# ADD ACCOUNT (no browser / headless)
# =============================================================================

async def add_account_no_browser(existing_accounts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Add a new account via OAuth with manual code input (no-browser mode).
    For headless servers without a desktop environment.
    
    Args:
        existing_accounts: List of existing account dictionaries
        
    Returns:
        New account dictionary or None if failed/duplicate
    """
    print("\n=== Add Google Account (No-Browser Mode) ===\n")
    
    # Generate authorization URL
    auth_data = get_authorization_url()
    url = auth_data["url"]
    verifier = auth_data["verifier"]
    state = auth_data["state"]
    
    print("Copy the following URL and open it in a browser on another device:\n")
    print(f"   {url}\n")
    print("After signing in, you will be redirected to a localhost URL.")
    print("Copy the ENTIRE redirect URL or just the authorization code.\n")
    
    user_input = input("Paste the callback URL or authorization code: ").strip()
    
    try:
        extracted = extract_code_from_input(user_input)
        code = extracted["code"]
        extracted_state = extracted.get("state")
        
        # Validate state if present
        if extracted_state and extracted_state != state:
            print("\n⚠ State mismatch detected. This could indicate a security issue.")
            print("Proceeding anyway as this is manual mode...")
        
        print("\nExchanging authorization code for tokens...")
        result = await complete_oauth_flow(code, verifier)
        
        # Check if account already exists
        existing = next(
            (a for a in existing_accounts if a.get("email") == result["email"]),
            None
        )
        if existing:
            print(f"\n⚠ Account {result['email']} already exists. Updating tokens.")
            existing["refreshToken"] = result["refresh_token"]
            existing["projectId"] = result["project_id"]
            existing["addedAt"] = datetime.now().isoformat()
            return None  # Don't add duplicate
        
        print(f"\n✓ Successfully authenticated: {result['email']}")
        if result.get("project_id"):
            print(f"  Project ID: {result['project_id']}")
        
        return {
            "email": result["email"],
            "refreshToken": result["refresh_token"],
            "projectId": result["project_id"],
            "addedAt": datetime.now().isoformat(),
            "modelRateLimits": {}
        }
        
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return None


# =============================================================================
# INTERACTIVE FLOWS
# =============================================================================

async def interactive_remove() -> None:
    """Interactive remove accounts flow."""
    while True:
        accounts = load_accounts()
        if not accounts:
            print("\nNo accounts to remove.")
            return
        
        display_accounts(accounts)
        print("\nEnter account number to remove (or 0 to cancel)")
        
        try:
            answer = input("> ").strip()
            index = int(answer)
        except ValueError:
            print("\n❌ Invalid selection.")
            continue
        
        if index < 0 or index > len(accounts):
            print("\n❌ Invalid selection.")
            continue
        
        if index == 0:
            return  # Exit
        
        removed = accounts[index - 1]  # 1-based to 0-based
        confirm = input(f"\nAre you sure you want to remove {removed.get('email')}? [y/N]: ").strip().lower()
        
        if confirm == "y":
            accounts.pop(index - 1)
            save_accounts(accounts)
            print(f"\n✓ Removed {removed.get('email')}")
        else:
            print("\nCancelled.")
        
        remove_more = input("\nRemove another account? [y/N]: ").strip().lower()
        if remove_more != "y":
            break


async def interactive_add(no_browser: bool = False) -> None:
    """
    Interactive add accounts flow (Main Menu).
    
    Args:
        no_browser: If True, use manual code input mode
    """
    if no_browser:
        print("\n📋 No-browser mode: You will manually paste the authorization code.\n")
    
    accounts = load_accounts()
    
    if accounts:
        display_accounts(accounts)
        
        choice = input("\n(a)dd new, (r)emove existing, (f)resh start, or (e)xit? [a/r/f/e]: ").strip().lower()
        
        if choice == "r":
            await interactive_remove()
            return
        elif choice == "f":
            print("\nStarting fresh - existing accounts will be replaced.")
            accounts = []
        elif choice == "a":
            print("\nAdding to existing accounts.")
        elif choice == "e":
            print("\nExiting...")
            return
        else:
            print("\nInvalid choice, defaulting to add.")
    
    # Add single account
    if len(accounts) >= MAX_ACCOUNTS:
        print(f"\nMaximum of {MAX_ACCOUNTS} accounts reached.")
        return
    
    # Use appropriate add function based on mode
    if no_browser:
        new_account = await add_account_no_browser(accounts)
    else:
        new_account = await add_account(accounts)
    
    if new_account:
        accounts.append(new_account)
        save_accounts(accounts)
    elif accounts:
        # Even if new_account is None (duplicate update), save the updated accounts
        save_accounts(accounts)
    
    if accounts:
        display_accounts(accounts)
        print("\nTo add more accounts, run this command again.")
    else:
        print("\nNo accounts to save.")


async def list_accounts_cmd() -> None:
    """List accounts command."""
    accounts = load_accounts()
    display_accounts(accounts)
    
    if accounts:
        print(f"\nConfig file: {ACCOUNT_CONFIG_PATH}")


async def clear_accounts() -> None:
    """Clear all accounts command."""
    accounts = load_accounts()
    
    if not accounts:
        print("No accounts to clear.")
        return
    
    display_accounts(accounts)
    
    confirm = input("\nAre you sure you want to remove all accounts? [y/N]: ").strip().lower()
    if confirm == "y":
        save_accounts([])
        print("All accounts removed.")
    else:
        print("Cancelled.")


async def verify_accounts() -> None:
    """Verify accounts (test refresh tokens) command."""
    accounts = load_accounts()
    
    if not accounts:
        print("No accounts to verify.")
        return
    
    print("\nVerifying accounts...\n")
    
    for account in accounts:
        try:
            refresh_token = account.get("refreshToken") or account.get("refresh_token")
            if not refresh_token:
                print(f"  ✗ {account.get('email')} - No refresh token")
                continue
            
            tokens = await refresh_access_token(refresh_token)
            email = await get_user_email(tokens["access_token"])
            print(f"  ✓ {email} - OK")
        except Exception as e:
            print(f"  ✗ {account.get('email')} - {e}")


# =============================================================================
# MAIN CLI ENTRY POINT
# =============================================================================

async def cli_main() -> None:
    """Main CLI entry point."""
    import argparse
    
    print("╔════════════════════════════════════════╗")
    print("║   Antigravity Proxy Account Manager    ║")
    print("║   Use --no-browser for headless mode   ║")
    print("╚════════════════════════════════════════╝")
    
    parser = argparse.ArgumentParser(
        description="Antigravity Proxy Account Manager",
        prog="antigravity_proxy accounts"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="add",
        choices=["add", "list", "remove", "verify", "clear", "help"],
        help="Command to run (default: add)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Manual authorization code input (for headless servers)"
    )
    
    # Parse only known args to handle being called from __main__.py
    args, _ = parser.parse_known_args()
    
    command = args.command
    no_browser = args.no_browser
    
    try:
        if command == "add":
            ensure_server_stopped()
            await interactive_add(no_browser)
        elif command == "list":
            await list_accounts_cmd()
        elif command == "remove":
            ensure_server_stopped()
            await interactive_remove()
        elif command == "verify":
            await verify_accounts()
        elif command == "clear":
            ensure_server_stopped()
            await clear_accounts()
        elif command == "help":
            print("\nUsage:")
            print("  python -m antigravity_proxy accounts add     Add new account(s)")
            print("  python -m antigravity_proxy accounts list    List all accounts")
            print("  python -m antigravity_proxy accounts remove  Remove accounts interactively")
            print("  python -m antigravity_proxy accounts verify  Verify account tokens")
            print("  python -m antigravity_proxy accounts clear   Remove all accounts")
            print("  python -m antigravity_proxy accounts help    Show this help")
            print("\nOptions:")
            print("  --no-browser    Manual authorization code input (for headless servers)")
        else:
            print(f"Unknown command: {command}")
            print("Run with 'help' for usage information.")
    except KeyboardInterrupt:
        print("\n\nCancelled.")


def run_cli() -> None:
    """Synchronous wrapper for CLI entry point."""
    try:
        asyncio.run(cli_main())
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    run_cli()
