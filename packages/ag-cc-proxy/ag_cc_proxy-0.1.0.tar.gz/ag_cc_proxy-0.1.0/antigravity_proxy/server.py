"""
Antigravity Claude Proxy - Web Server Module

Express-compatible aiohttp API server that proxies Anthropic Messages API
to Google Cloud Code via Antigravity.

Endpoints:
- POST /v1/messages        - Anthropic Messages API (streaming and non-streaming)
- GET  /v1/models          - List available models
- GET  /health             - Health check with detailed status
- GET  /account-limits     - Account status & quotas
- POST /refresh-token      - Force token refresh

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import os
import sys
import json
import asyncio
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

from aiohttp import web

from .config import (
    DEFAULT_PORT,
    REQUEST_BODY_LIMIT,
    ACCOUNT_CONFIG_PATH,
    format_duration,
    logger
)
from .accounts import AccountManager
from .auth import token_extractor
from .cloudcode import (
    send_message,
    send_message_stream,
    list_models,
    get_model_quotas
)


# =============================================================================
# GLOBALS
# =============================================================================

# Account manager instance (initialized on first request or startup)
account_manager: Optional[AccountManager] = None

# Initialization state
is_initialized = False
init_error: Optional[Exception] = None
init_lock = asyncio.Lock()

# Runtime flags (set from command line)
FALLBACK_ENABLED = False
DEBUG_ENABLED = False


# =============================================================================
# INITIALIZATION
# =============================================================================

async def ensure_initialized() -> None:
    """
    Ensure account manager is initialized (with race condition protection).
    """
    global account_manager, is_initialized, init_error
    
    if is_initialized:
        return
    
    async with init_lock:
        # Double-check after acquiring lock
        if is_initialized:
            return
        
        try:
            account_manager = AccountManager(ACCOUNT_CONFIG_PATH)
            await account_manager.initialize()
            is_initialized = True
            status = account_manager.get_status()
            logger.success(f"[Server] Account pool initialized: {status['summary']}")
        except Exception as e:
            init_error = e
            logger.error(f"[Server] Failed to initialize account manager: {e}")
            raise


# =============================================================================
# ERROR PARSING
# =============================================================================

def parse_error(error: Exception) -> Dict[str, Any]:
    """
    Parse error message to extract error type, status code, and user-friendly message.
    
    Args:
        error: The exception to parse
        
    Returns:
        Dict with 'error_type', 'status_code', 'error_message'
    """
    error_type = "api_error"
    status_code = 500
    error_message = str(error)
    
    msg = error_message.lower()
    msg_upper = error_message.upper()
    
    if "401" in msg or "unauthenticated" in msg:
        error_type = "authentication_error"
        status_code = 401
        error_message = "Authentication failed. Make sure Antigravity is running with a valid token."
        
    elif "429" in msg or "resource_exhausted" in msg_upper or "quota_exhausted" in msg_upper:
        error_type = "invalid_request_error"  # Force client to purge/stop
        status_code = 400  # Use 400 to ensure client does not retry
        
        # Try to extract the quota reset time from the error
        reset_match = re.search(r'quota will reset after ([\dh\dm\ds]+)', error_message, re.IGNORECASE)
        # Try to extract model from our error format
        model_match = re.search(r'Rate limited on ([^.]+)\.', error_message) or \
                      re.search(r'"model":\s*"([^"]+)"', error_message)
        model = model_match.group(1) if model_match else "the model"
        
        if reset_match:
            error_message = f"You have exhausted your capacity on {model}. Quota will reset after {reset_match.group(1)}."
        else:
            error_message = f"You have exhausted your capacity on {model}. Please wait for your quota to reset."
            
    elif "invalid_request_error" in msg or "invalid_argument" in msg_upper:
        error_type = "invalid_request_error"
        status_code = 400
        msg_match = re.search(r'"message":"([^"]+)"', error_message)
        if msg_match:
            error_message = msg_match.group(1)
            
    elif "all endpoints failed" in msg:
        error_type = "api_error"
        status_code = 503
        error_message = "Unable to connect to Claude API. Check that Antigravity is running."
        
    elif "permission_denied" in msg_upper:
        error_type = "permission_error"
        status_code = 403
        error_message = "Permission denied. Check your Antigravity license."
    
    return {
        "error_type": error_type,
        "status_code": status_code,
        "error_message": error_message
    }


# =============================================================================
# MIDDLEWARE
# =============================================================================

@web.middleware
async def cors_middleware(request: web.Request, handler) -> web.Response:
    """CORS middleware - allows all origins."""
    # Handle preflight requests
    if request.method == "OPTIONS":
        return web.Response(
            status=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-API-Key, anthropic-version",
                "Access-Control-Max-Age": "86400"
            }
        )
    
    # Process request
    response = await handler(request)
    
    # Add CORS headers to response
    response.headers["Access-Control-Allow-Origin"] = "*"
    
    return response


@web.middleware
async def logging_middleware(request: web.Request, handler) -> web.Response:
    """Request logging middleware."""
    path = request.path
    method = request.method
    
    # Skip logging for event logging batch unless in debug mode
    if path == "/api/event_logging/batch":
        if logger.is_debug_enabled:
            logger.debug(f"[{method}] {path}")
    else:
        logger.info(f"[{method}] {path}")
    
    return await handler(request)


@web.middleware
async def error_middleware(request: web.Request, handler) -> web.Response:
    """Global error handling middleware."""
    try:
        return await handler(request)
    except web.HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Server] Unhandled error: {e}")
        parsed = parse_error(e)
        return web.json_response(
            {
                "type": "error",
                "error": {
                    "type": parsed["error_type"],
                    "message": parsed["error_message"]
                }
            },
            status=parsed["status_code"]
        )


# =============================================================================
# ROUTE HANDLERS
# =============================================================================

async def health_handler(request: web.Request) -> web.Response:
    """
    Health check endpoint - Detailed status.
    Returns status of all accounts including rate limits and model quotas.
    """
    try:
        await ensure_initialized()
        start_time = datetime.now()
        
        # Get high-level status first
        status = account_manager.get_status()
        all_accounts = account_manager.get_all_accounts()
        
        # Fetch quotas for each account in parallel
        async def get_account_details(account):
            # Check model-specific rate limits
            import time
            now = time.time()
            active_model_limits = [
                (model_id, limit)
                for model_id, limit in account.model_rate_limits.items()
                if limit.is_rate_limited and limit.reset_time and limit.reset_time > now
            ]
            is_rate_limited = len(active_model_limits) > 0
            soonest_reset = min(
                (limit.reset_time for _, limit in active_model_limits),
                default=None
            ) if active_model_limits else None
            
            base_info = {
                "email": account.email,
                "lastUsed": datetime.fromtimestamp(account.last_used).isoformat() if account.last_used else None,
                "modelRateLimits": {
                    model_id: {"isRateLimited": limit.is_rate_limited, "resetTime": limit.reset_time}
                    for model_id, limit in account.model_rate_limits.items()
                },
                "rateLimitCooldownRemaining": max(0, int((soonest_reset - now) * 1000)) if soonest_reset else 0
            }
            
            # Skip invalid accounts for quota check
            if account.is_invalid:
                return {
                    **base_info,
                    "status": "invalid",
                    "error": account.invalid_reason,
                    "models": {}
                }
            
            try:
                token = await account_manager.get_token_for_account(account)
                quotas = await get_model_quotas(token)
                
                # Format quotas for readability
                formatted_quotas = {}
                for model_id, info in quotas.items():
                    remaining = info.get("remainingFraction")
                    formatted_quotas[model_id] = {
                        "remaining": f"{int(remaining * 100)}%" if remaining is not None else "N/A",
                        "remainingFraction": remaining,
                        "resetTime": info.get("resetTime")
                    }
                
                return {
                    **base_info,
                    "status": "rate-limited" if is_rate_limited else "ok",
                    "models": formatted_quotas
                }
            except Exception as e:
                return {
                    **base_info,
                    "status": "error",
                    "error": str(e),
                    "models": {}
                }
        
        # Gather all account details
        account_details = await asyncio.gather(
            *[get_account_details(acc) for acc in all_accounts],
            return_exceptions=True
        )
        
        # Process results
        detailed_accounts = []
        for i, result in enumerate(account_details):
            if isinstance(result, Exception):
                acc = all_accounts[i]
                detailed_accounts.append({
                    "email": acc.email,
                    "status": "error",
                    "error": str(result),
                    "modelRateLimits": {
                        model_id: {"isRateLimited": limit.is_rate_limited, "resetTime": limit.reset_time}
                        for model_id, limit in acc.model_rate_limits.items()
                    }
                })
            else:
                detailed_accounts.append(result)
        
        latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return web.json_response({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "latencyMs": latency_ms,
            "summary": status["summary"],
            "counts": {
                "total": status["total"],
                "available": status["available"],
                "rateLimited": status["rateLimited"],
                "invalid": status["invalid"]
            },
            "accounts": detailed_accounts
        })
        
    except Exception as e:
        logger.error(f"[API] Health check failed: {e}")
        return web.json_response(
            {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            status=503
        )


async def account_limits_handler(request: web.Request) -> web.Response:
    """
    Account limits endpoint - fetch quota/limits for all accounts × all models.
    Returns a table showing remaining quota and reset time for each combination.
    Use ?format=table for ASCII table output, default is JSON.
    """
    try:
        await ensure_initialized()
        all_accounts = account_manager.get_all_accounts()
        output_format = request.query.get("format", "json")
        
        # Fetch quotas for each account in parallel
        async def get_account_quotas(account):
            if account.is_invalid:
                return {
                    "email": account.email,
                    "status": "invalid",
                    "error": account.invalid_reason,
                    "models": {}
                }
            
            try:
                token = await account_manager.get_token_for_account(account)
                quotas = await get_model_quotas(token)
                return {
                    "email": account.email,
                    "status": "ok",
                    "models": quotas
                }
            except Exception as e:
                return {
                    "email": account.email,
                    "status": "error",
                    "error": str(e),
                    "models": {}
                }
        
        results = await asyncio.gather(
            *[get_account_quotas(acc) for acc in all_accounts],
            return_exceptions=True
        )
        
        # Process results
        account_limits = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                account_limits.append({
                    "email": all_accounts[i].email,
                    "status": "error",
                    "error": str(result),
                    "models": {}
                })
            else:
                account_limits.append(result)
        
        # Collect all unique model IDs
        all_model_ids = set()
        for acc in account_limits:
            all_model_ids.update(acc.get("models", {}).keys())
        sorted_models = sorted(all_model_ids)
        
        # Return ASCII table format
        if output_format == "table":
            lines = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"Account Limits ({timestamp})")
            
            # Get account status info
            status = account_manager.get_status()
            lines.append(
                f"Accounts: {status['total']} total, {status['available']} available, "
                f"{status['rateLimited']} rate-limited, {status['invalid']} invalid"
            )
            lines.append("")
            
            # Table 1: Account status
            acc_col_width = 25
            status_col_width = 15
            last_used_col_width = 25
            reset_col_width = 25
            
            header = (
                "Account".ljust(acc_col_width) +
                "Status".ljust(status_col_width) +
                "Last Used".ljust(last_used_col_width) +
                "Quota Reset"
            )
            lines.append(header)
            lines.append("─" * (acc_col_width + status_col_width + last_used_col_width + reset_col_width))
            
            for acc_status in status["accounts"]:
                short_email = acc_status["email"].split("@")[0][:22]
                last_used = (
                    datetime.fromtimestamp(acc_status["lastUsed"]).strftime("%Y-%m-%d %H:%M:%S")
                    if acc_status.get("lastUsed") else "never"
                )
                
                # Get status and error from account_limits
                acc_limit = next((a for a in account_limits if a["email"] == acc_status["email"]), None)
                
                if acc_status.get("isInvalid"):
                    acc_status_str = "invalid"
                elif acc_limit and acc_limit.get("status") == "error":
                    acc_status_str = "error"
                else:
                    # Count exhausted models
                    models = acc_limit.get("models", {}) if acc_limit else {}
                    model_count = len(models)
                    exhausted_count = sum(
                        1 for q in models.values()
                        if q.get("remainingFraction") == 0 or q.get("remainingFraction") is None
                    )
                    
                    if exhausted_count == 0:
                        acc_status_str = "ok"
                    else:
                        acc_status_str = f"({exhausted_count}/{model_count}) limited"
                
                # Get reset time from quota API
                claude_model = next((m for m in sorted_models if "claude" in m.lower()), None)
                quota = acc_limit.get("models", {}).get(claude_model) if claude_model and acc_limit else None
                reset_time = (
                    datetime.fromisoformat(quota["resetTime"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
                    if quota and quota.get("resetTime") else "-"
                )
                
                row = (
                    short_email.ljust(acc_col_width) +
                    acc_status_str.ljust(status_col_width) +
                    last_used.ljust(last_used_col_width) +
                    reset_time
                )
                
                if acc_limit and acc_limit.get("error"):
                    lines.append(row)
                    lines.append(f"  └─ {acc_limit['error']}")
                else:
                    lines.append(row)
            
            lines.append("")
            
            # Table 2: Model quotas
            model_col_width = max(28, max((len(m) for m in sorted_models), default=0)) + 2
            account_col_width = 30
            
            header = "Model".ljust(model_col_width)
            for acc in account_limits:
                short_email = acc["email"].split("@")[0][:26]
                header += short_email.ljust(account_col_width)
            lines.append(header)
            lines.append("─" * (model_col_width + len(account_limits) * account_col_width))
            
            for model_id in sorted_models:
                row = model_id.ljust(model_col_width)
                for acc in account_limits:
                    quota = acc.get("models", {}).get(model_id)
                    
                    if acc["status"] not in ("ok", "rate-limited"):
                        cell = f"[{acc['status']}]"
                    elif not quota:
                        cell = "-"
                    elif quota.get("remainingFraction") == 0 or quota.get("remainingFraction") is None:
                        # Show reset time for exhausted models
                        if quota.get("resetTime"):
                            try:
                                reset_dt = datetime.fromisoformat(quota["resetTime"].replace("Z", "+00:00"))
                                reset_ms = int((reset_dt.timestamp() - datetime.now().timestamp()) * 1000)
                                if reset_ms > 0:
                                    cell = f"0% (wait {format_duration(reset_ms)})"
                                else:
                                    cell = "0% (resetting...)"
                            except Exception:
                                cell = "0% (exhausted)"
                        else:
                            cell = "0% (exhausted)"
                    else:
                        pct = int(quota["remainingFraction"] * 100)
                        cell = f"{pct}%"
                    
                    row += cell.ljust(account_col_width)
                lines.append(row)
            
            return web.Response(
                text="\n".join(lines),
                content_type="text/plain; charset=utf-8"
            )
        
        # Default: JSON format
        return web.json_response({
            "timestamp": datetime.now().isoformat(),
            "totalAccounts": len(all_accounts),
            "models": sorted_models,
            "accounts": [
                {
                    "email": acc["email"],
                    "status": acc["status"],
                    "error": acc.get("error"),
                    "limits": {
                        model_id: {
                            "remaining": (
                                f"{int(quota['remainingFraction'] * 100)}%"
                                if quota and quota.get("remainingFraction") is not None
                                else "N/A"
                            ),
                            "remainingFraction": quota.get("remainingFraction") if quota else None,
                            "resetTime": quota.get("resetTime") if quota else None
                        }
                        for model_id in sorted_models
                        for quota in [acc.get("models", {}).get(model_id)]
                    }
                }
                for acc in account_limits
            ]
        })
        
    except Exception as e:
        return web.json_response(
            {"status": "error", "error": str(e)},
            status=500
        )


async def refresh_token_handler(request: web.Request) -> web.Response:
    """Force token refresh endpoint."""
    try:
        await ensure_initialized()
        
        # Clear all caches
        account_manager.clear_token_cache()
        account_manager.clear_project_cache()
        
        # Force refresh default token
        token = await token_extractor.force_refresh()
        
        return web.json_response({
            "status": "ok",
            "message": "Token caches cleared and refreshed",
            "tokenPrefix": token[:10] + "..."
        })
    except Exception as e:
        return web.json_response(
            {"status": "error", "error": str(e)},
            status=500
        )


async def list_models_handler(request: web.Request) -> web.Response:
    """List models endpoint (OpenAI-compatible format)."""
    try:
        await ensure_initialized()
        
        account = account_manager.pick_next()
        if not account:
            return web.json_response(
                {
                    "type": "error",
                    "error": {
                        "type": "api_error",
                        "message": "No accounts available"
                    }
                },
                status=503
            )
        
        token = await account_manager.get_token_for_account(account)
        models = await list_models(token)
        
        return web.json_response(models)
        
    except Exception as e:
        logger.error(f"[API] Error listing models: {e}")
        return web.json_response(
            {
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": str(e)
                }
            },
            status=500
        )


async def count_tokens_handler(request: web.Request) -> web.Response:
    """Count tokens endpoint (not supported)."""
    return web.json_response(
        {
            "type": "error",
            "error": {
                "type": "not_implemented",
                "message": (
                    "Token counting is not implemented. Use /v1/messages with max_tokens "
                    "or configure your client to skip token counting."
                )
            }
        },
        status=501
    )


async def messages_handler(request: web.Request) -> web.Response:
    """
    Anthropic-compatible Messages API.
    POST /v1/messages
    """
    try:
        await ensure_initialized()
        
        # Parse request body
        try:
            body = await request.json()
        except json.JSONDecodeError as e:
            return web.json_response(
                {
                    "type": "error",
                    "error": {
                        "type": "invalid_request_error",
                        "message": f"Invalid JSON: {e}"
                    }
                },
                status=400
            )
        
        model = body.get("model", "claude-3-5-sonnet-20241022")
        messages = body.get("messages")
        max_tokens = body.get("max_tokens", 4096)
        stream = body.get("stream", False)
        system = body.get("system")
        tools = body.get("tools")
        tool_choice = body.get("tool_choice")
        thinking = body.get("thinking")
        top_p = body.get("top_p")
        top_k = body.get("top_k")
        temperature = body.get("temperature")
        
        # Optimistic Retry: If ALL accounts are rate-limited for this model, reset them
        if account_manager.is_all_rate_limited(model):
            logger.warn(f"[Server] All accounts rate-limited for {model}. Resetting state for optimistic retry.")
            account_manager.reset_all_rate_limits()
        
        # Validate required fields
        if not messages or not isinstance(messages, list):
            return web.json_response(
                {
                    "type": "error",
                    "error": {
                        "type": "invalid_request_error",
                        "message": "messages is required and must be an array"
                    }
                },
                status=400
            )
        
        # Build the request object
        anthropic_request = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": stream,
            "system": system,
            "tools": tools,
            "tool_choice": tool_choice,
            "thinking": thinking,
            "top_p": top_p,
            "top_k": top_k,
            "temperature": temperature
        }
        
        logger.info(f"[API] Request for model: {model}, stream: {stream}")
        
        # Debug: Log message structure
        if logger.is_debug_enabled:
            logger.debug("[API] Message structure:")
            for i, msg in enumerate(messages):
                content = msg.get("content", [])
                if isinstance(content, list):
                    content_types = ", ".join(
                        c.get("type", "text") if isinstance(c, dict) else "text"
                        for c in content
                    )
                elif isinstance(content, str):
                    content_types = "text"
                else:
                    content_types = "unknown"
                logger.debug(f"  [{i}] {msg.get('role')}: {content_types}")
        
        if stream:
            # Handle streaming response
            response = web.StreamResponse(
                status=200,
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
            await response.prepare(request)
            
            try:
                async for event in send_message_stream(anthropic_request, account_manager, FALLBACK_ENABLED):
                    data = f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"
                    await response.write(data.encode("utf-8"))
                
                await response.write_eof()
                return response
                
            except Exception as stream_error:
                logger.error(f"[API] Stream error: {stream_error}")
                parsed = parse_error(stream_error)
                
                error_event = {
                    "type": "error",
                    "error": {
                        "type": parsed["error_type"],
                        "message": parsed["error_message"]
                    }
                }
                data = f"event: error\ndata: {json.dumps(error_event)}\n\n"
                await response.write(data.encode("utf-8"))
                await response.write_eof()
                return response
        
        else:
            # Handle non-streaming response
            response_data = await send_message(anthropic_request, account_manager, FALLBACK_ENABLED)
            return web.json_response(response_data)
            
    except Exception as error:
        logger.error(f"[API] Error: {error}")
        
        parsed = parse_error(error)
        
        # For auth errors, try to refresh token
        if parsed["error_type"] == "authentication_error":
            logger.warn("[API] Token might be expired, attempting refresh...")
            try:
                account_manager.clear_project_cache()
                account_manager.clear_token_cache()
                await token_extractor.force_refresh()
                parsed["error_message"] = "Token was expired and has been refreshed. Please retry your request."
            except Exception as refresh_error:
                parsed["error_message"] = "Could not refresh token. Make sure Antigravity is running."
        
        logger.warn(f"[API] Returning error response: {parsed['status_code']} {parsed['error_type']} - {parsed['error_message']}")
        
        return web.json_response(
            {
                "type": "error",
                "error": {
                    "type": parsed["error_type"],
                    "message": parsed["error_message"]
                }
            },
            status=parsed["status_code"]
        )


async def not_found_handler(request: web.Request) -> web.Response:
    """Catch-all handler for unsupported endpoints."""
    if logger.is_debug_enabled:
        logger.debug(f"[API] 404 Not Found: {request.method} {request.path}")
    
    return web.json_response(
        {
            "type": "error",
            "error": {
                "type": "not_found_error",
                "message": f"Endpoint {request.method} {request.path} not found"
            }
        },
        status=404
    )


# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_app() -> web.Application:
    """
    Create and configure the aiohttp application.
    
    Returns:
        Configured aiohttp Application
    """
    app = web.Application(
        middlewares=[cors_middleware, logging_middleware, error_middleware],
        client_max_size=REQUEST_BODY_LIMIT
    )
    
    # Add routes
    app.router.add_get("/health", health_handler)
    app.router.add_get("/account-limits", account_limits_handler)
    app.router.add_post("/refresh-token", refresh_token_handler)
    app.router.add_get("/v1/models", list_models_handler)
    app.router.add_post("/v1/messages/count_tokens", count_tokens_handler)
    app.router.add_post("/v1/messages", messages_handler)
    
    # Catch-all for undefined routes
    app.router.add_route("*", "/{path:.*}", not_found_handler)
    
    return app


# =============================================================================
# STARTUP BANNER
# =============================================================================

def print_startup_banner(port: int, debug: bool, fallback: bool) -> None:
    """Print the startup banner."""
    from pathlib import Path
    
    config_dir = Path.home() / ".antigravity-claude-proxy"
    
    # Build status section if any modes are active
    status_lines = []
    if debug or fallback:
        status_lines.append("║                                                              ║")
        status_lines.append("║  Active Modes:                                               ║")
        if debug:
            status_lines.append("║    ✓ Debug mode enabled                                      ║")
        if fallback:
            status_lines.append("║    ✓ Model fallback enabled                                  ║")
    
    # Build control section dynamically
    control_lines = ["║  Control:                                                    ║"]
    if not debug:
        control_lines.append("║    --debug            Enable debug logging                   ║")
    if not fallback:
        control_lines.append("║    --fallback         Enable model fallback on quota exhaust ║")
    control_lines.append("║    Ctrl+C             Stop server                            ║")
    
    status_section = "\n".join(status_lines) + "\n" if status_lines else ""
    control_section = "\n".join(control_lines)
    
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║           Antigravity Claude Proxy Server                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Server running at: http://localhost:{str(port).ljust(25)}║
{status_section}║                                                              ║
{control_section}
║                                                              ║
║  Endpoints:                                                  ║
║    POST /v1/messages         - Anthropic Messages API        ║
║    GET  /v1/models           - List available models         ║
║    GET  /health              - Health check                  ║
║    GET  /account-limits      - Account status & quotas       ║
║    POST /refresh-token       - Force token refresh           ║
║                                                              ║
║  Configuration:                                              ║
║    Storage: {str(config_dir).ljust(49)}║
║                                                              ║
║  Usage with Claude Code:                                     ║
║    export ANTHROPIC_BASE_URL=http://localhost:{str(port).ljust(15)}║
║    export ANTHROPIC_API_KEY=dummy                            ║
║    claude                                                    ║
║                                                              ║
║  Add Google accounts:                                        ║
║    python -m antigravity_proxy accounts                      ║
║                                                              ║
║  Prerequisites (if no accounts configured):                  ║
║    - Antigravity must be running                             ║
║    - Have a chat panel open in Antigravity                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)
    logger.success(f"Server started successfully on port {port}")
    if debug:
        logger.warn("Running in DEBUG mode - verbose logs enabled")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def run_server(
    port: int = DEFAULT_PORT,
    debug: bool = False,
    fallback: bool = False
) -> None:
    """
    Run the proxy server.
    
    Args:
        port: Port to listen on
        debug: Enable debug logging
        fallback: Enable model fallback on quota exhaustion
    """
    global DEBUG_ENABLED, FALLBACK_ENABLED
    
    DEBUG_ENABLED = debug
    FALLBACK_ENABLED = fallback
    logger.set_debug(debug)
    
    # Clear console for clean start
    os.system("cls" if os.name == "nt" else "clear")
    
    print_startup_banner(port, debug, fallback)
    
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=port, print=None)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Antigravity Claude Proxy Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--fallback", action="store_true", help="Enable model fallback")
    
    args = parser.parse_args()
    
    run_server(port=args.port, debug=args.debug, fallback=args.fallback)
