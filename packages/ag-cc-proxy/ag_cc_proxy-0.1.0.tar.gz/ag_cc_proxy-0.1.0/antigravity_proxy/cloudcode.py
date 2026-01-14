"""
Antigravity Claude Proxy - Cloud Code Client Module

Communicates with Google's Cloud Code internal API using the
v1internal:streamGenerateContent endpoint with proper request wrapping.

Includes:
- Rate limit parsing from headers and error messages
- Session ID derivation for cache continuity
- Request building with proper headers and system instructions
- SSE parsing for streaming and non-streaming responses
- Message handlers with multi-account support and retry logic
- Model listing and quota retrieval

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import re
import json
import hashlib
import secrets
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncIterator, Tuple, TYPE_CHECKING
from urllib.parse import urljoin

import aiohttp

from .config import (
    ANTIGRAVITY_ENDPOINT_FALLBACKS,
    ANTIGRAVITY_HEADERS,
    ANTIGRAVITY_SYSTEM_INSTRUCTION,
    DEFAULT_COOLDOWN_MS,
    MAX_RETRIES,
    MAX_EMPTY_RESPONSE_RETRIES,
    MAX_WAIT_BEFORE_ERROR_MS,
    MIN_SIGNATURE_LENGTH,
    ModelFamily,
    get_model_family,
    is_thinking_model,
    get_fallback_model,
    format_duration,
    sleep_ms,
    is_rate_limit_error,
    is_auth_error,
    is_network_error,
    EmptyResponseError,
    logger
)
from .converter import (
    convert_anthropic_to_google,
    convert_google_to_anthropic,
    generate_message_id,
    generate_tool_id,
    signature_cache
)

if TYPE_CHECKING:
    from .accounts import AccountManager, Account


# =============================================================================
# RATE LIMIT PARSER
# =============================================================================

def parse_reset_time(
    response: Optional[aiohttp.ClientResponse] = None,
    error_text: str = ""
) -> Optional[int]:
    """
    Parse reset time from HTTP response or error.
    Checks headers first, then error message body.
    
    Args:
        response: HTTP Response object (optional)
        error_text: Error body text
        
    Returns:
        Milliseconds until reset, or None if not found
    """
    reset_ms = None
    
    # If it's a Response object, check headers first
    if response:
        headers = response.headers
        
        # Standard Retry-After header (seconds or HTTP date)
        retry_after = headers.get("retry-after")
        if retry_after:
            try:
                seconds = int(retry_after)
                reset_ms = seconds * 1000
                logger.debug(f"[CloudCode] Retry-After header: {seconds}s")
            except ValueError:
                # Try parsing as HTTP date
                try:
                    from email.utils import parsedate_to_datetime
                    date = parsedate_to_datetime(retry_after)
                    reset_ms = int((date.timestamp() - datetime.now().timestamp()) * 1000)
                    if reset_ms > 0:
                        logger.debug(f"[CloudCode] Retry-After date: {retry_after}")
                    else:
                        reset_ms = None
                except Exception:
                    pass
        
        # x-ratelimit-reset (Unix timestamp in seconds)
        if not reset_ms:
            ratelimit_reset = headers.get("x-ratelimit-reset")
            if ratelimit_reset:
                try:
                    reset_timestamp = int(ratelimit_reset) * 1000
                    reset_ms = reset_timestamp - int(datetime.now().timestamp() * 1000)
                    if reset_ms > 0:
                        logger.debug(f"[CloudCode] x-ratelimit-reset: {datetime.fromtimestamp(int(ratelimit_reset)).isoformat()}")
                    else:
                        reset_ms = None
                except ValueError:
                    pass
        
        # x-ratelimit-reset-after (seconds)
        if not reset_ms:
            reset_after = headers.get("x-ratelimit-reset-after")
            if reset_after:
                try:
                    seconds = int(reset_after)
                    if seconds > 0:
                        reset_ms = seconds * 1000
                        logger.debug(f"[CloudCode] x-ratelimit-reset-after: {seconds}s")
                except ValueError:
                    pass
    
    # If no header found, try parsing from error message/body
    if not reset_ms and error_text:
        msg = error_text
        
        # Try to extract "quotaResetDelay" first (e.g. "754.431528ms" or "1.5s")
        quota_delay_match = re.search(r'quotaResetDelay[:\s"]+(\d+(?:\.\d+)?)(ms|s)', msg, re.IGNORECASE)
        if quota_delay_match:
            value = float(quota_delay_match.group(1))
            unit = quota_delay_match.group(2).lower()
            reset_ms = int(value * 1000) if unit == "s" else int(value)
            logger.debug(f"[CloudCode] Parsed quotaResetDelay from body: {reset_ms}ms")
        
        # Try to extract "quotaResetTimeStamp" (ISO format)
        if not reset_ms:
            quota_timestamp_match = re.search(
                r'quotaResetTimeStamp[:\s"]+(\d{4}-\d{2}-\d{2}T[\d:.]+Z?)',
                msg, re.IGNORECASE
            )
            if quota_timestamp_match:
                try:
                    reset_time_str = quota_timestamp_match.group(1)
                    if not reset_time_str.endswith("Z"):
                        reset_time_str += "Z"
                    reset_time = datetime.fromisoformat(reset_time_str.replace("Z", "+00:00"))
                    reset_ms = int((reset_time.timestamp() - datetime.now().timestamp()) * 1000)
                    logger.debug(f"[CloudCode] Parsed quotaResetTimeStamp: {quota_timestamp_match.group(1)} (Delta: {reset_ms}ms)")
                except Exception:
                    pass
        
        # Try to extract "retry-after-ms" or "retryDelay" - seconds format (e.g. "7739.23s")
        if not reset_ms:
            sec_match = re.search(
                r'(?:retry[-_]?after[-_]?ms|retryDelay)[:\s"]+([\\d\\.]+)(?:s\b|s")',
                msg, re.IGNORECASE
            )
            if sec_match:
                reset_ms = int(float(sec_match.group(1)) * 1000)
                logger.debug(f"[CloudCode] Parsed retry seconds from body (precise): {reset_ms}ms")
        
        # Check for ms (explicit "ms" suffix)
        if not reset_ms:
            ms_match = re.search(
                r'(?:retry[-_]?after[-_]?ms|retryDelay)[:\s"]+(\d+)(?:\s*ms)?(?![\w.])',
                msg, re.IGNORECASE
            )
            if ms_match:
                reset_ms = int(ms_match.group(1))
                logger.debug(f"[CloudCode] Parsed retry-after-ms from body: {reset_ms}ms")
        
        # Try to extract seconds value like "retry after 60 seconds"
        if not reset_ms:
            sec_match = re.search(r'retry\s+(?:after\s+)?(\d+)\s*(?:sec|s\b)', msg, re.IGNORECASE)
            if sec_match:
                reset_ms = int(sec_match.group(1)) * 1000
                logger.debug(f"[CloudCode] Parsed retry seconds from body: {sec_match.group(1)}s")
        
        # Try to extract duration like "1h23m45s" or "23m45s" or "45s"
        if not reset_ms:
            duration_match = re.search(r'(\d+)h(\d+)m(\d+)s|(\d+)m(\d+)s|(\d+)s', msg, re.IGNORECASE)
            if duration_match:
                groups = duration_match.groups()
                if groups[0]:  # 1h23m45s
                    hours, minutes, seconds = int(groups[0]), int(groups[1]), int(groups[2])
                    reset_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
                elif groups[3]:  # 23m45s
                    minutes, seconds = int(groups[3]), int(groups[4])
                    reset_ms = (minutes * 60 + seconds) * 1000
                elif groups[5]:  # 45s
                    reset_ms = int(groups[5]) * 1000
                if reset_ms:
                    logger.debug(f"[CloudCode] Parsed duration from body: {format_duration(reset_ms)}")
        
        # Try to extract ISO timestamp
        if not reset_ms:
            iso_match = re.search(r'reset[:\s"]+(\d{4}-\d{2}-\d{2}T[\d:.]+Z?)', msg, re.IGNORECASE)
            if iso_match:
                try:
                    reset_time_str = iso_match.group(1)
                    if not reset_time_str.endswith("Z"):
                        reset_time_str += "Z"
                    reset_time = datetime.fromisoformat(reset_time_str.replace("Z", "+00:00"))
                    reset_ms = int((reset_time.timestamp() - datetime.now().timestamp()) * 1000)
                    if reset_ms > 0:
                        logger.debug(f"[CloudCode] Parsed ISO reset time: {iso_match.group(1)}")
                    else:
                        reset_ms = None
                except Exception:
                    pass
    
    # SANITY CHECK: Enforce strict minimums for found rate limits
    if reset_ms is not None:
        if reset_ms < 1000:
            logger.debug(f"[CloudCode] Reset time too small ({reset_ms}ms), enforcing 2s buffer")
            reset_ms = 2000
    
    return reset_ms


# =============================================================================
# SESSION MANAGER
# =============================================================================

def derive_session_id(anthropic_request: Dict[str, Any]) -> str:
    """
    Derive a stable session ID from the first user message in the conversation.
    
    This ensures the same conversation uses the same session ID across turns,
    enabling prompt caching (cache is scoped to session + organization).
    
    Args:
        anthropic_request: The Anthropic-format request
        
    Returns:
        A stable session ID (32 hex characters) or random UUID if no user message
    """
    messages = anthropic_request.get("messages", [])
    
    # Find the first user message
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                # Extract text from content blocks
                texts = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
                ]
                text = "\n".join(texts)
            else:
                continue
            
            if text:
                # Hash the content with SHA256, return first 32 hex chars
                hash_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                return hash_digest[:32]
    
    # Fallback to random UUID if no user message found
    return secrets.token_hex(16)


# =============================================================================
# REQUEST BUILDER
# =============================================================================

def build_cloud_code_request(anthropic_request: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    """
    Build the wrapped request body for Cloud Code API.
    
    Args:
        anthropic_request: The Anthropic-format request
        project_id: The project ID to use
        
    Returns:
        The Cloud Code API request payload
    """
    model = anthropic_request.get("model", "")
    google_request = convert_anthropic_to_google(anthropic_request)
    
    # Use stable session ID derived from first user message for cache continuity
    google_request["sessionId"] = derive_session_id(anthropic_request)
    
    # Build system instruction parts array with [ignore] tags to prevent model from
    # identifying as "Antigravity" (fixes GitHub issue #76)
    system_parts = [
        {"text": ANTIGRAVITY_SYSTEM_INSTRUCTION},
        {"text": f"Please ignore the following [ignore]{ANTIGRAVITY_SYSTEM_INSTRUCTION}[/ignore]"}
    ]
    
    # Append any existing system instructions from the request
    existing_system = google_request.get("systemInstruction", {}).get("parts", [])
    for part in existing_system:
        if part.get("text"):
            system_parts.append({"text": part["text"]})
    
    payload = {
        "project": project_id,
        "model": model,
        "request": google_request,
        "userAgent": "antigravity",
        "requestType": "agent",  # CLIProxyAPI v6.6.89 compatibility
        "requestId": f"agent-{secrets.token_hex(16)}"
    }
    
    # Inject systemInstruction with role: "user" at the top level
    payload["request"]["systemInstruction"] = {
        "role": "user",
        "parts": system_parts
    }
    
    return payload


def build_headers(token: str, model: str, accept: str = "application/json") -> Dict[str, str]:
    """
    Build headers for Cloud Code API requests.
    
    Args:
        token: OAuth access token
        model: Model name
        accept: Accept header value (default: 'application/json')
        
    Returns:
        Headers dictionary
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        **ANTIGRAVITY_HEADERS
    }
    
    model_family = get_model_family(model)
    
    # Add interleaved thinking header only for Claude thinking models
    if model_family == ModelFamily.CLAUDE and is_thinking_model(model):
        headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
    
    if accept != "application/json":
        headers["Accept"] = accept
    
    return headers


