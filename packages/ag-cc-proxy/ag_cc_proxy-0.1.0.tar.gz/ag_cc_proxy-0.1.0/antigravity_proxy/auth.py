"""
Antigravity Claude Proxy - Authentication Module

Handles:
- SQLite database access for Antigravity state
- Google OAuth with PKCE for multi-account authentication
- Token extraction and caching

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import os
import re
import json
import sqlite3
import secrets
import hashlib
import base64
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

import aiohttp

from .config import (
    ANTIGRAVITY_DB_PATH,
    ANTIGRAVITY_AUTH_PORT,
    ANTIGRAVITY_ENDPOINT_FALLBACKS,
    ANTIGRAVITY_HEADERS,
    TOKEN_REFRESH_INTERVAL_S,
    OAUTH_CONFIG,
    OAUTH_REDIRECT_URI,
    logger
)


# =============================================================================
# DATABASE ACCESS
# =============================================================================

class DatabaseError(Exception):
    """Error accessing Antigravity database."""
    pass


def get_auth_status(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Query Antigravity database for authentication status.
    
    Args:
        db_path: Optional custom database path (defaults to platform-specific path)
        
    Returns:
        Parsed auth data with apiKey, email, name, etc.
        
    Raises:
        DatabaseError: If database doesn't exist, query fails, or no auth status found
    """
    path = db_path or ANTIGRAVITY_DB_PATH
    
    if not path.exists():
        raise DatabaseError(
            f"Database not found at {path}. "
            "Make sure Antigravity is installed and you are logged in."
        )
    
    try:
        # Open database in read-only mode
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query for auth status
        cursor.execute(
            "SELECT value FROM ItemTable WHERE key = 'antigravityAuthStatus'"
        )
        row = cursor.fetchone()
        
        conn.close()
        
        if not row or not row["value"]:
            raise DatabaseError("No auth status found in database")
        
        # Parse JSON value
        auth_data = json.loads(row["value"])
        
        if not auth_data.get("apiKey"):
            raise DatabaseError("Auth data missing apiKey field")
        
        return auth_data
        
    except sqlite3.Error as e:
        if "unable to open database" in str(e).lower():
            raise DatabaseError(
                f"Database not found at {path}. "
                "Make sure Antigravity is installed and you are logged in."
            )
        raise DatabaseError(f"Failed to read Antigravity database: {e}")


def is_database_accessible(db_path: Optional[Path] = None) -> bool:
    """
    Check if database exists and is accessible.
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        True if database exists and can be opened
    """
    try:
        get_auth_status(db_path)
        return True
    except Exception:
        return False


# =============================================================================
# PKCE GENERATION
# =============================================================================

def generate_pkce() -> Tuple[str, str]:
    """
    Generate PKCE code verifier and challenge.
    
    Returns:
        Tuple of (verifier, challenge) as base64url-encoded strings
    """
    # Generate 32 random bytes for verifier
    verifier_bytes = secrets.token_bytes(32)
    verifier = base64.urlsafe_b64encode(verifier_bytes).rstrip(b"=").decode("ascii")
    
    # SHA256 hash of verifier for challenge
    challenge_hash = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(challenge_hash).rstrip(b"=").decode("ascii")
    
    return verifier, challenge


# =============================================================================
# OAUTH AUTHORIZATION
# =============================================================================

def get_authorization_url() -> Dict[str, str]:
    """
    Generate authorization URL for Google OAuth.
    
    Returns:
        Dict with 'url', 'verifier', and 'state' keys
    """
    verifier, challenge = generate_pkce()
    state = secrets.token_hex(16)
    
    params = {
        "client_id": OAUTH_CONFIG.client_id,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": OAUTH_CONFIG.scopes_string,
        "access_type": "offline",
        "prompt": "consent",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state
    }
    
    url = f"{OAUTH_CONFIG.auth_url}?{urlencode(params)}"
    
    return {
        "url": url,
        "verifier": verifier,
        "state": state
    }


