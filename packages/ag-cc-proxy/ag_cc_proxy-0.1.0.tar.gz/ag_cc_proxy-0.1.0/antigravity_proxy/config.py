"""
Antigravity Claude Proxy - Configuration Module

Contains all constants, custom exceptions, helper functions, and logging.
Preserves all original values from the JavaScript implementation.

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import os
import re
import sys
import json
import platform
import asyncio
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum

# =============================================================================
# PLATFORM DETECTION
# =============================================================================

def get_antigravity_db_path() -> Path:
    """
    Get the Antigravity database path based on the current platform.
    
    Returns:
        Path to the Antigravity state database:
        - macOS: ~/Library/Application Support/Antigravity/User/globalStorage/state.vscdb
        - Windows: ~/AppData/Roaming/Antigravity/User/globalStorage/state.vscdb
        - Linux/other: ~/.config/Antigravity/User/globalStorage/state.vscdb
    """
    home = Path.home()
    system = platform.system()
    
    if system == "Darwin":
        return home / "Library/Application Support/Antigravity/User/globalStorage/state.vscdb"
    elif system == "Windows":
        return home / "AppData/Roaming/Antigravity/User/globalStorage/state.vscdb"
    else:  # Linux, FreeBSD, etc.
        return home / ".config/Antigravity/User/globalStorage/state.vscdb"


def get_platform_user_agent() -> str:
    """
    Generate platform-specific User-Agent string.
    
    Returns:
        User-Agent in format "antigravity/version os/arch"
    """
    os_name = platform.system().lower()
    architecture = platform.machine().lower()
    return f"antigravity/1.11.5 {os_name}/{architecture}"


def get_account_config_path() -> Path:
    """Get the path to the account configuration file."""
    return Path.home() / ".config/antigravity-proxy/accounts.json"


# =============================================================================
# CONSTANTS - Cloud Code API
# =============================================================================

# Cloud Code API endpoints (in fallback order: daily → prod)
ANTIGRAVITY_ENDPOINT_DAILY = "https://daily-cloudcode-pa.googleapis.com"
ANTIGRAVITY_ENDPOINT_PROD = "https://cloudcode-pa.googleapis.com"
ANTIGRAVITY_ENDPOINT_FALLBACKS = [
    ANTIGRAVITY_ENDPOINT_DAILY,
    ANTIGRAVITY_ENDPOINT_PROD
]

# Required headers for Antigravity API requests
ANTIGRAVITY_HEADERS = {
    "User-Agent": get_platform_user_agent(),
    "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
    "Client-Metadata": json.dumps({
        "ideType": "IDE_UNSPECIFIED",
        "platform": "PLATFORM_UNSPECIFIED",
        "pluginType": "GEMINI"
    })
}

# Default project ID if none can be discovered
DEFAULT_PROJECT_ID = "rising-fact-p41fc"

# =============================================================================
# CONSTANTS - Timing
# =============================================================================

TOKEN_REFRESH_INTERVAL_MS = 5 * 60 * 1000  # 5 minutes in milliseconds
TOKEN_REFRESH_INTERVAL_S = 5 * 60  # 5 minutes in seconds

DEFAULT_COOLDOWN_MS = 10 * 1000  # 10 second default cooldown
DEFAULT_COOLDOWN_S = 10  # 10 seconds

MAX_WAIT_BEFORE_ERROR_MS = 120_000  # 2 minutes - throw error if wait exceeds
MAX_WAIT_BEFORE_ERROR_S = 120  # 2 minutes in seconds

# =============================================================================
# CONSTANTS - Retry Logic
# =============================================================================

MAX_RETRIES = 5  # Max retry attempts across accounts
MAX_EMPTY_RESPONSE_RETRIES = 2  # Max retries for empty API responses
MAX_ACCOUNTS = 10  # Maximum number of accounts allowed

# =============================================================================
# CONSTANTS - Server
# =============================================================================

REQUEST_BODY_LIMIT = 50 * 1024 * 1024  # 50MB
ANTIGRAVITY_AUTH_PORT = 9092
DEFAULT_PORT = 8080

# =============================================================================
# CONSTANTS - Paths
# =============================================================================

ANTIGRAVITY_DB_PATH = get_antigravity_db_path()
ACCOUNT_CONFIG_PATH = get_account_config_path()

# =============================================================================
# CONSTANTS - Thinking Models
# =============================================================================

MIN_SIGNATURE_LENGTH = 50  # Minimum valid thinking signature length

# =============================================================================
# CONSTANTS - Gemini Specific
# =============================================================================

GEMINI_MAX_OUTPUT_TOKENS = 16384

# Sentinel value to skip thought signature validation when Claude Code strips the field
# See: https://ai.google.dev/gemini-api/docs/thought-signatures
GEMINI_SKIP_SIGNATURE = "skip_thought_signature_validator"

# Cache TTL for Gemini thoughtSignatures (2 hours)
GEMINI_SIGNATURE_CACHE_TTL_MS = 2 * 60 * 60 * 1000
GEMINI_SIGNATURE_CACHE_TTL_S = 2 * 60 * 60  # 2 hours in seconds

# =============================================================================
# CONSTANTS - OAuth Configuration
# =============================================================================

@dataclass(frozen=True)
class OAuthConfig:
    """
    Google OAuth configuration from opencode-antigravity-auth.
    
    These are the official Antigravity OAuth credentials.
    """
    client_id: str = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
    client_secret: str = "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"
    auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url: str = "https://oauth2.googleapis.com/token"
    user_info_url: str = "https://www.googleapis.com/oauth2/v1/userinfo"
    callback_port: int = 51121
    scopes: Tuple[str, ...] = (
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/cclog",
        "https://www.googleapis.com/auth/experimentsandconfigs"
    )
    
    @property
    def redirect_uri(self) -> str:
        """Get the OAuth redirect URI."""
        return f"http://localhost:{self.callback_port}/oauth-callback"
    
    @property
    def scopes_string(self) -> str:
        """Get scopes as space-separated string."""
        return " ".join(self.scopes)


OAUTH_CONFIG = OAuthConfig()
OAUTH_REDIRECT_URI = OAUTH_CONFIG.redirect_uri

# =============================================================================
# CONSTANTS - System Instructions
# =============================================================================

# Minimal Antigravity system instruction (from CLIProxyAPI)
# Only includes the essential identity portion to reduce token usage and improve response quality
# Reference: GitHub issue #76, CLIProxyAPI, gcli2api
ANTIGRAVITY_SYSTEM_INSTRUCTION = (
    "You are Antigravity, a powerful agentic AI coding assistant designed by the "
    "Google Deepmind team working on Advanced Agentic Coding. You are pair programming "
    "with a USER to solve their coding task. The task may require creating a new codebase, "
    "modifying or debugging an existing codebase, or simply answering a question."
    "**Absolute paths only****Proactiveness**"
)

# =============================================================================
# CONSTANTS - Model Fallback Mapping
# =============================================================================

# Model fallback mapping - maps primary model to fallback when quota exhausted
MODEL_FALLBACK_MAP: Dict[str, str] = {
    "gemini-3-pro-high": "claude-opus-4-5-thinking",
    "gemini-3-pro-low": "claude-sonnet-4-5",
    "gemini-3-flash": "claude-sonnet-4-5-thinking",
    "claude-opus-4-5-thinking": "gemini-3-pro-high",
    "claude-sonnet-4-5-thinking": "gemini-3-flash",
    "claude-sonnet-4-5": "gemini-3-flash"
}


# =============================================================================
# MODEL UTILITIES
# =============================================================================

class ModelFamily(Enum):
    """Model family enumeration."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    UNKNOWN = "unknown"