# =============================================================================
# SSE PARSER (Non-streaming for thinking models)
# =============================================================================

async def parse_thinking_sse_response(
    response: aiohttp.ClientResponse,
    original_model: str
) -> Dict[str, Any]:
    """
    Parse SSE response for thinking models and accumulate all parts.
    
    Args:
        response: The HTTP response with SSE body
        original_model: The original model name
        
    Returns:
        Anthropic-format response object
    """
    accumulated_thinking_text = ""
    accumulated_thinking_signature = ""
    accumulated_text = ""
    final_parts: List[Dict[str, Any]] = []
    usage_metadata: Dict[str, Any] = {}
    finish_reason = "STOP"
    
    def flush_thinking():
        nonlocal accumulated_thinking_text, accumulated_thinking_signature
        if accumulated_thinking_text:
            final_parts.append({
                "thought": True,
                "text": accumulated_thinking_text,
                "thoughtSignature": accumulated_thinking_signature
            })
            accumulated_thinking_text = ""
            accumulated_thinking_signature = ""
    
    def flush_text():
        nonlocal accumulated_text
        if accumulated_text:
            final_parts.append({"text": accumulated_text})
            accumulated_text = ""
    
    buffer = ""
    async for chunk in response.content.iter_any():
        buffer += chunk.decode("utf-8", errors="replace")
        lines = buffer.split("\n")
        buffer = lines.pop()  # Keep incomplete line in buffer
        
        for line in lines:
            if not line.startswith("data:"):
                continue
            json_text = line[5:].strip()
            if not json_text:
                continue
            
            try:
                data = json.loads(json_text)
                inner_response = data.get("response", data)
                
                if inner_response.get("usageMetadata"):
                    usage_metadata = inner_response["usageMetadata"]
                
                candidates = inner_response.get("candidates", [])
                first_candidate = candidates[0] if candidates else {}
                if first_candidate.get("finishReason"):
                    finish_reason = first_candidate["finishReason"]
                
                parts = first_candidate.get("content", {}).get("parts", [])
                for part in parts:
                    if part.get("thought") is True:
                        flush_text()
                        accumulated_thinking_text += part.get("text", "")
                        if part.get("thoughtSignature"):
                            accumulated_thinking_signature = part["thoughtSignature"]
                    elif "functionCall" in part:
                        flush_thinking()
                        flush_text()
                        final_parts.append(part)
                    elif "text" in part:
                        if not part["text"]:
                            continue
                        flush_thinking()
                        accumulated_text += part["text"]
                        
            except json.JSONDecodeError as e:
                logger.debug(f"[CloudCode] SSE parse warning: {e}, Raw: {json_text[:100]}")
    
    flush_thinking()
    flush_text()
    
    accumulated_response = {
        "candidates": [{"content": {"parts": final_parts}, "finishReason": finish_reason}],
        "usageMetadata": usage_metadata
    }
    
    part_types = [
        "thought" if p.get("thought") else ("functionCall" if "functionCall" in p else "text")
        for p in final_parts
    ]
    logger.debug(f"[CloudCode] Response received (SSE), part types: {part_types}")
    
    if any(p.get("thought") for p in final_parts):
        thinking_part = next((p for p in final_parts if p.get("thought")), None)
        if thinking_part:
            logger.debug(f"[CloudCode] Thinking signature length: {len(thinking_part.get('thoughtSignature', ''))}")
    
    return convert_google_to_anthropic(accumulated_response, original_model)