def extract_code_from_input(user_input: str) -> Dict[str, Optional[str]]:
    """
    Extract authorization code and state from user input.
    
    User can paste either:
    - Full callback URL: http://localhost:51121/oauth-callback?code=xxx&state=xxx
    - Just the code parameter: 4/0xxx...
    
    Args:
        user_input: User input (URL or code)
        
    Returns:
        Dict with 'code' and 'state' (state may be None if just code provided)
        
    Raises:
        ValueError: If input is invalid
    """
    if not user_input or not isinstance(user_input, str):
        raise ValueError("No input provided")
    
    trimmed = user_input.strip()
    
    # Check if it looks like a URL
    if trimmed.startswith("http://") or trimmed.startswith("https://"):
        try:
            parsed = urlparse(trimmed)
            params = parse_qs(parsed.query)
            
            # Check for OAuth error
            if "error" in params:
                raise ValueError(f"OAuth error: {params['error'][0]}")
            
            code = params.get("code", [None])[0]
            state = params.get("state", [None])[0]
            
            if not code:
                raise ValueError("No authorization code found in URL")
            
            return {"code": code, "state": state}
            
        except ValueError:
            raise
        except Exception:
            raise ValueError("Invalid URL format")
    
    # Assume it's a raw code
    # Google auth codes typically start with "4/" and are long
    if len(trimmed) < 10:
        raise ValueError("Input is too short to be a valid authorization code")
    
    return {"code": trimmed, "state": None}


# =============================================================================
# OAUTH CALLBACK SERVER
# =============================================================================

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""
    
    # Class-level storage for result
    result: Optional[Dict[str, Any]] = None
    expected_state: Optional[str] = None
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
        """Handle GET request for OAuth callback."""
        parsed = urlparse(self.path)
        
        if parsed.path != "/oauth-callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return
        
        params = parse_qs(parsed.query)
        
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]
        
        if error:
            self._send_html(400, "Authentication Failed", f"❌ Error: {error}", "#dc3545")
            OAuthCallbackHandler.result = {"error": error}
            return
        
        if state != OAuthCallbackHandler.expected_state:
            self._send_html(400, "Authentication Failed", "❌ State mismatch - possible CSRF attack.", "#dc3545")
            OAuthCallbackHandler.result = {"error": "State mismatch"}
            return
        
        if not code:
            self._send_html(400, "Authentication Failed", "❌ No authorization code received.", "#dc3545")
            OAuthCallbackHandler.result = {"error": "No authorization code"}
            return
        
        # Success!
        self._send_html(200, "Authentication Successful", "✅ You can close this window and return to the terminal.", "#28a745")
        OAuthCallbackHandler.result = {"code": code}
    
    def _send_html(self, status: int, title: str, message: str, color: str):
        """Send HTML response."""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        
        html = f"""
        <html>
        <head><meta charset="UTF-8"><title>{title}</title></head>
        <body style="font-family: system-ui; padding: 40px; text-align: center;">
            <h1 style="color: {color};">{message}</h1>
            <p>You can close this window.</p>
            <script>setTimeout(() => window.close(), 2000);</script>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))


def start_callback_server(expected_state: str, timeout_seconds: int = 120) -> str:
    """
    Start a local server to receive the OAuth callback.
    
    Args:
        expected_state: Expected state parameter for CSRF protection
        timeout_seconds: Timeout in seconds (default 120)
        
    Returns:
        Authorization code from OAuth callback
        
    Raises:
        TimeoutError: If no callback received within timeout
        ValueError: If callback contained an error
    """
    OAuthCallbackHandler.result = None
    OAuthCallbackHandler.expected_state = expected_state
    
    server = HTTPServer(("localhost", OAUTH_CONFIG.callback_port), OAuthCallbackHandler)
    server.timeout = timeout_seconds
    
    logger.info(f"[OAuth] Callback server listening on port {OAUTH_CONFIG.callback_port}")
    
    # Handle requests until we get a result or timeout
    start_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
    
    while OAuthCallbackHandler.result is None:
        server.handle_request()
        if server.timeout <= 0:
            break
    
    server.server_close()
    
    if OAuthCallbackHandler.result is None:
        raise TimeoutError("OAuth callback timeout - no response received")
    
    if "error" in OAuthCallbackHandler.result:
        raise ValueError(f"OAuth error: {OAuthCallbackHandler.result['error']}")
    
    return OAuthCallbackHandler.result["code"]


async def start_callback_server_async(expected_state: str, timeout_seconds: int = 120) -> str:
    """
    Async version: Start a local server to receive the OAuth callback.
    
    Runs the blocking server in a thread pool.
    
    Args:
        expected_state: Expected state parameter for CSRF protection
        timeout_seconds: Timeout in seconds (default 120)
        
    Returns:
        Authorization code from OAuth callback
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        start_callback_server, 
        expected_state, 
        timeout_seconds
    )


