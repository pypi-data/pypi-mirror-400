"""
Antigravity Claude Proxy - Account Manager Module

Manages multiple Antigravity accounts with:
- Sticky selection for cache continuity
- Automatic failover on rate limits
- Smart cooldown for rate-limited accounts
- Model-specific rate limit tracking
- Credential management (OAuth tokens, project discovery)

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import json
import time
import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

from .config import (
    ACCOUNT_CONFIG_PATH,
    ANTIGRAVITY_DB_PATH,
    ANTIGRAVITY_ENDPOINT_FALLBACKS,
    ANTIGRAVITY_HEADERS,
    DEFAULT_PROJECT_ID,
    DEFAULT_COOLDOWN_MS,
    DEFAULT_COOLDOWN_S,
    MAX_WAIT_BEFORE_ERROR_MS,
    MAX_WAIT_BEFORE_ERROR_S,
    TOKEN_REFRESH_INTERVAL_S,
    format_duration,
    format_duration_s,
    is_network_error,
    logger
)
from .auth import (
    get_auth_status,
    refresh_access_token,
    DatabaseError
)

import aiohttp


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ModelRateLimit:
    """Rate limit state for a specific model."""
    is_rate_limited: bool = False
    reset_time: Optional[float] = None  # Unix timestamp in seconds


@dataclass
class Account:
    """
    Account data structure.
    
    Attributes:
        email: Account email address
        source: Account source ('oauth', 'database', 'manual')
        refresh_token: OAuth refresh token (for oauth source)
        api_key: API key (for manual source)
        project_id: Cloud project ID
        db_path: Custom database path (for database source)
        added_at: ISO timestamp when account was added
        last_used: Unix timestamp of last use
        is_invalid: Whether credentials are invalid
        invalid_reason: Reason for invalidation
        invalid_at: Unix timestamp when marked invalid
        model_rate_limits: Per-model rate limit state
    """
    email: str
    source: str = "oauth"
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    project_id: Optional[str] = None
    db_path: Optional[str] = None
    added_at: Optional[str] = None
    last_used: Optional[float] = None
    is_invalid: bool = False
    invalid_reason: Optional[str] = None
    invalid_at: Optional[float] = None
    model_rate_limits: Dict[str, ModelRateLimit] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "email": self.email,
            "source": self.source,
            "refreshToken": self.refresh_token,
            "apiKey": self.api_key,
            "projectId": self.project_id,
            "dbPath": self.db_path,
            "addedAt": self.added_at,
            "lastUsed": self.last_used,
            "isInvalid": self.is_invalid,
            "invalidReason": self.invalid_reason,
            "modelRateLimits": {
                model_id: {"isRateLimited": limit.is_rate_limited, "resetTime": limit.reset_time}
                for model_id, limit in self.model_rate_limits.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        """Create Account from dictionary (JSON deserialization)."""
        model_limits = {}
        raw_limits = data.get("modelRateLimits", {})
        for model_id, limit_data in raw_limits.items():
            model_limits[model_id] = ModelRateLimit(
                is_rate_limited=limit_data.get("isRateLimited", False),
                reset_time=limit_data.get("resetTime")
            )
        
        return cls(
            email=data["email"],
            source=data.get("source", "oauth"),
            refresh_token=data.get("refreshToken"),
            api_key=data.get("apiKey"),
            project_id=data.get("projectId"),
            db_path=data.get("dbPath"),
            added_at=data.get("addedAt"),
            last_used=data.get("lastUsed"),
            is_invalid=False,  # Reset on load - give accounts fresh chance
            invalid_reason=None,
            model_rate_limits=model_limits
        )


@dataclass
class TokenCacheEntry:
    """Cached token entry."""
    token: str
    extracted_at: float  # Unix timestamp


# =============================================================================
# STORAGE FUNCTIONS
# =============================================================================

def load_accounts_from_file(config_path: Path = ACCOUNT_CONFIG_PATH) -> Tuple[List[Account], Dict[str, Any], int]:
    """
    Load accounts from the config file.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Tuple of (accounts list, settings dict, active_index)
    """
    try:
        if not config_path.exists():
            logger.info("[AccountManager] No config file found. Using Antigravity database (single account mode)")
            return [], {}, 0
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        accounts = [Account.from_dict(acc) for acc in config.get("accounts", [])]
        settings = config.get("settings", {})
        active_index = config.get("activeIndex", 0)
        
        # Clamp active_index to valid range
        if active_index >= len(accounts):
            active_index = 0
        
        logger.info(f"[AccountManager] Loaded {len(accounts)} account(s) from config")
        
        return accounts, settings, active_index
        
    except Exception as e:
        logger.error(f"[AccountManager] Failed to load config: {e}")
        return [], {}, 0


def load_default_account(db_path: Optional[Path] = None) -> Tuple[List[Account], Dict[str, TokenCacheEntry]]:
    """
    Load the default account from Antigravity's database.
    
    Args:
        db_path: Optional path to the database
        
    Returns:
        Tuple of (accounts list, token_cache dict)
    """
    try:
        auth_data = get_auth_status(db_path)
        if auth_data.get("apiKey"):
            email = auth_data.get("email", "default@antigravity")
            account = Account(
                email=email,
                source="database",
            )
            
            token_cache = {
                email: TokenCacheEntry(
                    token=auth_data["apiKey"],
                    extracted_at=time.time()
                )
            }
            
            logger.info(f"[AccountManager] Loaded default account: {email}")
            
            return [account], token_cache
            
    except Exception as e:
        logger.error(f"[AccountManager] Failed to load default account: {e}")
    
    return [], {}


async def save_accounts_to_file(
    config_path: Path,
    accounts: List[Account],
    settings: Dict[str, Any],
    active_index: int
) -> None:
    """
    Save account configuration to disk.
    
    Args:
        config_path: Path to the config file
        accounts: List of Account objects
        settings: Settings dictionary
        active_index: Current active account index
    """
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "accounts": [acc.to_dict() for acc in accounts],
            "settings": settings,
            "activeIndex": active_index
        }
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            
    except Exception as e:
        logger.error(f"[AccountManager] Failed to save config: {e}")


# =============================================================================
# RATE LIMIT FUNCTIONS
# =============================================================================

def is_all_rate_limited(accounts: List[Account], model_id: Optional[str] = None) -> bool:
    """
    Check if all accounts are rate-limited for a specific model.
    
    Args:
        accounts: List of Account objects
        model_id: Model ID to check rate limits for
        
    Returns:
        True if all accounts are rate-limited or invalid
    """
    if not accounts:
        return True
    if not model_id:
        return False
    
    now = time.time()
    for acc in accounts:
        if acc.is_invalid:
            continue
        limit = acc.model_rate_limits.get(model_id)
        if not limit or not limit.is_rate_limited or (limit.reset_time and limit.reset_time <= now):
            return False
    return True


def get_available_accounts(accounts: List[Account], model_id: Optional[str] = None) -> List[Account]:
    """
    Get list of available (non-rate-limited, non-invalid) accounts for a model.
    
    Args:
        accounts: List of Account objects
        model_id: Model ID to filter by
        
    Returns:
        List of available Account objects
    """
    now = time.time()
    available = []
    
    for acc in accounts:
        if acc.is_invalid:
            continue
        
        if model_id:
            limit = acc.model_rate_limits.get(model_id)
            if limit and limit.is_rate_limited and limit.reset_time and limit.reset_time > now:
                continue
        
        available.append(acc)
    
    return available


def get_invalid_accounts(accounts: List[Account]) -> List[Account]:
    """Get list of invalid accounts."""
    return [acc for acc in accounts if acc.is_invalid]


def clear_expired_limits(accounts: List[Account]) -> int:
    """
    Clear expired rate limits.
    
    Args:
        accounts: List of Account objects
        
    Returns:
        Number of rate limits cleared
    """
    now = time.time()
    cleared = 0
    
    for account in accounts:
        for model_id, limit in list(account.model_rate_limits.items()):
            if limit.is_rate_limited and limit.reset_time and limit.reset_time <= now:
                limit.is_rate_limited = False
                limit.reset_time = None
                cleared += 1
                logger.success(f"[AccountManager] Rate limit expired for: {account.email} (model: {model_id})")
    
    return cleared


def reset_all_rate_limits(accounts: List[Account]) -> None:
    """
    Clear all rate limits to force a fresh check (optimistic retry strategy).
    
    Args:
        accounts: List of Account objects
    """
    for account in accounts:
        for model_id in list(account.model_rate_limits.keys()):
            account.model_rate_limits[model_id] = ModelRateLimit()
    logger.warn("[AccountManager] Reset all rate limits for optimistic retry")


def mark_rate_limited(
    accounts: List[Account],
    email: str,
    reset_ms: Optional[int] = None,
    settings: Optional[Dict[str, Any]] = None,
    model_id: Optional[str] = None
) -> bool:
    """
    Mark an account as rate-limited for a specific model.
    
    Args:
        accounts: List of Account objects
        email: Email of the account to mark
        reset_ms: Time in ms until rate limit resets
        settings: Settings dict with cooldownDurationMs
        model_id: Model ID to mark rate limit for
        
    Returns:
        True if account was found and marked
    """
    account = next((a for a in accounts if a.email == email), None)
    if not account or not model_id:
        return False
    
    settings = settings or {}
    cooldown_ms = reset_ms or settings.get("cooldownDurationMs", DEFAULT_COOLDOWN_MS)
    reset_time = time.time() + (cooldown_ms / 1000)
    
    account.model_rate_limits[model_id] = ModelRateLimit(
        is_rate_limited=True,
        reset_time=reset_time
    )
    
    logger.warn(
        f"[AccountManager] Rate limited: {email} (model: {model_id}). "
        f"Available in {format_duration(cooldown_ms)}"
    )
    
    return True


def mark_invalid(accounts: List[Account], email: str, reason: str = "Unknown error") -> bool:
    """
    Mark an account as invalid (credentials need re-authentication).
    
    Args:
        accounts: List of Account objects
        email: Email of the account to mark
        reason: Reason for marking as invalid
        
    Returns:
        True if account was found and marked
    """
    account = next((a for a in accounts if a.email == email), None)
    if not account:
        return False
    
    account.is_invalid = True
    account.invalid_reason = reason
    account.invalid_at = time.time()
    
    logger.error(f"[AccountManager] ⚠ Account INVALID: {email}")
    logger.error(f"[AccountManager]   Reason: {reason}")
    logger.error(f"[AccountManager]   Run 'python -m antigravity_proxy accounts' to re-authenticate")
    
    return True


def get_min_wait_time_ms(accounts: List[Account], model_id: Optional[str] = None) -> int:
    """
    Get the minimum wait time until any account becomes available for a model.
    
    Args:
        accounts: List of Account objects
        model_id: Model ID to check
        
    Returns:
        Wait time in milliseconds
    """
    if not is_all_rate_limited(accounts, model_id):
        return 0
    
    now = time.time()
    min_wait_s = float("inf")
    soonest_account = None
    
    for account in accounts:
        if account.is_invalid:
            continue
        if model_id:
            limit = account.model_rate_limits.get(model_id)
            if limit and limit.is_rate_limited and limit.reset_time:
                wait_s = limit.reset_time - now
                if 0 < wait_s < min_wait_s:
                    min_wait_s = wait_s
                    soonest_account = account
    
    if soonest_account:
        logger.info(
            f"[AccountManager] Shortest wait: {format_duration_s(min_wait_s)} "
            f"(account: {soonest_account.email})"
        )
    
    if min_wait_s == float("inf"):
        return DEFAULT_COOLDOWN_MS
    
    return int(min_wait_s * 1000)


# =============================================================================
# SELECTION FUNCTIONS
# =============================================================================

def is_account_usable(account: Optional[Account], model_id: Optional[str] = None) -> bool:
    """
    Check if an account is usable for a specific model.
    
    Args:
        account: Account to check
        model_id: Model ID to check
        
    Returns:
        True if account is usable
    """
    if not account or account.is_invalid:
        return False
    
    if model_id:
        limit = account.model_rate_limits.get(model_id)
        if limit and limit.is_rate_limited and limit.reset_time and limit.reset_time > time.time():
            return False
    
    return True


def pick_next(
    accounts: List[Account],
    current_index: int,
    model_id: Optional[str] = None
) -> Tuple[Optional[Account], int]:
    """
    Pick the next available account (fallback when current is unavailable).
    
    Args:
        accounts: List of Account objects
        current_index: Current account index
        model_id: Model ID to check rate limits for
        
    Returns:
        Tuple of (next available account or None, new index)
    """
    clear_expired_limits(accounts)
    
    available = get_available_accounts(accounts, model_id)
    if not available:
        return None, current_index
    
    # Clamp index to valid range
    index = current_index
    if index >= len(accounts):
        index = 0
    
    # Find next available account starting from index AFTER current
    for i in range(1, len(accounts) + 1):
        idx = (index + i) % len(accounts)
        account = accounts[idx]
        
        if is_account_usable(account, model_id):
            account.last_used = time.time()
            
            position = idx + 1
            total = len(accounts)
            logger.info(f"[AccountManager] Using account: {account.email} ({position}/{total})")
            
            return account, idx
    
    return None, current_index


def get_current_sticky_account(
    accounts: List[Account],
    current_index: int,
    model_id: Optional[str] = None
) -> Tuple[Optional[Account], int]:
    """
    Get the current account without advancing the index (sticky selection).
    
    Args:
        accounts: List of Account objects
        current_index: Current account index
        model_id: Model ID to check rate limits for
        
    Returns:
        Tuple of (current account or None, index)
    """
    clear_expired_limits(accounts)
    
    if not accounts:
        return None, current_index
    
    # Clamp index to valid range
    index = current_index
    if index >= len(accounts):
        index = 0
    
    # Get current account directly
    account = accounts[index]
    
    if is_account_usable(account, model_id):
        account.last_used = time.time()
        return account, index
    
    return None, index


def should_wait_for_current_account(
    accounts: List[Account],
    current_index: int,
    model_id: Optional[str] = None
) -> Tuple[bool, int, Optional[Account]]:
    """
    Check if we should wait for the current account's rate limit to reset.
    
    Args:
        accounts: List of Account objects
        current_index: Current account index
        model_id: Model ID to check rate limits for
        
    Returns:
        Tuple of (should_wait, wait_ms, account)
    """
    if not accounts:
        return False, 0, None
    
    # Clamp index
    index = current_index
    if index >= len(accounts):
        index = 0
    
    account = accounts[index]
    
    if not account or account.is_invalid:
        return False, 0, None
    
    wait_ms = 0
    
    if model_id:
        limit = account.model_rate_limits.get(model_id)
        if limit and limit.is_rate_limited and limit.reset_time:
            wait_s = limit.reset_time - time.time()
            wait_ms = int(wait_s * 1000) if wait_s > 0 else 0
    
    # If wait time is within threshold, recommend waiting
    if wait_ms > 0 and wait_ms <= MAX_WAIT_BEFORE_ERROR_MS:
        return True, wait_ms, account
    
    return False, 0, None


def pick_sticky_account(
    accounts: List[Account],
    current_index: int,
    model_id: Optional[str] = None
) -> Tuple[Optional[Account], int, int]:
    """
    Pick an account with sticky selection preference.
    Prefers the current account for cache continuity.
    
    Args:
        accounts: List of Account objects
        current_index: Current account index
        model_id: Model ID to check rate limits for
        
    Returns:
        Tuple of (account or None, wait_ms, new_index)
    """
    # First try to get the current sticky account
    sticky_account, sticky_index = get_current_sticky_account(accounts, current_index, model_id)
    if sticky_account:
        return sticky_account, 0, sticky_index
    
    # Current account is rate-limited or invalid.
    # CHECK IF OTHERS ARE AVAILABLE before deciding to wait.
    available = get_available_accounts(accounts, model_id)
    if available:
        # Found a free account! Switch immediately.
        next_account, new_index = pick_next(accounts, current_index, model_id)
        if next_account:
            logger.info(f"[AccountManager] Switched to new account (failover): {next_account.email}")
            return next_account, 0, new_index
    
    # No other accounts available. Now check if we should wait for current account.
    should_wait, wait_ms, wait_account = should_wait_for_current_account(accounts, current_index, model_id)
    if should_wait:
        logger.info(
            f"[AccountManager] Waiting {format_duration(wait_ms)} for sticky account: {wait_account.email}"
        )
        return None, wait_ms, current_index
    
    # Current account unavailable for too long/invalid, and no others available?
    next_account, new_index = pick_next(accounts, current_index, model_id)
    if next_account:
        logger.info(f"[AccountManager] Switched to new account for cache: {next_account.email}")
    return next_account, 0, new_index


# =============================================================================
# CREDENTIALS FUNCTIONS
# =============================================================================

async def get_token_for_account(
    account: Account,
    token_cache: Dict[str, TokenCacheEntry],
    on_invalid: Optional[callable] = None,
    on_save: Optional[callable] = None
) -> str:
    """
    Get OAuth token for an account.
    
    Args:
        account: Account object
        token_cache: Token cache dictionary
        on_invalid: Callback when account is invalid (email, reason)
        on_save: Callback to save changes
        
    Returns:
        OAuth access token
        
    Raises:
        ValueError: If token refresh fails
    """
    # Check cache first
    cached = token_cache.get(account.email)
    if cached and (time.time() - cached.extracted_at) < TOKEN_REFRESH_INTERVAL_S:
        return cached.token
    
    token = None
    
    if account.source == "oauth" and account.refresh_token:
        # OAuth account - use refresh token
        try:
            tokens = await refresh_access_token(account.refresh_token)
            token = tokens["access_token"]
            # Clear invalid flag on success
            if account.is_invalid:
                account.is_invalid = False
                account.invalid_reason = None
                if on_save:
                    await on_save()
            logger.success(f"[AccountManager] Refreshed OAuth token for: {account.email}")
        except Exception as e:
            # Check if it's a transient network error
            if is_network_error(e):
                logger.warn(
                    f"[AccountManager] Failed to refresh token for {account.email} "
                    f"due to network error: {e}"
                )
                raise ValueError(f"AUTH_NETWORK_ERROR: {e}")
            
            logger.error(f"[AccountManager] Failed to refresh token for {account.email}: {e}")
            if on_invalid:
                on_invalid(account.email, str(e))
            raise ValueError(f"AUTH_INVALID: {account.email}: {e}")
            
    elif account.source == "manual" and account.api_key:
        token = account.api_key
    else:
        # Extract from database
        db_path = Path(account.db_path) if account.db_path else ANTIGRAVITY_DB_PATH
        auth_data = get_auth_status(db_path)
        token = auth_data["apiKey"]
    
    # Cache the token
    token_cache[account.email] = TokenCacheEntry(
        token=token,
        extracted_at=time.time()
    )
    
    return token


async def get_project_for_account(
    account: Account,
    token: str,
    project_cache: Dict[str, str]
) -> str:
    """
    Get project ID for an account.
    
    Args:
        account: Account object
        token: OAuth access token
        project_cache: Project cache dictionary
        
    Returns:
        Project ID
    """
    # Check cache first
    cached = project_cache.get(account.email)
    if cached:
        return cached
    
    # OAuth or manual accounts may have projectId specified
    if account.project_id:
        project_cache[account.email] = account.project_id
        return account.project_id
    
    # Discover project via loadCodeAssist API
    project = await discover_project(token)
    project_cache[account.email] = project
    return project


async def discover_project(token: str) -> str:
    """
    Discover project ID via Cloud Code API.
    
    Args:
        token: OAuth access token
        
    Returns:
        Project ID
    """
    headers = {
        "Authorization": f"Bearer {token}",
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
                        error_text = await response.text()
                        logger.warn(
                            f"[AccountManager] Project discovery failed at {endpoint}: "
                            f"{response.status} - {error_text}"
                        )
                        continue
                    
                    data = await response.json()
                    
                    project = data.get("cloudaicompanionProject")
                    if isinstance(project, str):
                        logger.success(f"[AccountManager] Discovered project: {project}")
                        return project
                    if isinstance(project, dict) and project.get("id"):
                        logger.success(f"[AccountManager] Discovered project: {project['id']}")
                        return project["id"]
                        
            except Exception as e:
                logger.warn(f"[AccountManager] Project discovery failed at {endpoint}: {e}")
    
    logger.warn(
        f"[AccountManager] Project discovery failed for all endpoints. "
        f"Using default project: {DEFAULT_PROJECT_ID}"
    )
    logger.warn(
        "[AccountManager] If you see 404 errors, your account may not have Gemini Code Assist enabled."
    )
    return DEFAULT_PROJECT_ID


# =============================================================================
# ACCOUNT MANAGER CLASS
# =============================================================================

class AccountManager:
    """
    Account Manager for Antigravity Claude Proxy.
    
    Manages multiple accounts with sticky selection, automatic failover,
    and smart cooldown for rate-limited accounts.
    """
    
    def __init__(self, config_path: Path = ACCOUNT_CONFIG_PATH):
        self._accounts: List[Account] = []
        self._current_index: int = 0
        self._config_path = config_path
        self._settings: Dict[str, Any] = {}
        self._initialized = False
        
        # Per-account caches
        self._token_cache: Dict[str, TokenCacheEntry] = {}
        self._project_cache: Dict[str, str] = {}
    
    async def initialize(self) -> None:
        """Initialize the account manager by loading config."""
        if self._initialized:
            return
        
        accounts, settings, active_index = load_accounts_from_file(self._config_path)
        
        self._accounts = accounts
        self._settings = settings
        self._current_index = active_index
        
        # If config exists but has no accounts, fall back to Antigravity database
        if not self._accounts:
            logger.warn("[AccountManager] No accounts in config. Falling back to Antigravity database")
            default_accounts, token_cache = load_default_account()
            self._accounts = default_accounts
            self._token_cache = token_cache
        
        # Clear any expired rate limits
        self.clear_expired_limits()
        
        self._initialized = True
    
    def get_account_count(self) -> int:
        """Get the number of accounts."""
        return len(self._accounts)
    
    def is_all_rate_limited(self, model_id: Optional[str] = None) -> bool:
        """Check if all accounts are rate-limited for a model."""
        return is_all_rate_limited(self._accounts, model_id)
    
    def get_available_accounts(self, model_id: Optional[str] = None) -> List[Account]:
        """Get list of available accounts."""
        return get_available_accounts(self._accounts, model_id)
    
    def get_invalid_accounts(self) -> List[Account]:
        """Get list of invalid accounts."""
        return get_invalid_accounts(self._accounts)
    
    def clear_expired_limits(self) -> int:
        """Clear expired rate limits."""
        cleared = clear_expired_limits(self._accounts)
        if cleared > 0:
            asyncio.create_task(self._save_to_disk())
        return cleared
    
    def reset_all_rate_limits(self) -> None:
        """Clear all rate limits for optimistic retry."""
        reset_all_rate_limits(self._accounts)
    
    def pick_next(self, model_id: Optional[str] = None) -> Optional[Account]:
        """Pick the next available account."""
        account, new_index = pick_next(self._accounts, self._current_index, model_id)
        self._current_index = new_index
        if account:
            asyncio.create_task(self._save_to_disk())
        return account
    
    def get_current_sticky_account(self, model_id: Optional[str] = None) -> Optional[Account]:
        """Get current account without advancing index."""
        account, new_index = get_current_sticky_account(self._accounts, self._current_index, model_id)
        self._current_index = new_index
        if account:
            asyncio.create_task(self._save_to_disk())
        return account
    
    def should_wait_for_current_account(self, model_id: Optional[str] = None) -> Tuple[bool, int, Optional[Account]]:
        """Check if we should wait for current account."""
        return should_wait_for_current_account(self._accounts, self._current_index, model_id)
    
    def pick_sticky_account(self, model_id: Optional[str] = None) -> Tuple[Optional[Account], int]:
        """Pick account with sticky selection preference."""
        account, wait_ms, new_index = pick_sticky_account(self._accounts, self._current_index, model_id)
        self._current_index = new_index
        if account:
            asyncio.create_task(self._save_to_disk())
        return account, wait_ms
    
    def mark_rate_limited(self, email: str, reset_ms: Optional[int] = None, model_id: Optional[str] = None) -> None:
        """Mark an account as rate-limited."""
        mark_rate_limited(self._accounts, email, reset_ms, self._settings, model_id)
        asyncio.create_task(self._save_to_disk())
    
    def mark_invalid(self, email: str, reason: str = "Unknown error") -> None:
        """Mark an account as invalid."""
        mark_invalid(self._accounts, email, reason)
        asyncio.create_task(self._save_to_disk())
    
    def get_min_wait_time_ms(self, model_id: Optional[str] = None) -> int:
        """Get minimum wait time until any account becomes available."""
        return get_min_wait_time_ms(self._accounts, model_id)
    
    async def get_token_for_account(self, account: Account) -> str:
        """Get OAuth token for an account."""
        return await get_token_for_account(
            account,
            self._token_cache,
            on_invalid=lambda email, reason: self.mark_invalid(email, reason),
            on_save=self._save_to_disk
        )
    
    async def get_project_for_account(self, account: Account, token: str) -> str:
        """Get project ID for an account."""
        return await get_project_for_account(account, token, self._project_cache)
    
    def clear_project_cache(self, email: Optional[str] = None) -> None:
        """Clear project cache."""
        if email:
            self._project_cache.pop(email, None)
        else:
            self._project_cache.clear()
    
    def clear_token_cache(self, email: Optional[str] = None) -> None:
        """Clear token cache."""
        if email:
            self._token_cache.pop(email, None)
        else:
            self._token_cache.clear()
    
    async def _save_to_disk(self) -> None:
        """Save current state to disk."""
        await save_accounts_to_file(
            self._config_path,
            self._accounts,
            self._settings,
            self._current_index
        )
    
    async def save_to_disk(self) -> None:
        """Public method to save state."""
        await self._save_to_disk()
    
    def get_status(self) -> Dict[str, Any]:
        """Get status object for logging/API."""
        available = self.get_available_accounts()
        invalid = self.get_invalid_accounts()
        
        # Count accounts with any active model-specific rate limits
        now = time.time()
        rate_limited = [
            a for a in self._accounts
            if any(
                limit.is_rate_limited and limit.reset_time and limit.reset_time > now
                for limit in a.model_rate_limits.values()
            )
        ]
        
        return {
            "total": len(self._accounts),
            "available": len(available),
            "rateLimited": len(rate_limited),
            "invalid": len(invalid),
            "summary": (
                f"{len(self._accounts)} total, {len(available)} available, "
                f"{len(rate_limited)} rate-limited, {len(invalid)} invalid"
            ),
            "accounts": [
                {
                    "email": a.email,
                    "source": a.source,
                    "modelRateLimits": {
                        model_id: {"isRateLimited": limit.is_rate_limited, "resetTime": limit.reset_time}
                        for model_id, limit in a.model_rate_limits.items()
                    },
                    "isInvalid": a.is_invalid,
                    "invalidReason": a.invalid_reason,
                    "lastUsed": a.last_used
                }
                for a in self._accounts
            ]
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """Get settings."""
        return dict(self._settings)
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts (internal use for quota fetching)."""
        return self._accounts