def get_model_family(model_name: Optional[str]) -> ModelFamily:
    """
    Get the model family from model name (dynamic detection, no hardcoded list).
    
    Args:
        model_name: The model name from the request
        
    Returns:
        ModelFamily enum value
    """
    lower = (model_name or "").lower()
    if "claude" in lower:
        return ModelFamily.CLAUDE
    if "gemini" in lower:
        return ModelFamily.GEMINI
    return ModelFamily.UNKNOWN


def is_thinking_model(model_name: Optional[str]) -> bool:
    """
    Check if a model supports thinking/reasoning output.
    
    Args:
        model_name: The model name from the request
        
    Returns:
        True if the model supports thinking blocks
    """
    lower = (model_name or "").lower()
    
    # Claude thinking models have "thinking" in the name
    if "claude" in lower and "thinking" in lower:
        return True
    
    # Gemini thinking models: explicit "thinking" in name, OR gemini version 3+
    if "gemini" in lower:
        if "thinking" in lower:
            return True
        # Check for gemini-3 or higher (e.g., gemini-3, gemini-3.5, gemini-4, etc.)
        match = re.search(r"gemini-(\d+)", lower)
        if match and int(match.group(1)) >= 3:
            return True
    
    return False


def get_fallback_model(model: str) -> Optional[str]:
    """
    Get fallback model for a given model ID.
    
    Args:
        model: Primary model ID
        
    Returns:
        Fallback model ID or None if no fallback exists
    """
    return MODEL_FALLBACK_MAP.get(model)