# =============================================================================
# TOKEN EXCHANGE
# =============================================================================

async def exchange_code(code: str, verifier: str) -> Dict[str, Any]:
    """
    Exchange authorization code for tokens.
    
    Args:
        code: Authorization code from OAuth callback
        verifier: PKCE code verifier
        
    Returns:
        Dict with 'access_token', 'refresh_token', 'expires_in'
        
    Raises:
        ValueError: If token exchange fails
    """
    data = {
        "client_id": OAUTH_CONFIG.client_id,
        "client_secret": OAUTH_CONFIG.client_secret,
        "code": code,
        "code_verifier": verifier,
        "grant_type": "authorization_code",
        "redirect_uri": OAUTH_REDIRECT_URI
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            OAUTH_CONFIG.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if not response.ok:
                error_text = await response.text()
                logger.error(f"[OAuth] Token exchange failed: {response.status} {error_text}")
                raise ValueError(f"Token exchange failed: {error_text}")
            
            tokens = await response.json()
            
            if not tokens.get("access_token"):
                logger.error(f"[OAuth] No access token in response: {tokens}")
                raise ValueError("No access token received")
            
            logger.info(f"[OAuth] Token exchange successful, access_token length: {len(tokens.get('access_token', ''))}")
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in")
            }


async def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: OAuth refresh token
        
    Returns:
        Dict with 'access_token', 'expires_in'
        
    Raises:
        ValueError: If token refresh fails
    """
    data = {
        "client_id": OAUTH_CONFIG.client_id,
        "client_secret": OAUTH_CONFIG.client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            OAUTH_CONFIG.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if not response.ok:
                error_text = await response.text()
                raise ValueError(f"Token refresh failed: {error_text}")
            
            tokens = await response.json()
            
            return {
                "access_token": tokens["access_token"],
                "expires_in": tokens.get("expires_in")
            }


async def get_user_email(access_token: str) -> str:
    """
    Get user email from access token.
    
    Args:
        access_token: OAuth access token
        
    Returns:
        User's email address
        
    Raises:
        ValueError: If request fails
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            OAUTH_CONFIG.user_info_url,
            headers={"Authorization": f"Bearer {access_token}"}
        ) as response:
            if not response.ok:
                error_text = await response.text()
                logger.error(f"[OAuth] getUserEmail failed: {response.status} {error_text}")
                raise ValueError(f"Failed to get user info: {response.status}")
            
            user_info = await response.json()
            return user_info["email"]