# =============================================================================
# SSE STREAMER (Real-time streaming)
# =============================================================================

async def stream_sse_response(
    response: aiohttp.ClientResponse,
    original_model: str
) -> AsyncIterator[Dict[str, Any]]:
    """
    Stream SSE response and yield Anthropic-format events.
    
    Args:
        response: The HTTP response with SSE body
        original_model: The original model name
        
    Yields:
        Anthropic-format SSE events
    """
    message_id = generate_message_id()
    has_emitted_start = False
    block_index = 0
    current_block_type: Optional[str] = None
    current_thinking_signature = ""
    input_tokens = 0
    output_tokens = 0
    cache_read_tokens = 0
    stop_reason = "end_turn"
    
    buffer = ""
    async for chunk in response.content.iter_any():
        buffer += chunk.decode("utf-8", errors="replace")
        lines = buffer.split("\n")
        buffer = lines.pop()  # Keep incomplete line in buffer
        
        for line in lines:
            if not line.startswith("data:"):
                continue
            
            json_text = line[5:].strip()
            if not json_text:
                continue
            
            try:
                data = json.loads(json_text)
                inner_response = data.get("response", data)
                
                # Extract usage metadata (including cache tokens)
                usage = inner_response.get("usageMetadata")
                if usage:
                    input_tokens = usage.get("promptTokenCount", input_tokens)
                    output_tokens = usage.get("candidatesTokenCount", output_tokens)
                    cache_read_tokens = usage.get("cachedContentTokenCount", cache_read_tokens)
                
                candidates = inner_response.get("candidates", [])
                first_candidate = candidates[0] if candidates else {}
                content = first_candidate.get("content", {})
                parts = content.get("parts", [])
                
                # Emit message_start on first data
                if not has_emitted_start and parts:
                    has_emitted_start = True
                    yield {
                        "type": "message_start",
                        "message": {
                            "id": message_id,
                            "type": "message",
                            "role": "assistant",
                            "content": [],
                            "model": original_model,
                            "stop_reason": None,
                            "stop_sequence": None,
                            "usage": {
                                "input_tokens": input_tokens - cache_read_tokens,
                                "output_tokens": 0,
                                "cache_read_input_tokens": cache_read_tokens,
                                "cache_creation_input_tokens": 0
                            }
                        }
                    }
                
                # Process each part
                for part in parts:
                    if part.get("thought") is True:
                        # Handle thinking block
                        text = part.get("text", "")
                        signature = part.get("thoughtSignature", "")
                        
                        if current_block_type != "thinking":
                            if current_block_type is not None:
                                yield {"type": "content_block_stop", "index": block_index}
                                block_index += 1
                            current_block_type = "thinking"
                            current_thinking_signature = ""
                            yield {
                                "type": "content_block_start",
                                "index": block_index,
                                "content_block": {"type": "thinking", "thinking": ""}
                            }
                        
                        if signature and len(signature) >= MIN_SIGNATURE_LENGTH:
                            current_thinking_signature = signature
                            # Cache thinking signature with model family
                            model_family = get_model_family(original_model)
                            if model_family != ModelFamily.UNKNOWN:
                                signature_cache.cache_thinking_signature(signature, model_family.value)
                        
                        yield {
                            "type": "content_block_delta",
                            "index": block_index,
                            "delta": {"type": "thinking_delta", "thinking": text}
                        }
                        
                    elif "text" in part:
                        # Skip empty text parts
                        if not part["text"] or not part["text"].strip():
                            continue
                        
                        # Handle regular text
                        if current_block_type != "text":
                            if current_block_type == "thinking" and current_thinking_signature:
                                yield {
                                    "type": "content_block_delta",
                                    "index": block_index,
                                    "delta": {"type": "signature_delta", "signature": current_thinking_signature}
                                }
                                current_thinking_signature = ""
                            if current_block_type is not None:
                                yield {"type": "content_block_stop", "index": block_index}
                                block_index += 1
                            current_block_type = "text"
                            yield {
                                "type": "content_block_start",
                                "index": block_index,
                                "content_block": {"type": "text", "text": ""}
                            }
                        
                        yield {
                            "type": "content_block_delta",
                            "index": block_index,
                            "delta": {"type": "text_delta", "text": part["text"]}
                        }
                        
                    elif "functionCall" in part:
                        # Handle tool use
                        function_call_signature = part.get("thoughtSignature", "")
                        
                        if current_block_type == "thinking" and current_thinking_signature:
                            yield {
                                "type": "content_block_delta",
                                "index": block_index,
                                "delta": {"type": "signature_delta", "signature": current_thinking_signature}
                            }
                            current_thinking_signature = ""
                        if current_block_type is not None:
                            yield {"type": "content_block_stop", "index": block_index}
                            block_index += 1
                        current_block_type = "tool_use"
                        stop_reason = "tool_use"
                        
                        fc = part["functionCall"]
                        tool_id = fc.get("id") or generate_tool_id()
                        
                        # Build tool_use block
                        tool_use_block: Dict[str, Any] = {
                            "type": "tool_use",
                            "id": tool_id,
                            "name": fc.get("name"),
                            "input": {}
                        }
                        
                        # Store the signature in the tool_use block for later retrieval
                        if function_call_signature and len(function_call_signature) >= MIN_SIGNATURE_LENGTH:
                            tool_use_block["thoughtSignature"] = function_call_signature
                            # Cache for future requests
                            signature_cache.cache_signature(tool_id, function_call_signature)
                        
                        yield {
                            "type": "content_block_start",
                            "index": block_index,
                            "content_block": tool_use_block
                        }
                        
                        yield {
                            "type": "content_block_delta",
                            "index": block_index,
                            "delta": {
                                "type": "input_json_delta",
                                "partial_json": json.dumps(fc.get("args", {}))
                            }
                        }
                
                # Check finish reason
                if first_candidate.get("finishReason"):
                    fr = first_candidate["finishReason"]
                    if fr == "MAX_TOKENS":
                        stop_reason = "max_tokens"
                    elif fr == "STOP":
                        stop_reason = "end_turn"
                        
            except json.JSONDecodeError as e:
                logger.warn(f"[CloudCode] SSE parse error: {e}")
    
    # Handle no content received - throw error to trigger retry
    if not has_emitted_start:
        logger.warn("[CloudCode] No content parts received, throwing for retry")
        raise EmptyResponseError("No content parts received from API")
    else:
        # Close any open block
        if current_block_type is not None:
            if current_block_type == "thinking" and current_thinking_signature:
                yield {
                    "type": "content_block_delta",
                    "index": block_index,
                    "delta": {"type": "signature_delta", "signature": current_thinking_signature}
                }
            yield {"type": "content_block_stop", "index": block_index}
    
    # Emit message_delta and message_stop
    yield {
        "type": "message_delta",
        "delta": {"stop_reason": stop_reason, "stop_sequence": None},
        "usage": {
            "output_tokens": output_tokens,
            "cache_read_input_tokens": cache_read_tokens,
            "cache_creation_input_tokens": 0
        }
    }
    
    yield {"type": "message_stop"}