def has_fallback(model: str) -> bool:
    """
    Check if a model has a fallback configured.
    
    Args:
        model: Model ID to check
        
    Returns:
        True if fallback exists
    """
    return model in MODEL_FALLBACK_MAP


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class AntigravityError(Exception):
    """
    Base error class for Antigravity proxy errors.
    
    Provides structured error types for better error handling and classification.
    Replaces string-based error detection with proper error class checking.
    """
    
    def __init__(
        self, 
        message: str, 
        code: str = "UNKNOWN", 
        retryable: bool = False,
        **metadata
    ):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "name": self.__class__.__name__,
            "code": self.code,
            "message": str(self),
            "retryable": self.retryable,
            **self.metadata
        }


class RateLimitError(AntigravityError):
    """
    Rate limit error (429 / RESOURCE_EXHAUSTED).
    
    Attributes:
        reset_ms: Time in ms until rate limit resets
        account_email: Email of the rate-limited account
    """
    
    def __init__(
        self, 
        message: str, 
        reset_ms: Optional[int] = None,
        account_email: Optional[str] = None
    ):
        super().__init__(
            message, 
            code="RATE_LIMITED", 
            retryable=True,
            reset_ms=reset_ms,
            account_email=account_email
        )
        self.reset_ms = reset_ms
        self.account_email = account_email


class AuthError(AntigravityError):
    """
    Authentication error (invalid credentials, token expired, etc.).
    
    Attributes:
        account_email: Email of the account with auth issues
        reason: Specific reason for auth failure
    """
    
    def __init__(
        self, 
        message: str, 
        account_email: Optional[str] = None,
        reason: Optional[str] = None
    ):
        super().__init__(
            message, 
            code="AUTH_INVALID", 
            retryable=False,
            account_email=account_email,
            reason=reason
        )
        self.account_email = account_email
        self.reason = reason


class NoAccountsError(AntigravityError):
    """
    No accounts available error.
    
    Attributes:
        all_rate_limited: Whether all accounts are rate limited
    """
    
    def __init__(
        self, 
        message: str = "No accounts available", 
        all_rate_limited: bool = False
    ):
        super().__init__(
            message, 
            code="NO_ACCOUNTS", 
            retryable=all_rate_limited,
            all_rate_limited=all_rate_limited
        )
        self.all_rate_limited = all_rate_limited


class MaxRetriesError(AntigravityError):
    """
    Max retries exceeded error.
    
    Attributes:
        attempts: Number of attempts made
    """
    
    def __init__(self, message: str = "Max retries exceeded", attempts: int = 0):
        super().__init__(
            message, 
            code="MAX_RETRIES", 
            retryable=False,
            attempts=attempts
        )
        self.attempts = attempts


class ApiError(AntigravityError):
    """
    API error from upstream service.
    
    Attributes:
        status_code: HTTP status code
        error_type: Type of API error
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        error_type: str = "api_error"
    ):
        super().__init__(
            message, 
            code=error_type.upper(), 
            retryable=(status_code >= 500),
            status_code=status_code,
            error_type=error_type
        )
        self.status_code = status_code
        self.error_type = error_type


class EmptyResponseError(AntigravityError):
    """
    Empty response error - thrown when API returns no content.
    
    Used to trigger retry logic in streaming handler.
    """
    
    def __init__(self, message: str = "No content received from API"):
        super().__init__(message, code="EMPTY_RESPONSE", retryable=True)


# =============================================================================
# ERROR DETECTION HELPERS
# =============================================================================

def is_rate_limit_error(error: Exception) -> bool:
    """
    Check if an error is a rate limit error.
    Works with both custom error classes and legacy string-based errors.
    
    Args:
        error: Error to check
        
    Returns:
        True if it is a rate limit error
    """
    if isinstance(error, RateLimitError):
        return True
    msg = str(error).lower()
    return any(x in msg for x in [
        "429", 
        "resource_exhausted", 
        "quota_exhausted", 
        "rate limit"
    ])


def is_auth_error(error: Exception) -> bool:
    """
    Check if an error is an authentication error.
    Works with both custom error classes and legacy string-based errors.
    
    Args:
        error: Error to check
        
    Returns:
        True if it is an auth error
    """
    if isinstance(error, AuthError):
        return True
    msg = str(error).upper()
    return any(x in msg for x in [
        "AUTH_INVALID", 
        "INVALID_GRANT", 
        "TOKEN REFRESH FAILED",
        "401",
        "UNAUTHENTICATED"
    ])


def is_empty_response_error(error: Exception) -> bool:
    """
    Check if an error is an empty response error.
    
    Args:
        error: Error to check
        
    Returns:
        True if it is an empty response error
    """
    return isinstance(error, EmptyResponseError)


def is_network_error(error: Exception) -> bool:
    """
    Check if an error is a network error (transient).
    
    Args:
        error: Error to check
        
    Returns:
        True if it is a network error
    """
    msg = str(error).lower()
    return any(x in msg for x in [
        "fetch failed",
        "network error",
        "connection reset",
        "econnreset",
        "etimedout",
        "socket hang up",
        "timeout",
        "timed out",
        "connection refused",
        "econnrefused"
    ])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_duration(ms: int) -> str:
    """
    Format duration in milliseconds to human-readable string.
    
    Args:
        ms: Duration in milliseconds
        
    Returns:
        Human-readable duration (e.g., "1h23m45s")
    """
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h{minutes}m{secs}s"
    elif minutes > 0:
        return f"{minutes}m{secs}s"
    return f"{secs}s"


def format_duration_s(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Human-readable duration (e.g., "1h23m45s")
    """
    return format_duration(int(seconds * 1000))