async def discover_project_id(access_token: str) -> Optional[str]:
    """
    Discover project ID for the authenticated user.
    
    Args:
        access_token: OAuth access token
        
    Returns:
        Project ID or None if not found
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        **ANTIGRAVITY_HEADERS
    }
    
    body = {
        "metadata": {
            "ideType": "IDE_UNSPECIFIED",
            "platform": "PLATFORM_UNSPECIFIED",
            "pluginType": "GEMINI"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        for endpoint in ANTIGRAVITY_ENDPOINT_FALLBACKS:
            try:
                async with session.post(
                    f"{endpoint}/v1internal:loadCodeAssist",
                    json=body,
                    headers=headers
                ) as response:
                    if not response.ok:
                        continue
                    
                    data = await response.json()
                    
                    # Handle both string and object formats
                    project = data.get("cloudaicompanionProject")
                    if isinstance(project, str):
                        return project
                    if isinstance(project, dict) and project.get("id"):
                        return project["id"]
                        
            except Exception as e:
                logger.warn(f"[OAuth] Project discovery failed at {endpoint}: {e}")
    
    return None


async def complete_oauth_flow(code: str, verifier: str) -> Dict[str, Any]:
    """
    Complete OAuth flow: exchange code and get all account info.
    
    Args:
        code: Authorization code from OAuth callback
        verifier: PKCE code verifier
        
    Returns:
        Dict with 'email', 'refresh_token', 'access_token', 'project_id'
    """
    # Exchange code for tokens
    tokens = await exchange_code(code, verifier)
    
    # Get user email
    email = await get_user_email(tokens["access_token"])
    
    # Discover project ID
    project_id = await discover_project_id(tokens["access_token"])
    
    return {
        "email": email,
        "refresh_token": tokens["refresh_token"],
        "access_token": tokens["access_token"],
        "project_id": project_id
    }


# =============================================================================
# TOKEN EXTRACTOR (Legacy - from Antigravity database/page)
# =============================================================================

class TokenExtractor:
    """
    Token Extractor for Antigravity.
    
    Extracts OAuth tokens from Antigravity's SQLite database.
    The database is automatically updated by Antigravity when tokens refresh.
    """
    
    def __init__(self):
        self._cached_token: Optional[str] = None
        self._token_extracted_at: Optional[float] = None
    
    async def _extract_chat_params(self) -> Dict[str, Any]:
        """
        Extract the chat params from Antigravity's HTML page (fallback method).
        
        Returns:
            Parsed chat params config
            
        Raises:
            ConnectionError: If cannot connect to Antigravity
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://127.0.0.1:{ANTIGRAVITY_AUTH_PORT}/") as response:
                    html = await response.text()
                    
                    # Find the base64-encoded chatParams in the HTML
                    match = re.search(r"window\.chatParams\s*=\s*'([^']+)'", html)
                    if not match:
                        raise ValueError("Could not find chatParams in Antigravity page")
                    
                    # Decode base64
                    base64_data = match.group(1)
                    json_string = base64.b64decode(base64_data).decode("utf-8")
                    return json.loads(json_string)
                    
        except aiohttp.ClientConnectorError:
            raise ConnectionError(
                f"Cannot connect to Antigravity on port {ANTIGRAVITY_AUTH_PORT}. "
                "Make sure Antigravity is running."
            )
    
    async def _get_token_data(self) -> Dict[str, Any]:
        """
        Get fresh token data - tries DB first, falls back to HTML page.
        
        Returns:
            Auth data with apiKey
            
        Raises:
            ValueError: If token cannot be extracted
        """
        # Try database first (preferred - always has fresh token)
        try:
            db_data = get_auth_status()
            if db_data.get("apiKey"):
                logger.info("[Token] Got fresh token from SQLite database")
                return db_data
        except Exception as e:
            logger.warn(f"[Token] DB extraction failed, trying HTML page...")
        
        # Fallback to HTML page
        try:
            page_data = await self._extract_chat_params()
            if page_data.get("apiKey"):
                logger.warn("[Token] Got token from HTML page (may be stale)")
                return page_data
        except Exception as e:
            logger.warn(f"[Token] HTML page extraction failed: {e}")
        
        raise ValueError(
            "Could not extract token from Antigravity. "
            "Make sure Antigravity is running and you are logged in."
        )
    
    def _needs_refresh(self) -> bool:
        """Check if the cached token needs refresh."""
        if not self._cached_token or not self._token_extracted_at:
            return True
        import time
        return (time.time() - self._token_extracted_at) > TOKEN_REFRESH_INTERVAL_S
    
    async def get_token(self) -> str:
        """
        Get the current OAuth token (with caching).
        
        Returns:
            OAuth access token
        """
        if self._needs_refresh():
            import time
            data = await self._get_token_data()
            self._cached_token = data["apiKey"]
            self._token_extracted_at = time.time()
        return self._cached_token
    
    async def force_refresh(self) -> str:
        """
        Force refresh the token (useful if requests start failing).
        
        Returns:
            Fresh OAuth access token
        """
        self._cached_token = None
        self._token_extracted_at = None
        return await self.get_token()


# Global token extractor instance
token_extractor = TokenExtractor()