def emit_empty_response_fallback(model: str) -> List[Dict[str, Any]]:
    """
    Emit a fallback message when all retry attempts fail with empty response.
    
    Args:
        model: The model name
        
    Returns:
        List of Anthropic-format SSE events
    """
    message_id = generate_message_id()
    
    return [
        {
            "type": "message_start",
            "message": {
                "id": message_id,
                "type": "message",
                "role": "assistant",
                "content": [],
                "model": model,
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }
        },
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""}
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "[No response after retries - please try again]"}
        },
        {"type": "content_block_stop", "index": 0},
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn", "stop_sequence": None},
            "usage": {"output_tokens": 0}
        },
        {"type": "message_stop"}
    ]


# =============================================================================
# MODEL API
# =============================================================================

def is_supported_model(model_id: str) -> bool:
    """Check if a model is supported (Claude or Gemini)."""
    family = get_model_family(model_id)
    return family in (ModelFamily.CLAUDE, ModelFamily.GEMINI)


async def fetch_available_models(token: str) -> Dict[str, Any]:
    """
    Fetch available models with quota info from Cloud Code API.
    
    Args:
        token: OAuth access token
        
    Returns:
        Raw response from fetchAvailableModels API
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        **ANTIGRAVITY_HEADERS
    }
    
    async with aiohttp.ClientSession() as session:
        for endpoint in ANTIGRAVITY_ENDPOINT_FALLBACKS:
            try:
                url = f"{endpoint}/v1internal:fetchAvailableModels"
                async with session.post(url, headers=headers, json={}) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.warn(f"[CloudCode] fetchAvailableModels error at {endpoint}: {response.status}")
                        continue
                    return await response.json()
            except Exception as e:
                logger.warn(f"[CloudCode] fetchAvailableModels failed at {endpoint}: {e}")
    
    raise Exception("Failed to fetch available models from all endpoints")


async def list_models(token: str) -> Dict[str, Any]:
    """
    List available models in Anthropic API format.
    Fetches models dynamically from the Cloud Code API.
    
    Args:
        token: OAuth access token
        
    Returns:
        OpenAI-compatible model list response
    """
    import time
    
    data = await fetch_available_models(token)
    if not data or "models" not in data:
        return {"object": "list", "data": []}
    
    model_list = []
    for model_id, model_data in data["models"].items():
        if not is_supported_model(model_id):
            continue
        model_list.append({
            "id": model_id,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "anthropic",
            "description": model_data.get("displayName", model_id)
        })
    
    return {"object": "list", "data": model_list}


async def get_model_quotas(token: str) -> Dict[str, Dict[str, Any]]:
    """
    Get model quotas for an account.
    Extracts quota info (remaining fraction and reset time) for each model.
    
    Args:
        token: OAuth access token
        
    Returns:
        Map of modelId -> { remainingFraction, resetTime }
    """
    data = await fetch_available_models(token)
    if not data or "models" not in data:
        return {}
    
    quotas = {}
    for model_id, model_data in data["models"].items():
        # Only include Claude and Gemini models
        if not is_supported_model(model_id):
            continue
        
        quota_info = model_data.get("quotaInfo")
        if quota_info:
            quotas[model_id] = {
                "remainingFraction": quota_info.get("remainingFraction"),
                "resetTime": quota_info.get("resetTime")
            }
    
    return quotas


# =============================================================================
# MESSAGE HANDLER (Non-streaming)
# =============================================================================

async def send_message(
    anthropic_request: Dict[str, Any],
    account_manager: "AccountManager",
    fallback_enabled: bool = False
) -> Dict[str, Any]:
    """
    Send a non-streaming request to Cloud Code with multi-account support.
    Uses SSE endpoint for thinking models (non-streaming doesn't return thinking blocks).
    
    Args:
        anthropic_request: The Anthropic-format request
        account_manager: The account manager instance
        fallback_enabled: Whether to enable model fallback on quota exhaustion
        
    Returns:
        Anthropic-format response object
        
    Raises:
        Exception: If max retries exceeded or no accounts available
    """
    model = anthropic_request.get("model", "")
    is_thinking = is_thinking_model(model)
    
    # Retry loop with account failover
    max_attempts = max(MAX_RETRIES, account_manager.get_account_count() + 1)
    
    for attempt in range(max_attempts):
        # Use sticky account selection for cache continuity
        sticky_account, wait_ms = account_manager.pick_sticky_account(model)
        account = sticky_account
        
        # Handle waiting for sticky account
        if not account and wait_ms > 0:
            logger.info(f"[CloudCode] Waiting {format_duration(wait_ms)} for sticky account...")
            await sleep_ms(wait_ms)
            account_manager.clear_expired_limits()
            account = account_manager.get_current_sticky_account(model)
        
        # Handle all accounts rate-limited
        if not account:
            if account_manager.is_all_rate_limited(model):
                all_wait_ms = account_manager.get_min_wait_time_ms(model)
                
                # If wait time is too long, throw error immediately
                if all_wait_ms > MAX_WAIT_BEFORE_ERROR_MS:
                    reset_time = format_duration(all_wait_ms)
                    raise Exception(
                        f"RESOURCE_EXHAUSTED: Rate limited on {model}. "
                        f"Quota will reset after {reset_time}."
                    )
                
                # Wait for reset
                account_count = account_manager.get_account_count()
                logger.warn(f"[CloudCode] All {account_count} account(s) rate-limited. Waiting {format_duration(all_wait_ms)}...")
                await sleep_ms(all_wait_ms)
                await sleep_ms(500)  # Buffer
                account_manager.clear_expired_limits()
                account = account_manager.pick_next(model)
                
                # If still no account after waiting, try optimistic reset
                if not account:
                    logger.warn("[CloudCode] No account available after wait, attempting optimistic reset...")
                    account_manager.reset_all_rate_limits()
                    account = account_manager.pick_next(model)
            
            if not account:
                # Check if fallback is enabled and available
                if fallback_enabled:
                    fallback_model = get_fallback_model(model)
                    if fallback_model:
                        logger.warn(f"[CloudCode] All accounts exhausted for {model}. Attempting fallback to {fallback_model}")
                        fallback_request = {**anthropic_request, "model": fallback_model}
                        return await send_message(fallback_request, account_manager, False)
                raise Exception("No accounts available")
        
        try:
            # Get token and project for this account
            token = await account_manager.get_token_for_account(account)
            project = await account_manager.get_project_for_account(account, token)
            payload = build_cloud_code_request(anthropic_request, project)
            
            logger.debug(f"[CloudCode] Sending request for model: {model}")
            
            # Try each endpoint
            last_error = None
            async with aiohttp.ClientSession() as session:
                for endpoint in ANTIGRAVITY_ENDPOINT_FALLBACKS:
                    try:
                        if is_thinking:
                            url = f"{endpoint}/v1internal:streamGenerateContent?alt=sse"
                        else:
                            url = f"{endpoint}/v1internal:generateContent"
                        
                        accept = "text/event-stream" if is_thinking else "application/json"
                        headers = build_headers(token, model, accept)
                        
                        async with session.post(url, headers=headers, json=payload) as response:
                            if not response.ok:
                                error_text = await response.text()
                                logger.warn(f"[CloudCode] Error at {endpoint}: {response.status} - {error_text}")
                                
                                if response.status == 401:
                                    # Auth error - clear caches and retry
                                    logger.warn("[CloudCode] Auth error, refreshing token...")
                                    account_manager.clear_token_cache(account.email)
                                    account_manager.clear_project_cache(account.email)
                                    continue
                                
                                if response.status == 429:
                                    # Rate limited - try next endpoint first
                                    logger.debug(f"[CloudCode] Rate limited at {endpoint}, trying next endpoint...")
                                    reset_ms = parse_reset_time(response, error_text)
                                    if not last_error or not last_error.get("is_429"):
                                        last_error = {"is_429": True, "error_text": error_text, "reset_ms": reset_ms}
                                    elif reset_ms and (not last_error.get("reset_ms") or reset_ms < last_error["reset_ms"]):
                                        last_error["reset_ms"] = reset_ms
                                    continue
                                
                                if response.status >= 400:
                                    last_error = {"error": Exception(f"API error {response.status}: {error_text}")}
                                    if response.status >= 500:
                                        logger.warn(f"[CloudCode] {response.status} error, waiting 1s before retry...")
                                        await sleep_ms(1000)
                                    continue
                            
                            # For thinking models, parse SSE and accumulate all parts
                            if is_thinking:
                                return await parse_thinking_sse_response(response, anthropic_request.get("model", ""))
                            
                            # Non-thinking models use regular JSON
                            data = await response.json()
                            logger.debug("[CloudCode] Response received")
                            return convert_google_to_anthropic(data, anthropic_request.get("model", ""))
                            
                    except Exception as endpoint_error:
                        if is_rate_limit_error(endpoint_error):
                            raise  # Re-throw to trigger account switch
                        logger.warn(f"[CloudCode] Error at {endpoint}: {endpoint_error}")
                        last_error = {"error": endpoint_error}
            
            # If all endpoints failed for this account
            if last_error:
                if last_error.get("is_429"):
                    logger.warn(f"[CloudCode] All endpoints rate-limited for {account.email}")
                    account_manager.mark_rate_limited(account.email, last_error.get("reset_ms"), model)
                    raise Exception(f"Rate limited: {last_error.get('error_text', '')}")
                if "error" in last_error:
                    raise last_error["error"]
                    
        except Exception as error:
            if is_rate_limit_error(error):
                logger.info(f"[CloudCode] Account {account.email} rate-limited, trying next...")
                continue
            if is_auth_error(error):
                logger.warn(f"[CloudCode] Account {account.email} has invalid credentials, trying next...")
                continue
            
            error_msg = str(error)
            if "API error 5" in error_msg or "500" in error_msg or "503" in error_msg:
                logger.warn(f"[CloudCode] Account {account.email} failed with 5xx error, trying next...")
                account_manager.pick_next(model)
                continue
            
            if is_network_error(error):
                logger.warn(f"[CloudCode] Network error for {account.email}, trying next account... ({error})")
                await sleep_ms(1000)
                account_manager.pick_next(model)
                continue
            
            raise
    
    raise Exception("Max retries exceeded")


# =============================================================================
# STREAMING HANDLER
# =============================================================================

async def send_message_stream(
    anthropic_request: Dict[str, Any],
    account_manager: "AccountManager",
    fallback_enabled: bool = False
) -> AsyncIterator[Dict[str, Any]]:
    """
    Send a streaming request to Cloud Code with multi-account support.
    Streams events in real-time as they arrive from the server.
    
    Args:
        anthropic_request: The Anthropic-format request
        account_manager: The account manager instance
        fallback_enabled: Whether to enable model fallback on quota exhaustion
        
    Yields:
        Anthropic-format SSE events
        
    Raises:
        Exception: If max retries exceeded or no accounts available
    """
    model = anthropic_request.get("model", "")
    
    # Retry loop with account failover
    max_attempts = max(MAX_RETRIES, account_manager.get_account_count() + 1)
    
    for attempt in range(max_attempts):
        # Use sticky account selection for cache continuity
        sticky_account, wait_ms = account_manager.pick_sticky_account(model)
        account = sticky_account
        
        # Handle waiting for sticky account
        if not account and wait_ms > 0:
            logger.info(f"[CloudCode] Waiting {format_duration(wait_ms)} for sticky account...")
            await sleep_ms(wait_ms)
            account_manager.clear_expired_limits()
            account = account_manager.get_current_sticky_account(model)
        
        # Handle all accounts rate-limited
        if not account:
            if account_manager.is_all_rate_limited(model):
                all_wait_ms = account_manager.get_min_wait_time_ms(model)
                
                # If wait time is too long, throw error immediately
                if all_wait_ms > MAX_WAIT_BEFORE_ERROR_MS:
                    reset_time = format_duration(all_wait_ms)
                    raise Exception(
                        f"RESOURCE_EXHAUSTED: Rate limited on {model}. "
                        f"Quota will reset after {reset_time}."
                    )
                
                # Wait for reset
                account_count = account_manager.get_account_count()
                logger.warn(f"[CloudCode] All {account_count} account(s) rate-limited. Waiting {format_duration(all_wait_ms)}...")
                await sleep_ms(all_wait_ms)
                await sleep_ms(500)  # Buffer
                account_manager.clear_expired_limits()
                account = account_manager.pick_next(model)
                
                # If still no account after waiting, try optimistic reset
                if not account:
                    logger.warn("[CloudCode] No account available after wait, attempting optimistic reset...")
                    account_manager.reset_all_rate_limits()
                    account = account_manager.pick_next(model)
            
            if not account:
                # Check if fallback is enabled and available
                if fallback_enabled:
                    fallback_model = get_fallback_model(model)
                    if fallback_model:
                        logger.warn(f"[CloudCode] All accounts exhausted for {model}. Attempting fallback to {fallback_model} (streaming)")
                        fallback_request = {**anthropic_request, "model": fallback_model}
                        async for event in send_message_stream(fallback_request, account_manager, False):
                            yield event
                        return
                raise Exception("No accounts available")
        
        try:
            # Get token and project for this account
            token = await account_manager.get_token_for_account(account)
            project = await account_manager.get_project_for_account(account, token)
            payload = build_cloud_code_request(anthropic_request, project)
            
            logger.debug(f"[CloudCode] Starting stream for model: {model}")
            
            # Try each endpoint for streaming
            last_error = None
            async with aiohttp.ClientSession() as session:
                for endpoint in ANTIGRAVITY_ENDPOINT_FALLBACKS:
                    try:
                        url = f"{endpoint}/v1internal:streamGenerateContent?alt=sse"
                        headers = build_headers(token, model, "text/event-stream")
                        
                        async with session.post(url, headers=headers, json=payload) as response:
                            if not response.ok:
                                error_text = await response.text()
                                logger.warn(f"[CloudCode] Stream error at {endpoint}: {response.status} - {error_text}")
                                
                                if response.status == 401:
                                    # Auth error - clear caches and retry
                                    account_manager.clear_token_cache(account.email)
                                    account_manager.clear_project_cache(account.email)
                                    continue
                                
                                if response.status == 429:
                                    # Rate limited - try next endpoint first
                                    logger.debug(f"[CloudCode] Stream rate limited at {endpoint}, trying next endpoint...")
                                    reset_ms = parse_reset_time(response, error_text)
                                    if not last_error or not last_error.get("is_429"):
                                        last_error = {"is_429": True, "error_text": error_text, "reset_ms": reset_ms}
                                    elif reset_ms and (not last_error.get("reset_ms") or reset_ms < last_error["reset_ms"]):
                                        last_error["reset_ms"] = reset_ms
                                    continue
                                
                                last_error = {"error": Exception(f"API error {response.status}: {error_text}")}
                                
                                if response.status >= 500:
                                    logger.warn(f"[CloudCode] {response.status} stream error, waiting 1s before retry...")
                                    await sleep_ms(1000)
                                continue
                            
                            # Stream the response with retry logic for empty responses
                            for empty_retries in range(MAX_EMPTY_RESPONSE_RETRIES + 1):
                                try:
                                    async for event in stream_sse_response(response, anthropic_request.get("model", "")):
                                        yield event
                                    logger.debug("[CloudCode] Stream completed")
                                    return
                                    
                                except EmptyResponseError:
                                    if empty_retries >= MAX_EMPTY_RESPONSE_RETRIES:
                                        logger.error(f"[CloudCode] Empty response after {MAX_EMPTY_RESPONSE_RETRIES} retries")
                                        for event in emit_empty_response_fallback(anthropic_request.get("model", "")):
                                            yield event
                                        return
                                    
                                    # Exponential backoff: 500ms, 1000ms, 2000ms
                                    backoff_ms = 500 * (2 ** empty_retries)
                                    logger.warn(f"[CloudCode] Empty response, retry {empty_retries + 1}/{MAX_EMPTY_RESPONSE_RETRIES} after {backoff_ms}ms...")
                                    await sleep_ms(backoff_ms)
                                    
                                    # Refetch the response
                                    async with session.post(url, headers=headers, json=payload) as retry_response:
                                        if not retry_response.ok:
                                            retry_error_text = await retry_response.text()
                                            
                                            if retry_response.status == 429:
                                                reset_ms = parse_reset_time(retry_response, retry_error_text)
                                                account_manager.mark_rate_limited(account.email, reset_ms, model)
                                                raise Exception(f"429 RESOURCE_EXHAUSTED during retry: {retry_error_text}")
                                            
                                            if retry_response.status == 401:
                                                account_manager.clear_token_cache(account.email)
                                                account_manager.clear_project_cache(account.email)
                                                raise Exception(f"401 AUTH_INVALID during retry: {retry_error_text}")
                                            
                                            if retry_response.status >= 500:
                                                logger.warn(f"[CloudCode] Retry got {retry_response.status}, will retry...")
                                                await sleep_ms(1000)
                                                continue
                                            
                                            raise Exception(f"Empty response retry failed: {retry_response.status} - {retry_error_text}")
                                        
                                        # Update response for next iteration
                                        response = retry_response
                                        
                    except EmptyResponseError:
                        raise  # Re-throw to outer handler
                    except Exception as endpoint_error:
                        if is_rate_limit_error(endpoint_error):
                            raise  # Re-throw to trigger account switch
                        if isinstance(endpoint_error, EmptyResponseError):
                            raise
                        logger.warn(f"[CloudCode] Stream error at {endpoint}: {endpoint_error}")
                        last_error = {"error": endpoint_error}
            
            # If all endpoints failed for this account
            if last_error:
                if last_error.get("is_429"):
                    logger.warn(f"[CloudCode] All endpoints rate-limited for {account.email}")
                    account_manager.mark_rate_limited(account.email, last_error.get("reset_ms"), model)
                    raise Exception(f"Rate limited: {last_error.get('error_text', '')}")
                if "error" in last_error:
                    raise last_error["error"]
                    
        except Exception as error:
            if is_rate_limit_error(error):
                logger.info(f"[CloudCode] Account {account.email} rate-limited, trying next...")
                continue
            if is_auth_error(error):
                logger.warn(f"[CloudCode] Account {account.email} has invalid credentials, trying next...")
                continue
            
            error_msg = str(error)
            if "API error 5" in error_msg or "500" in error_msg or "503" in error_msg:
                logger.warn(f"[CloudCode] Account {account.email} failed with 5xx stream error, trying next...")
                account_manager.pick_next(model)
                continue
            
            if is_network_error(error):
                logger.warn(f"[CloudCode] Network error for {account.email} (stream), trying next account... ({error})")
                await sleep_ms(1000)
                account_manager.pick_next(model)
                continue
            
            raise
    
    raise Exception("Max retries exceeded")