async def sleep_ms(ms: int) -> None:
    """
    Async sleep for specified milliseconds.
    
    Args:
        ms: Duration to sleep in milliseconds
    """
    await asyncio.sleep(ms / 1000)


async def sleep_s(seconds: float) -> None:
    """
    Async sleep for specified seconds.
    
    Args:
        seconds: Duration to sleep in seconds
    """
    await asyncio.sleep(seconds)


def current_time_ms() -> int:
    """Get current time in milliseconds since epoch."""
    return int(datetime.now().timestamp() * 1000)


def current_time_s() -> float:
    """Get current time in seconds since epoch."""
    return datetime.now().timestamp()


# =============================================================================
# LOGGER
# =============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\x1b[0m"
    BRIGHT = "\x1b[1m"
    DIM = "\x1b[2m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"
    GRAY = "\x1b[90m"


class Logger:
    """
    Logger utility with colors and debug support.
    
    Provides structured logging with timestamps and colored output.
    Simple ANSI codes used to avoid dependencies.
    """
    
    def __init__(self):
        self._debug_enabled = False
    
    @property
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self._debug_enabled
    
    def set_debug(self, enabled: bool) -> None:
        """
        Set debug mode.
        
        Args:
            enabled: Whether to enable debug logging
        """
        self._debug_enabled = bool(enabled)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string in ISO format."""
        return datetime.now().isoformat()
    
    def _print(self, level: str, color: str, message: str, *args) -> None:
        """
        Format and print a log message.
        
        Format: [TIMESTAMP] [LEVEL] Message
        
        Args:
            level: Log level name
            color: ANSI color code
            message: Log message
            *args: Additional arguments to append
        """
        timestamp = f"{Colors.GRAY}[{self._get_timestamp()}]{Colors.RESET}"
        level_tag = f"{color}[{level}]{Colors.RESET}"
        
        # Format additional args
        extra = " ".join(str(arg) for arg in args) if args else ""
        full_message = f"{message} {extra}".strip()
        
        print(f"{timestamp} {level_tag} {full_message}", file=sys.stderr)
    
    def info(self, message: str, *args) -> None:
        """Standard info log."""
        self._print("INFO", Colors.BLUE, message, *args)
    
    def success(self, message: str, *args) -> None:
        """Success log."""
        self._print("SUCCESS", Colors.GREEN, message, *args)
    
    def warn(self, message: str, *args) -> None:
        """Warning log."""
        self._print("WARN", Colors.YELLOW, message, *args)
    
    def error(self, message: str, *args) -> None:
        """Error log."""
        self._print("ERROR", Colors.RED, message, *args)
    
    def debug(self, message: str, *args) -> None:
        """Debug log - only prints if debug mode is enabled."""
        if self._debug_enabled:
            self._print("DEBUG", Colors.MAGENTA, message, *args)
    
    def log(self, message: str, *args) -> None:
        """Direct log (for raw output) - proxied to stdout."""
        extra = " ".join(str(arg) for arg in args) if args else ""
        print(f"{message} {extra}".strip())
    
    def header(self, title: str) -> None:
        """Print a section header."""
        print(f"\n{Colors.BRIGHT}{Colors.CYAN}=== {title} ==={Colors.RESET}\n")


# Global logger singleton instance
logger = Logger()
