"""
Antigravity Claude Proxy - Format Converter Module

Converts between Anthropic Messages API format and Google Generative AI format.

Includes:
- Signature caching for Gemini thoughtSignatures
- Schema sanitization for Gemini API compatibility
- Thinking block utilities (filtering, validation, recovery)
- Content conversion (Anthropic to Google parts)
- Request conversion (Anthropic to Google format)
- Response conversion (Google to Anthropic format)

Based on: https://github.com/NoeFabris/opencode-antigravity-auth
"""

import re
import copy
import time
import secrets
from typing import Optional, Dict, Any, List, Tuple, Set, Union

from .config import (
    MIN_SIGNATURE_LENGTH,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_SKIP_SIGNATURE,
    GEMINI_SIGNATURE_CACHE_TTL_S,
    ModelFamily,
    get_model_family,
    is_thinking_model,
    logger
)


# =============================================================================
# SIGNATURE CACHE
# =============================================================================

class SignatureCache:
    """
    In-memory cache for Gemini thoughtSignatures.
    
    Gemini models require thoughtSignature on tool calls, but Claude Code
    strips non-standard fields. This cache stores signatures by tool_use_id
    so they can be restored in subsequent requests.
    
    Also caches thinking block signatures with model family for cross-model
    compatibility checking.
    """
    
    def __init__(self):
        # tool_use_id -> {"signature": str, "timestamp": float}
        self._signature_cache: Dict[str, Dict[str, Any]] = {}
        # signature -> {"model_family": str, "timestamp": float}
        self._thinking_signature_cache: Dict[str, Dict[str, Any]] = {}
    
    def cache_signature(self, tool_use_id: str, signature: str) -> None:
        """
        Store a signature for a tool_use_id.
        
        Args:
            tool_use_id: The tool use ID
            signature: The thoughtSignature to cache
        """
        if not tool_use_id or not signature:
            return
        self._signature_cache[tool_use_id] = {
            "signature": signature,
            "timestamp": time.time()
        }
    
    def get_cached_signature(self, tool_use_id: str) -> Optional[str]:
        """
        Get a cached signature for a tool_use_id.
        
        Args:
            tool_use_id: The tool use ID
            
        Returns:
            The cached signature or None if not found/expired
        """
        if not tool_use_id:
            return None
        entry = self._signature_cache.get(tool_use_id)
        if not entry:
            return None
        
        # Check TTL
        if time.time() - entry["timestamp"] > GEMINI_SIGNATURE_CACHE_TTL_S:
            del self._signature_cache[tool_use_id]
            return None
        
        return entry["signature"]
    
    def cache_thinking_signature(self, signature: str, model_family: str) -> None:
        """
        Cache a thinking block signature with its model family.
        
        Args:
            signature: The thinking signature to cache
            model_family: The model family ('claude' or 'gemini')
        """
        if not signature or len(signature) < MIN_SIGNATURE_LENGTH:
            return
        self._thinking_signature_cache[signature] = {
            "model_family": model_family,
            "timestamp": time.time()
        }
    
    def get_cached_signature_family(self, signature: str) -> Optional[str]:
        """
        Get the cached model family for a thinking signature.
        
        Args:
            signature: The signature to look up
            
        Returns:
            'claude', 'gemini', or None if not found/expired
        """
        if not signature:
            return None
        entry = self._thinking_signature_cache.get(signature)
        if not entry:
            return None
        
        # Check TTL
        if time.time() - entry["timestamp"] > GEMINI_SIGNATURE_CACHE_TTL_S:
            del self._thinking_signature_cache[signature]
            return None
        
        return entry["model_family"]
    
    def cleanup(self) -> None:
        """Clear expired entries from both caches."""
        now = time.time()
        
        # Clean signature cache
        expired_sigs = [
            k for k, v in self._signature_cache.items()
            if now - v["timestamp"] > GEMINI_SIGNATURE_CACHE_TTL_S
        ]
        for k in expired_sigs:
            del self._signature_cache[k]
        
        # Clean thinking signature cache
        expired_thinking = [
            k for k, v in self._thinking_signature_cache.items()
            if now - v["timestamp"] > GEMINI_SIGNATURE_CACHE_TTL_S
        ]
        for k in expired_thinking:
            del self._thinking_signature_cache[k]
    
    def get_cache_size(self) -> int:
        """Get the current signature cache size."""
        return len(self._signature_cache)
    
    def get_thinking_cache_size(self) -> int:
        """Get the current thinking signature cache size."""
        return len(self._thinking_signature_cache)


# Global signature cache instance
signature_cache = SignatureCache()


# =============================================================================
# SCHEMA SANITIZER
# =============================================================================

def append_description_hint(schema: Dict[str, Any], hint: str) -> Dict[str, Any]:
    """
    Append a hint to a schema's description field.
    Format: "existing (hint)" or just "hint" if no existing description.
    
    Args:
        schema: Schema object to modify
        hint: Hint text to append
        
    Returns:
        Modified schema with appended description
    """
    if not schema or not isinstance(schema, dict):
        return schema
    result = dict(schema)
    existing = result.get("description", "")
    result["description"] = f"{existing} ({hint})" if existing else hint
    return result


def score_schema_option(schema: Dict[str, Any]) -> int:
    """
    Score a schema option for anyOf/oneOf selection.
    Higher scores = more preferred schemas.
    
    Args:
        schema: Schema option to score
        
    Returns:
        Score (0-3)
    """
    if not schema or not isinstance(schema, dict):
        return 0
    
    # Score 3: Object types with properties (most informative)
    if schema.get("type") == "object" or schema.get("properties"):
        return 3
    
    # Score 2: Array types with items
    if schema.get("type") == "array" or schema.get("items"):
        return 2
    
    # Score 1: Any other non-null type
    if schema.get("type") and schema.get("type") != "null":
        return 1
    
    # Score 0: Null or no type
    return 0


def convert_refs_to_hints(schema: Any) -> Any:
    """
    Convert $ref references to description hints.
    Replaces { $ref: "#/$defs/Foo" } with { type: "object", description: "See: Foo" }
    
    Args:
        schema: Schema to process
        
    Returns:
        Schema with refs converted to hints
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [convert_refs_to_hints(item) for item in schema]
    
    result = dict(schema)
    
    # Handle $ref at this level
    if "$ref" in result and isinstance(result["$ref"], str):
        # Extract definition name from ref path
        parts = result["$ref"].split("/")
        def_name = parts[-1] if parts else "unknown"
        hint = f"See: {def_name}"
        
        # Merge with existing description if present
        existing_desc = result.get("description", "")
        description = f"{existing_desc} ({hint})" if existing_desc else hint
        
        # Replace with object type and hint
        return {"type": "object", "description": description}
    
    # Recursively process properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: convert_refs_to_hints(value)
            for key, value in result["properties"].items()
        }
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [convert_refs_to_hints(item) for item in result["items"]]
        elif isinstance(result["items"], dict):
            result["items"] = convert_refs_to_hints(result["items"])
    
    # Recursively process anyOf/oneOf/allOf
    for key in ["anyOf", "oneOf", "allOf"]:
        if key in result and isinstance(result[key], list):
            result[key] = [convert_refs_to_hints(item) for item in result[key]]
    
    return result


def merge_all_of(schema: Any) -> Any:
    """
    Merge all schemas in an allOf array into a single schema.
    Properties and required arrays are merged; other fields use first occurrence.
    
    Args:
        schema: Schema with potential allOf to merge
        
    Returns:
        Schema with allOf merged
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [merge_all_of(item) for item in schema]
    
    result = dict(schema)
    
    # Process allOf if present
    if "allOf" in result and isinstance(result["allOf"], list) and result["allOf"]:
        merged_properties = {}
        merged_required: Set[str] = set()
        other_fields = {}
        
        for sub_schema in result["allOf"]:
            if not sub_schema or not isinstance(sub_schema, dict):
                continue
            
            # Merge properties (later overrides earlier)
            if "properties" in sub_schema:
                merged_properties.update(sub_schema["properties"])
            
            # Union required arrays
            if "required" in sub_schema and isinstance(sub_schema["required"], list):
                merged_required.update(sub_schema["required"])
            
            # Copy other fields (first occurrence wins)
            for key, value in sub_schema.items():
                if key not in ("properties", "required") and key not in other_fields:
                    other_fields[key] = value
        
        # Apply merged content
        del result["allOf"]
        
        # Merge other fields first (parent takes precedence)
        for key, value in other_fields.items():
            if key not in result:
                result[key] = value
        
        # Merge properties (allOf properties override parent for same keys)
        if merged_properties:
            existing_props = result.get("properties", {})
            result["properties"] = {**merged_properties, **existing_props}
        
        # Merge required
        if merged_required:
            parent_required = result.get("required", [])
            result["required"] = list(set(merged_required) | set(parent_required))
    
    # Recursively process properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: merge_all_of(value)
            for key, value in result["properties"].items()
        }
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [merge_all_of(item) for item in result["items"]]
        elif isinstance(result["items"], dict):
            result["items"] = merge_all_of(result["items"])
    
    return result


def flatten_any_of_one_of(schema: Any) -> Any:
    """
    Flatten anyOf/oneOf by selecting the best option based on scoring.
    Adds type hints to description when multiple types existed.
    
    Args:
        schema: Schema with potential anyOf/oneOf
        
    Returns:
        Flattened schema
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [flatten_any_of_one_of(item) for item in schema]
    
    result = dict(schema)
    
    # Handle anyOf or oneOf
    for union_key in ["anyOf", "oneOf"]:
        if union_key in result and isinstance(result[union_key], list) and result[union_key]:
            options = result[union_key]
            
            # Collect type names for hint
            type_names = []
            best_option = None
            best_score = -1
            
            for option in options:
                if not option or not isinstance(option, dict):
                    continue
                
                # Collect type name
                type_name = option.get("type") or ("object" if option.get("properties") else None)
                if type_name and type_name != "null":
                    type_names.append(type_name)
                
                # Score and track best option
                score = score_schema_option(option)
                if score > best_score:
                    best_score = score
                    best_option = option
            
            # Remove the union key
            del result[union_key]
            
            # Merge best option into result
            if best_option:
                # Preserve parent description
                parent_description = result.get("description")
                
                # Recursively flatten the best option
                flattened_option = flatten_any_of_one_of(best_option)
                
                # Merge fields from selected option
                for key, value in flattened_option.items():
                    if key == "description":
                        # Merge descriptions if different
                        if value and value != parent_description:
                            result["description"] = (
                                f"{parent_description} ({value})" if parent_description else value
                            )
                    elif key not in result or key in ("type", "properties", "items"):
                        result[key] = value
                
                # Add type hint if multiple types existed
                if len(type_names) > 1:
                    unique_types = list(dict.fromkeys(type_names))  # Preserve order, remove dupes
                    result = append_description_hint(result, f"Accepts: {' | '.join(unique_types)}")
    
    # Recursively process properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: flatten_any_of_one_of(value)
            for key, value in result["properties"].items()
        }
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [flatten_any_of_one_of(item) for item in result["items"]]
        elif isinstance(result["items"], dict):
            result["items"] = flatten_any_of_one_of(result["items"])
    
    return result


def add_enum_hints(schema: Any) -> Any:
    """
    Add hints for enum values (if ≤10 values).
    Preserves enum information in the description.
    
    Args:
        schema: Schema to process
        
    Returns:
        Schema with enum hints added to description
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [add_enum_hints(item) for item in schema]
    
    result = dict(schema)
    
    # Add enum hint if present and reasonable size
    if "enum" in result and isinstance(result["enum"], list):
        if 1 < len(result["enum"]) <= 10:
            vals = ", ".join(str(v) for v in result["enum"])
            result = append_description_hint(result, f"Allowed: {vals}")
    
    # Recursively process properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: add_enum_hints(value)
            for key, value in result["properties"].items()
        }
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [add_enum_hints(item) for item in result["items"]]
        else:
            result["items"] = add_enum_hints(result["items"])
    
    return result


def add_additional_properties_hints(schema: Any) -> Any:
    """
    Add hints for additionalProperties: false.
    Informs the model that extra properties are not allowed.
    
    Args:
        schema: Schema to process
        
    Returns:
        Schema with additionalProperties hints added
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [add_additional_properties_hints(item) for item in schema]
    
    result = dict(schema)
    
    if result.get("additionalProperties") is False:
        result = append_description_hint(result, "No extra properties allowed")
    
    # Recursively process properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: add_additional_properties_hints(value)
            for key, value in result["properties"].items()
        }
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [add_additional_properties_hints(item) for item in result["items"]]
        else:
            result["items"] = add_additional_properties_hints(result["items"])
    
    return result


def move_constraints_to_description(schema: Any) -> Any:
    """
    Move unsupported constraints to description hints.
    Preserves constraint information that would otherwise be lost.
    
    Args:
        schema: Schema to process
        
    Returns:
        Schema with constraint hints added to description
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [move_constraints_to_description(item) for item in schema]
    
    CONSTRAINTS = [
        "minLength", "maxLength", "pattern", "minimum", "maximum",
        "minItems", "maxItems", "format"
    ]
    
    result = dict(schema)
    
    for constraint in CONSTRAINTS:
        if constraint in result and not isinstance(result[constraint], dict):
            result = append_description_hint(result, f"{constraint}: {result[constraint]}")
    
    # Recursively process properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: move_constraints_to_description(value)
            for key, value in result["properties"].items()
        }
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [move_constraints_to_description(item) for item in result["items"]]
        else:
            result["items"] = move_constraints_to_description(result["items"])
    
    return result


def flatten_type_arrays(
    schema: Any,
    nullable_props: Optional[Set[str]] = None,
    current_prop_name: Optional[str] = None
) -> Any:
    """
    Flatten array type fields and track nullable properties.
    Converts { type: ["string", "null"] } to { type: "string" } with nullable hint.
    
    Args:
        schema: Schema to process
        nullable_props: Set to collect nullable property names (mutated)
        current_prop_name: Current property name (for tracking)
        
    Returns:
        Flattened schema
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [flatten_type_arrays(item, nullable_props) for item in schema]
    
    result = dict(schema)
    
    # Handle array type fields
    if "type" in result and isinstance(result["type"], list):
        types = result["type"]
        has_null = "null" in types
        non_null_types = [t for t in types if t and t != "null"]
        
        # Select first non-null type, or 'string' as fallback
        first_type = non_null_types[0] if non_null_types else "string"
        result["type"] = first_type
        
        # Add hint for multiple types
        if len(non_null_types) > 1:
            result = append_description_hint(result, f"Accepts: {' | '.join(non_null_types)}")
        
        # Track nullable and add hint
        if has_null:
            result = append_description_hint(result, "nullable")
            if nullable_props is not None and current_prop_name:
                nullable_props.add(current_prop_name)
    
    # Recursively process properties, tracking nullable ones
    if "properties" in result and isinstance(result["properties"], dict):
        child_nullable_props: Set[str] = set()
        new_props = {}
        
        for key, value in result["properties"].items():
            new_props[key] = flatten_type_arrays(value, child_nullable_props, key)
        result["properties"] = new_props
        
        # Remove nullable properties from required array
        if "required" in result and isinstance(result["required"], list) and child_nullable_props:
            result["required"] = [prop for prop in result["required"] if prop not in child_nullable_props]
            if not result["required"]:
                del result["required"]
    
    # Recursively process items
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [flatten_type_arrays(item, nullable_props) for item in result["items"]]
        elif isinstance(result["items"], dict):
            result["items"] = flatten_type_arrays(result["items"], nullable_props)
    
    return result


def sanitize_schema(schema: Any) -> Dict[str, Any]:
    """
    Sanitize JSON Schema for Antigravity API compatibility.
    Uses allowlist approach - only permit known-safe JSON Schema features.
    Converts "const" to equivalent "enum" for compatibility.
    Generates placeholder schema for empty tool schemas.
    
    Args:
        schema: Schema to sanitize
        
    Returns:
        Sanitized schema
    """
    if not schema or not isinstance(schema, dict):
        # Empty/missing schema - generate placeholder with reason property
        return {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Reason for calling this tool"
                }
            },
            "required": ["reason"]
        }
    
    # Allowlist of permitted JSON Schema fields
    ALLOWED_FIELDS = {
        "type", "description", "properties", "required",
        "items", "enum", "title"
    }
    
    sanitized = {}
    
    for key, value in schema.items():
        # Convert "const" to "enum" for compatibility
        if key == "const":
            sanitized["enum"] = [value]
            continue
        
        # Skip fields not in allowlist
        if key not in ALLOWED_FIELDS:
            continue
        
        if key == "properties" and value and isinstance(value, dict):
            sanitized["properties"] = {
                prop_key: sanitize_schema(prop_value)
                for prop_key, prop_value in value.items()
            }
        elif key == "items" and value and isinstance(value, dict):
            if isinstance(value, list):
                sanitized["items"] = [sanitize_schema(item) for item in value]
            else:
                sanitized["items"] = sanitize_schema(value)
        elif isinstance(value, dict) and value:
            sanitized[key] = sanitize_schema(value)
        else:
            sanitized[key] = value
    
    # Ensure we have at least a type
    if "type" not in sanitized:
        sanitized["type"] = "object"
    
    # If object type with no properties, add placeholder
    if sanitized.get("type") == "object":
        props = sanitized.get("properties", {})
        if not props:
            sanitized["properties"] = {
                "reason": {
                    "type": "string",
                    "description": "Reason for calling this tool"
                }
            }
            sanitized["required"] = ["reason"]
    
    return sanitized


def clean_schema_for_gemini(schema: Any) -> Any:
    """
    Cleans JSON schema for Gemini API compatibility.
    Uses a multi-phase pipeline matching opencode-antigravity-auth approach.
    
    Args:
        schema: The JSON schema to clean
        
    Returns:
        Cleaned schema safe for Gemini API
    """
    if not schema or not isinstance(schema, dict):
        return schema
    if isinstance(schema, list):
        return [clean_schema_for_gemini(item) for item in schema]
    
    # Phase 1: Convert $refs to hints
    result = convert_refs_to_hints(schema)
    
    # Phase 1b: Add enum hints (preserves enum info in description)
    result = add_enum_hints(result)
    
    # Phase 1c: Add additionalProperties hints
    result = add_additional_properties_hints(result)
    
    # Phase 1d: Move constraints to description (before they get stripped)
    result = move_constraints_to_description(result)
    
    # Phase 2a: Merge allOf schemas
    result = merge_all_of(result)
    
    # Phase 2b: Flatten anyOf/oneOf
    result = flatten_any_of_one_of(result)
    
    # Phase 2c: Flatten type arrays and update required for nullable
    result = flatten_type_arrays(result)
    
    # Phase 3: Remove unsupported keywords
    unsupported = [
        "additionalProperties", "default", "$schema", "$defs",
        "definitions", "$ref", "$id", "$comment", "title",
        "minLength", "maxLength", "pattern", "format",
        "minItems", "maxItems", "examples", "allOf", "anyOf", "oneOf"
    ]
    
    for key in unsupported:
        result.pop(key, None)
    
    # Check for unsupported 'format' in string types
    if result.get("type") == "string" and "format" in result:
        allowed_formats = ["enum", "date-time"]
        if result["format"] not in allowed_formats:
            del result["format"]
    
    # Phase 4: Final cleanup - recursively clean nested schemas and validate required
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = {
            key: clean_schema_for_gemini(value)
            for key, value in result["properties"].items()
        }
    
    if "items" in result:
        if isinstance(result["items"], list):
            result["items"] = [clean_schema_for_gemini(item) for item in result["items"]]
        elif isinstance(result["items"], dict):
            result["items"] = clean_schema_for_gemini(result["items"])
    
    # Validate that required array only contains properties that exist
    if "required" in result and isinstance(result["required"], list) and "properties" in result:
        defined_props = set(result["properties"].keys())
        result["required"] = [prop for prop in result["required"] if prop in defined_props]
        if not result["required"]:
            del result["required"]
    
    return result


# =============================================================================
# THINKING UTILITIES
# =============================================================================

def is_thinking_part(part: Dict[str, Any]) -> bool:
    """
    Check if a part is a thinking block.
    
    Args:
        part: Content part to check
        
    Returns:
        True if the part is a thinking block
    """
    if not part or not isinstance(part, dict):
        return False
    return (
        part.get("type") == "thinking" or
        part.get("type") == "redacted_thinking" or
        "thinking" in part or
        part.get("thought") is True
    )


def has_valid_signature(part: Dict[str, Any]) -> bool:
    """
    Check if a thinking part has a valid signature (>= MIN_SIGNATURE_LENGTH chars).
    
    Args:
        part: Content part to check
        
    Returns:
        True if part has a valid signature
    """
    if part.get("thought") is True:
        signature = part.get("thoughtSignature", "")
    else:
        signature = part.get("signature", "")
    return isinstance(signature, str) and len(signature) >= MIN_SIGNATURE_LENGTH


def has_gemini_history(messages: List[Dict[str, Any]]) -> bool:
    """
    Check if conversation history contains Gemini-style messages.
    Gemini puts thoughtSignature on tool_use blocks, Claude puts signature on thinking blocks.
    
    Args:
        messages: Array of messages
        
    Returns:
        True if any tool_use has thoughtSignature (Gemini pattern)
    """
    for msg in messages:
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use" and "thoughtSignature" in block:
                return True
    return False


def sanitize_thinking_part(part: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a thinking part by keeping only allowed fields.
    
    Args:
        part: Part to sanitize
        
    Returns:
        Sanitized part
    """
    # Gemini-style thought blocks: { thought: true, text, thoughtSignature }
    if part.get("thought") is True:
        sanitized = {"thought": True}
        if "text" in part:
            sanitized["text"] = part["text"]
        if "thoughtSignature" in part:
            sanitized["thoughtSignature"] = part["thoughtSignature"]
        return sanitized
    
    # Anthropic-style thinking blocks: { type: "thinking", thinking, signature }
    if part.get("type") == "thinking" or "thinking" in part:
        sanitized = {"type": "thinking"}
        if "thinking" in part:
            sanitized["thinking"] = part["thinking"]
        if "signature" in part:
            sanitized["signature"] = part["signature"]
        return sanitized
    
    return part


def sanitize_anthropic_thinking_block(block: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize a thinking block by removing extra fields like cache_control.
    Only keeps: type, thinking, signature (for thinking) or type, data (for redacted_thinking)
    
    Args:
        block: Block to sanitize
        
    Returns:
        Sanitized block
    """
    if not block:
        return block
    
    if block.get("type") == "thinking":
        sanitized = {"type": "thinking"}
        if "thinking" in block:
            sanitized["thinking"] = block["thinking"]
        if "signature" in block:
            sanitized["signature"] = block["signature"]
        return sanitized
    
    if block.get("type") == "redacted_thinking":
        sanitized = {"type": "redacted_thinking"}
        if "data" in block:
            sanitized["data"] = block["data"]
        return sanitized
    
    return block


def filter_unsigned_thinking_blocks(contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter unsigned thinking blocks from contents (Gemini format).
    
    Args:
        contents: Array of content objects in Gemini format
        
    Returns:
        Filtered contents with unsigned thinking blocks removed
    """
    result = []
    for content in contents:
        if not content or not isinstance(content, dict):
            result.append(content)
            continue
        
        if "parts" in content and isinstance(content["parts"], list):
            filtered_parts = []
            for item in content["parts"]:
                if not item or not isinstance(item, dict):
                    filtered_parts.append(item)
                    continue
                
                if not is_thinking_part(item):
                    filtered_parts.append(item)
                    continue
                
                # Keep items with valid signatures
                if has_valid_signature(item):
                    filtered_parts.append(sanitize_thinking_part(item))
                    continue
                
                # Drop unsigned thinking blocks
                logger.debug("[ThinkingUtils] Dropping unsigned thinking block")
            
            result.append({**content, "parts": filtered_parts})
        else:
            result.append(content)
    
    return result


def remove_trailing_thinking_blocks(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove trailing unsigned thinking blocks from assistant messages.
    Claude/Gemini APIs require that assistant messages don't end with unsigned thinking blocks.
    
    Args:
        content: Array of content blocks
        
    Returns:
        Content array with trailing unsigned thinking blocks removed
    """
    if not isinstance(content, list) or not content:
        return content
    
    # Work backwards from the end, removing thinking blocks
    end_index = len(content)
    for i in range(len(content) - 1, -1, -1):
        block = content[i]
        if not block or not isinstance(block, dict):
            break
        
        # Check if it's a thinking block
        if is_thinking_part(block):
            # Check if it has a valid signature
            if not has_valid_signature(block):
                end_index = i
            else:
                break  # Stop at signed thinking block
        else:
            break  # Stop at first non-thinking block
    
    if end_index < len(content):
        removed_count = len(content) - end_index
        logger.debug(f"[ThinkingUtils] Removed {removed_count} trailing unsigned thinking blocks")
        return content[:end_index]
    
    return content


def restore_thinking_signatures(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter thinking blocks: keep only those with valid signatures.
    Blocks without signatures are dropped (API requires signatures).
    Also sanitizes blocks to remove extra fields like cache_control.
    
    Args:
        content: Array of content blocks
        
    Returns:
        Filtered content with only valid signed thinking blocks
    """
    if not isinstance(content, list):
        return content
    
    original_length = len(content)
    filtered = []
    
    for block in content:
        if not block or block.get("type") != "thinking":
            filtered.append(block)
            continue
        
        # Keep blocks with valid signatures, sanitized
        signature = block.get("signature", "")
        if signature and len(signature) >= MIN_SIGNATURE_LENGTH:
            filtered.append(sanitize_anthropic_thinking_block(block))
        # Unsigned thinking blocks are dropped
    
    if len(filtered) < original_length:
        dropped = original_length - len(filtered)
        logger.debug(f"[ThinkingUtils] Dropped {dropped} unsigned thinking block(s)")
    
    return filtered


def reorder_assistant_content(content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reorder content so that:
    1. Thinking blocks come first (required when thinking is enabled)
    2. Text blocks come in the middle (filtering out empty/useless ones)
    3. Tool_use blocks come at the end (required before tool_result)
    
    Args:
        content: Array of content blocks
        
    Returns:
        Reordered content array
    """
    if not isinstance(content, list):
        return content
    
    # Even for single-element arrays, we need to sanitize thinking blocks
    if len(content) == 1:
        block = content[0]
        if block and block.get("type") in ("thinking", "redacted_thinking"):
            return [sanitize_anthropic_thinking_block(block)]
        return content
    
    thinking_blocks = []
    text_blocks = []
    tool_use_blocks = []
    dropped_empty_blocks = 0
    
    for block in content:
        if not block:
            continue
        
        block_type = block.get("type")
        
        if block_type in ("thinking", "redacted_thinking"):
            # Sanitize thinking blocks to remove cache_control and other extra fields
            thinking_blocks.append(sanitize_anthropic_thinking_block(block))
        elif block_type == "tool_use":
            tool_use_blocks.append(block)
        elif block_type == "text":
            # Only keep text blocks with meaningful content
            text = block.get("text", "")
            if text and text.strip():
                text_blocks.append(block)
            else:
                dropped_empty_blocks += 1
        else:
            # Other block types go in the text position
            text_blocks.append(block)
    
    if dropped_empty_blocks > 0:
        logger.debug(f"[ThinkingUtils] Dropped {dropped_empty_blocks} empty text block(s)")
    
    reordered = thinking_blocks + text_blocks + tool_use_blocks
    
    # Log only if actual reordering happened (not just filtering)
    if len(reordered) == len(content):
        original_order = ",".join(b.get("type", "unknown") for b in content if b)
        new_order = ",".join(b.get("type", "unknown") for b in reordered if b)
        if original_order != new_order:
            logger.debug("[ThinkingUtils] Reordered assistant content")
    
    return reordered


# =============================================================================
# THINKING RECOVERY FUNCTIONS
# =============================================================================

def message_has_valid_thinking(message: Dict[str, Any]) -> bool:
    """
    Check if a message has any VALID (signed) thinking blocks.
    Only counts thinking blocks that have valid signatures.
    
    Args:
        message: Message to check
        
    Returns:
        True if message has valid signed thinking blocks
    """
    content = message.get("content") or message.get("parts", [])
    if not isinstance(content, list):
        return False
    
    for block in content:
        if not is_thinking_part(block):
            continue
        # Check for valid signature (Anthropic style)
        signature = block.get("signature", "")
        if signature and len(signature) >= MIN_SIGNATURE_LENGTH:
            return True
        # Check for thoughtSignature (Gemini style on functionCall)
        thought_sig = block.get("thoughtSignature", "")
        if thought_sig and len(thought_sig) >= MIN_SIGNATURE_LENGTH:
            return True
    return False


def message_has_tool_use(message: Dict[str, Any]) -> bool:
    """Check if a message has tool_use blocks."""
    content = message.get("content") or message.get("parts", [])
    if not isinstance(content, list):
        return False
    return any(
        isinstance(block, dict) and (block.get("type") == "tool_use" or "functionCall" in block)
        for block in content
    )


def message_has_tool_result(message: Dict[str, Any]) -> bool:
    """Check if a message has tool_result blocks."""
    content = message.get("content") or message.get("parts", [])
    if not isinstance(content, list):
        return False
    return any(
        isinstance(block, dict) and (block.get("type") == "tool_result" or "functionResponse" in block)
        for block in content
    )


def is_plain_user_message(message: Dict[str, Any]) -> bool:
    """Check if message is a plain user text message (not tool_result)."""
    if message.get("role") != "user":
        return False
    content = message.get("content") or message.get("parts", [])
    if not isinstance(content, list):
        return isinstance(content, str)
    # Check if it has tool_result blocks
    return not any(
        isinstance(block, dict) and (block.get("type") == "tool_result" or "functionResponse" in block)
        for block in content
    )


def analyze_conversation_state(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze conversation state to detect if we're in a corrupted state.
    
    Args:
        messages: Array of messages
        
    Returns:
        State dict with inToolLoop, interruptedTool, turnHasThinking, etc.
    """
    if not messages:
        return {"inToolLoop": False, "interruptedTool": False, "turnHasThinking": False, "toolResultCount": 0}
    
    # Find the last assistant message
    last_assistant_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") in ("assistant", "model"):
            last_assistant_idx = i
            break
    
    if last_assistant_idx == -1:
        return {"inToolLoop": False, "interruptedTool": False, "turnHasThinking": False, "toolResultCount": 0}
    
    last_assistant = messages[last_assistant_idx]
    has_tool_use = message_has_tool_use(last_assistant)
    has_thinking = message_has_valid_thinking(last_assistant)
    
    # Count trailing tool results after the assistant message
    tool_result_count = 0
    has_plain_user_message_after = False
    for i in range(last_assistant_idx + 1, len(messages)):
        if message_has_tool_result(messages[i]):
            tool_result_count += 1
        if is_plain_user_message(messages[i]):
            has_plain_user_message_after = True
    
    # We're in a tool loop if: assistant has tool_use AND there are tool_results after
    in_tool_loop = has_tool_use and tool_result_count > 0
    
    # We have an interrupted tool if: assistant has tool_use, NO tool_results,
    # but there IS a plain user message after (user interrupted and sent new message)
    interrupted_tool = has_tool_use and tool_result_count == 0 and has_plain_user_message_after
    
    return {
        "inToolLoop": in_tool_loop,
        "interruptedTool": interrupted_tool,
        "turnHasThinking": has_thinking,
        "toolResultCount": tool_result_count,
        "lastAssistantIdx": last_assistant_idx
    }


def needs_thinking_recovery(messages: List[Dict[str, Any]]) -> bool:
    """
    Check if conversation needs thinking recovery.
    
    Recovery is only needed when:
    1. We're in a tool loop or have an interrupted tool, AND
    2. No valid thinking blocks exist in the current turn
    
    Args:
        messages: Array of messages
        
    Returns:
        True if thinking recovery is needed
    """
    state = analyze_conversation_state(messages)
    
    # Recovery is only needed in tool loops or interrupted tools
    if not state["inToolLoop"] and not state["interruptedTool"]:
        return False
    
    # Need recovery if no valid thinking blocks exist
    return not state["turnHasThinking"]


def strip_invalid_thinking_blocks(
    messages: List[Dict[str, Any]],
    target_family: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Strip invalid or incompatible thinking blocks from messages.
    Keeps valid thinking blocks to preserve context from previous turns.
    
    Args:
        messages: Array of messages
        target_family: Target model family ('claude' or 'gemini')
        
    Returns:
        Messages with invalid thinking blocks removed
    """
    stripped_count = 0
    result = []
    
    for msg in messages:
        content = msg.get("content") or msg.get("parts")
        if not isinstance(content, list):
            result.append(msg)
            continue
        
        filtered = []
        for block in content:
            # Keep non-thinking blocks
            if not is_thinking_part(block):
                filtered.append(block)
                continue
            
            # Check generic validity (has signature of sufficient length)
            if not has_valid_signature(block):
                stripped_count += 1
                continue
            
            # Check family compatibility only for Gemini targets
            # Claude can validate its own signatures, so we don't drop for Claude
            if target_family == "gemini":
                signature = block.get("thoughtSignature") if block.get("thought") is True else block.get("signature")
                signature_family = signature_cache.get_cached_signature_family(signature) if signature else None
                
                # For Gemini: drop unknown or mismatched signatures
                if not signature_family or signature_family != target_family:
                    stripped_count += 1
                    continue
            
            filtered.append(block)
        
        # Use '.' instead of '' because claude models reject empty text parts
        if "content" in msg:
            new_content = filtered if filtered else [{"type": "text", "text": "."}]
            result.append({**msg, "content": new_content})
        elif "parts" in msg:
            new_parts = filtered if filtered else [{"text": "."}]
            result.append({**msg, "parts": new_parts})
        else:
            result.append(msg)
    
    if stripped_count > 0:
        logger.debug(f"[ThinkingUtils] Stripped {stripped_count} invalid/incompatible thinking block(s)")
    
    return result


def close_tool_loop_for_thinking(
    messages: List[Dict[str, Any]],
    target_family: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Close tool loop by injecting synthetic messages.
    This allows the model to start a fresh turn when thinking is corrupted.
    
    Args:
        messages: Array of messages
        target_family: Target model family ('claude' or 'gemini')
        
    Returns:
        Modified messages with synthetic messages injected
    """
    state = analyze_conversation_state(messages)
    
    # Handle neither tool loop nor interrupted tool
    if not state["inToolLoop"] and not state["interruptedTool"]:
        return messages
    
    # Strip only invalid/incompatible thinking blocks (keep valid ones)
    modified = strip_invalid_thinking_blocks(list(messages), target_family)
    
    if state["interruptedTool"]:
        # For interrupted tools: just strip thinking and add a synthetic assistant message
        # to acknowledge the interruption before the user's new message
        insert_idx = state["lastAssistantIdx"] + 1
        
        # Insert synthetic assistant message acknowledging interruption
        modified.insert(insert_idx, {
            "role": "assistant",
            "content": [{"type": "text", "text": "[Tool call was interrupted.]"}]
        })
        
        logger.debug("[ThinkingUtils] Applied thinking recovery for interrupted tool")
        
    elif state["inToolLoop"]:
        # For tool loops: add synthetic messages to close the loop
        tool_result_count = state["toolResultCount"]
        synthetic_text = (
            "[Tool execution completed.]" if tool_result_count == 1
            else f"[{tool_result_count} tool executions completed.]"
        )
        
        # Inject synthetic model message to complete the turn
        modified.append({
            "role": "assistant",
            "content": [{"type": "text", "text": synthetic_text}]
        })
        
        # Inject synthetic user message to start fresh
        modified.append({
            "role": "user",
            "content": [{"type": "text", "text": "[Continue]"}]
        })
        
        logger.debug("[ThinkingUtils] Applied thinking recovery for tool loop")
    
    return modified


# =============================================================================
# CONTENT CONVERTER
# =============================================================================

def convert_role(role: str) -> str:
    """
    Convert Anthropic role to Google role.
    
    Args:
        role: Anthropic role ('user', 'assistant')
        
    Returns:
        Google role ('user', 'model')
    """
    if role == "assistant":
        return "model"
    if role == "user":
        return "user"
    return "user"  # Default to user


def convert_content_to_parts(
    content: Union[str, List[Dict[str, Any]]],
    is_claude_model: bool = False,
    is_gemini_model: bool = False
) -> List[Dict[str, Any]]:
    """
    Convert Anthropic message content to Google Generative AI parts.
    
    Args:
        content: Anthropic message content (string or array of blocks)
        is_claude_model: Whether the model is a Claude model
        is_gemini_model: Whether the model is a Gemini model
        
    Returns:
        Google Generative AI parts array
    """
    if isinstance(content, str):
        return [{"text": content}]
    
    if not isinstance(content, list):
        return [{"text": str(content)}]
    
    parts = []
    
    for block in content:
        if not block:
            continue
        
        block_type = block.get("type")
        
        if block_type == "text":
            # Skip empty text blocks - they cause API errors
            text = block.get("text", "")
            if text and text.strip():
                parts.append({"text": text})
                
        elif block_type == "image":
            # Handle image content
            source = block.get("source", {})
            if source.get("type") == "base64":
                # Base64-encoded image
                parts.append({
                    "inlineData": {
                        "mimeType": source.get("media_type"),
                        "data": source.get("data")
                    }
                })
            elif source.get("type") == "url":
                # URL-referenced image
                parts.append({
                    "fileData": {
                        "mimeType": source.get("media_type", "image/jpeg"),
                        "fileUri": source.get("url")
                    }
                })
                
        elif block_type == "document":
            # Handle document content (e.g. PDF)
            source = block.get("source", {})
            if source.get("type") == "base64":
                parts.append({
                    "inlineData": {
                        "mimeType": source.get("media_type"),
                        "data": source.get("data")
                    }
                })
            elif source.get("type") == "url":
                parts.append({
                    "fileData": {
                        "mimeType": source.get("media_type", "application/pdf"),
                        "fileUri": source.get("url")
                    }
                })
                
        elif block_type == "tool_use":
            # Convert tool_use to functionCall (Google format)
            function_call = {
                "name": block.get("name"),
                "args": block.get("input", {})
            }
            
            if is_claude_model and block.get("id"):
                function_call["id"] = block["id"]
            
            # Build the part with functionCall
            part: Dict[str, Any] = {"functionCall": function_call}
            
            # For Gemini models, include thoughtSignature at the part level
            if is_gemini_model:
                # Priority: block.thoughtSignature > cache > GEMINI_SKIP_SIGNATURE
                sig = block.get("thoughtSignature")
                
                if not sig and block.get("id"):
                    sig = signature_cache.get_cached_signature(block["id"])
                    if sig:
                        logger.debug(f"[ContentConverter] Restored signature from cache for: {block['id']}")
                
                part["thoughtSignature"] = sig or GEMINI_SKIP_SIGNATURE
            
            parts.append(part)
            
        elif block_type == "tool_result":
            # Convert tool_result to functionResponse (Google format)
            response_content = block.get("content")
            image_parts = []
            
            if isinstance(response_content, str):
                response_content = {"result": response_content}
            elif isinstance(response_content, list):
                # Extract images from tool results
                for item in response_content:
                    if isinstance(item, dict) and item.get("type") == "image":
                        source = item.get("source", {})
                        if source.get("type") == "base64":
                            image_parts.append({
                                "inlineData": {
                                    "mimeType": source.get("media_type"),
                                    "data": source.get("data")
                                }
                            })
                
                # Extract text content
                texts = [
                    c.get("text", "") for c in response_content
                    if isinstance(c, dict) and c.get("type") == "text"
                ]
                text_content = "\n".join(texts)
                response_content = {"result": text_content or ("Image attached" if image_parts else "")}
            
            function_response = {
                "name": block.get("tool_use_id", "unknown"),
                "response": response_content
            }
            
            # For Claude models, the id field must match the tool_use_id
            if is_claude_model and block.get("tool_use_id"):
                function_response["id"] = block["tool_use_id"]
            
            parts.append({"functionResponse": function_response})
            
            # Add any images from the tool result as separate parts
            parts.extend(image_parts)
            
        elif block_type == "thinking":
            # Handle thinking blocks with signature compatibility check
            signature = block.get("signature", "")
            if signature and len(signature) >= MIN_SIGNATURE_LENGTH:
                signature_family = signature_cache.get_cached_signature_family(signature)
                target_family = "claude" if is_claude_model else ("gemini" if is_gemini_model else None)
                
                # Drop blocks with incompatible signatures for Gemini (cross-model switch)
                if is_gemini_model and signature_family and target_family and signature_family != target_family:
                    logger.debug(f"[ContentConverter] Dropping incompatible {signature_family} thinking for {target_family} model")
                    continue
                
                # Drop blocks with unknown signature origin for Gemini (cold cache - safe default)
                if is_gemini_model and not signature_family and target_family:
                    logger.debug("[ContentConverter] Dropping thinking with unknown signature origin")
                    continue
                
                # Compatible - convert to Gemini format with signature
                parts.append({
                    "text": block.get("thinking", ""),
                    "thought": True,
                    "thoughtSignature": signature
                })
            # Unsigned thinking blocks are dropped (existing behavior)
    
    return parts


# =============================================================================
# REQUEST CONVERTER
# =============================================================================

def convert_anthropic_to_google(anthropic_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Anthropic Messages API request to the format expected by Cloud Code.
    
    Uses Google Generative AI format, but for Claude models:
    - Keeps tool_result in Anthropic format (required by Claude API)
    
    Args:
        anthropic_request: Anthropic format request
        
    Returns:
        Request body for Cloud Code API
    """
    messages = anthropic_request.get("messages", [])
    system = anthropic_request.get("system")
    max_tokens = anthropic_request.get("max_tokens")
    temperature = anthropic_request.get("temperature")
    top_p = anthropic_request.get("top_p")
    top_k = anthropic_request.get("top_k")
    stop_sequences = anthropic_request.get("stop_sequences")
    tools = anthropic_request.get("tools")
    thinking = anthropic_request.get("thinking")
    
    model_name = anthropic_request.get("model", "")
    model_family = get_model_family(model_name)
    is_claude_model = model_family == ModelFamily.CLAUDE
    is_gemini_model = model_family == ModelFamily.GEMINI
    is_thinking = is_thinking_model(model_name)
    
    google_request: Dict[str, Any] = {
        "contents": [],
        "generationConfig": {}
    }
    
    # Handle system instruction
    if system:
        system_parts = []
        if isinstance(system, str):
            system_parts = [{"text": system}]
        elif isinstance(system, list):
            # Filter for text blocks
            system_parts = [
                {"text": block["text"]}
                for block in system
                if isinstance(block, dict) and block.get("type") == "text"
            ]
        
        if system_parts:
            google_request["systemInstruction"] = {"parts": system_parts}
    
    # Add interleaved thinking hint for Claude thinking models with tools
    if is_claude_model and is_thinking and tools:
        hint = (
            "Interleaved thinking is enabled. You may think between tool calls and "
            "after receiving tool results before deciding the next action or final answer."
        )
        if "systemInstruction" not in google_request:
            google_request["systemInstruction"] = {"parts": [{"text": hint}]}
        else:
            last_part = google_request["systemInstruction"]["parts"][-1]
            if "text" in last_part:
                last_part["text"] = f"{last_part['text']}\n\n{hint}"
            else:
                google_request["systemInstruction"]["parts"].append({"text": hint})
    
    # Apply thinking recovery for thinking models when needed
    processed_messages = messages
    
    if is_gemini_model and is_thinking and needs_thinking_recovery(messages):
        logger.debug("[RequestConverter] Applying thinking recovery for Gemini")
        processed_messages = close_tool_loop_for_thinking(messages, "gemini")
    
    # For Claude: apply recovery only for cross-model (Gemini→Claude) switch
    if is_claude_model and is_thinking and has_gemini_history(messages) and needs_thinking_recovery(messages):
        logger.debug("[RequestConverter] Applying thinking recovery for Claude (cross-model from Gemini)")
        processed_messages = close_tool_loop_for_thinking(messages, "claude")
    
    # Convert messages to contents, then filter unsigned thinking blocks
    for msg in processed_messages:
        msg_content = msg.get("content", [])
        
        # For assistant messages, process thinking blocks and reorder content
        if msg.get("role") in ("assistant", "model") and isinstance(msg_content, list):
            # First, try to restore signatures for unsigned thinking blocks from cache
            msg_content = restore_thinking_signatures(msg_content)
            # Remove trailing unsigned thinking blocks
            msg_content = remove_trailing_thinking_blocks(msg_content)
            # Reorder: thinking first, then text, then tool_use
            msg_content = reorder_assistant_content(msg_content)
        
        parts = convert_content_to_parts(msg_content, is_claude_model, is_gemini_model)
        
        # SAFETY: Google API requires at least one part per content message
        if not parts:
            logger.warn("[RequestConverter] WARNING: Empty parts array after filtering, adding placeholder")
            parts = [{"text": "."}]
        
        content = {
            "role": convert_role(msg.get("role", "user")),
            "parts": parts
        }
        google_request["contents"].append(content)
    
    # Filter unsigned thinking blocks for Claude models
    if is_claude_model:
        google_request["contents"] = filter_unsigned_thinking_blocks(google_request["contents"])
    
    # Generation config
    if max_tokens:
        google_request["generationConfig"]["maxOutputTokens"] = max_tokens
    if temperature is not None:
        google_request["generationConfig"]["temperature"] = temperature
    if top_p is not None:
        google_request["generationConfig"]["topP"] = top_p
    if top_k is not None:
        google_request["generationConfig"]["topK"] = top_k
    if stop_sequences:
        google_request["generationConfig"]["stopSequences"] = stop_sequences
    
    # Enable thinking for thinking models (Claude and Gemini 3+)
    if is_thinking:
        if is_claude_model:
            # Claude thinking config
            thinking_config: Dict[str, Any] = {"include_thoughts": True}
            
            # Only set thinking_budget if explicitly provided
            thinking_budget = thinking.get("budget_tokens") if thinking else None
            if thinking_budget:
                thinking_config["thinking_budget"] = thinking_budget
                logger.debug(f"[RequestConverter] Claude thinking enabled with budget: {thinking_budget}")
                
                # Validate max_tokens > thinking_budget as required by the API
                current_max_tokens = google_request["generationConfig"].get("maxOutputTokens")
                if current_max_tokens and current_max_tokens <= thinking_budget:
                    adjusted = thinking_budget + 8192
                    logger.warn(
                        f"[RequestConverter] max_tokens ({current_max_tokens}) <= thinking_budget ({thinking_budget}). "
                        f"Adjusting to {adjusted}"
                    )
                    google_request["generationConfig"]["maxOutputTokens"] = adjusted
            else:
                logger.debug("[RequestConverter] Claude thinking enabled (no budget specified)")
            
            google_request["generationConfig"]["thinkingConfig"] = thinking_config
            
        elif is_gemini_model:
            # Gemini thinking config (uses camelCase)
            budget = thinking.get("budget_tokens", 16000) if thinking else 16000
            thinking_config = {
                "includeThoughts": True,
                "thinkingBudget": budget
            }
            logger.debug(f"[RequestConverter] Gemini thinking enabled with budget: {budget}")
            google_request["generationConfig"]["thinkingConfig"] = thinking_config
    
    # Convert tools to Google format
    if tools:
        function_declarations = []
        for idx, tool in enumerate(tools):
            # Extract name from various possible locations
            name = (
                tool.get("name") or
                tool.get("function", {}).get("name") or
                tool.get("custom", {}).get("name") or
                f"tool-{idx}"
            )
            
            # Extract description
            description = (
                tool.get("description") or
                tool.get("function", {}).get("description") or
                tool.get("custom", {}).get("description") or
                ""
            )
            
            # Extract schema
            schema = (
                tool.get("input_schema") or
                tool.get("function", {}).get("input_schema") or
                tool.get("function", {}).get("parameters") or
                tool.get("custom", {}).get("input_schema") or
                tool.get("parameters") or
                {"type": "object"}
            )
            
            # Sanitize schema for general compatibility
            parameters = sanitize_schema(schema)
            
            # For Gemini models, apply additional cleaning for VALIDATED mode
            if is_gemini_model:
                parameters = clean_schema_for_gemini(parameters)
            
            # Clean name to valid identifier
            clean_name = re.sub(r"[^a-zA-Z0-9_-]", "_", str(name))[:64]
            
            function_declarations.append({
                "name": clean_name,
                "description": description,
                "parameters": parameters
            })
        
        google_request["tools"] = [{"functionDeclarations": function_declarations}]
        logger.debug(f"[RequestConverter] Tools: {str(google_request['tools'])[:300]}")
    
    # Cap max tokens for Gemini models
    if is_gemini_model:
        current_max = google_request["generationConfig"].get("maxOutputTokens", 0)
        if current_max > GEMINI_MAX_OUTPUT_TOKENS:
            logger.debug(
                f"[RequestConverter] Capping Gemini max_tokens from {current_max} to {GEMINI_MAX_OUTPUT_TOKENS}"
            )
            google_request["generationConfig"]["maxOutputTokens"] = GEMINI_MAX_OUTPUT_TOKENS
    
    return google_request


# =============================================================================
# RESPONSE CONVERTER
# =============================================================================

def generate_message_id() -> str:
    """Generate a random message ID."""
    return f"msg_{secrets.token_hex(16)}"


def generate_tool_id() -> str:
    """Generate a random tool use ID."""
    return f"toolu_{secrets.token_hex(12)}"


def convert_google_to_anthropic(google_response: Dict[str, Any], model: str) -> Dict[str, Any]:
    """
    Convert Google Generative AI response to Anthropic Messages API format.
    
    Args:
        google_response: Google format response (the inner response object)
        model: The model name used
        
    Returns:
        Anthropic format response
    """
    # Handle the response wrapper
    response = google_response.get("response", google_response)
    
    candidates = response.get("candidates", [])
    first_candidate = candidates[0] if candidates else {}
    content = first_candidate.get("content", {})
    parts = content.get("parts", [])
    
    # Convert parts to Anthropic content blocks
    anthropic_content = []
    has_tool_calls = False
    
    for part in parts:
        if "text" in part:
            # Handle thinking blocks
            if part.get("thought") is True:
                signature = part.get("thoughtSignature", "")
                
                # Cache thinking signature with model family for cross-model compatibility
                if signature and len(signature) >= MIN_SIGNATURE_LENGTH:
                    model_family = get_model_family(model)
                    family_str = model_family.value if model_family != ModelFamily.UNKNOWN else None
                    if family_str:
                        signature_cache.cache_thinking_signature(signature, family_str)
                
                # Include thinking blocks in the response for Claude Code
                anthropic_content.append({
                    "type": "thinking",
                    "thinking": part["text"],
                    "signature": signature
                })
            else:
                anthropic_content.append({
                    "type": "text",
                    "text": part["text"]
                })
                
        elif "functionCall" in part:
            # Convert functionCall to tool_use
            fc = part["functionCall"]
            tool_id = fc.get("id") or generate_tool_id()
            
            tool_use_block: Dict[str, Any] = {
                "type": "tool_use",
                "id": tool_id,
                "name": fc.get("name"),
                "input": fc.get("args", {})
            }
            
            # For Gemini 3+, include thoughtSignature from the part level
            thought_sig = part.get("thoughtSignature", "")
            if thought_sig and len(thought_sig) >= MIN_SIGNATURE_LENGTH:
                tool_use_block["thoughtSignature"] = thought_sig
                # Cache for future requests (Claude Code may strip this field)
                signature_cache.cache_signature(tool_id, thought_sig)
            
            anthropic_content.append(tool_use_block)
            has_tool_calls = True
    
    # Determine stop reason
    finish_reason = first_candidate.get("finishReason", "")
    stop_reason = "end_turn"
    if finish_reason == "STOP":
        stop_reason = "end_turn"
    elif finish_reason == "MAX_TOKENS":
        stop_reason = "max_tokens"
    elif finish_reason == "TOOL_USE" or has_tool_calls:
        stop_reason = "tool_use"
    
    # Extract usage metadata
    # Note: Antigravity's promptTokenCount is the TOTAL (includes cached),
    # but Anthropic's input_tokens excludes cached. We subtract to match.
    usage_metadata = response.get("usageMetadata", {})
    prompt_tokens = usage_metadata.get("promptTokenCount", 0)
    cached_tokens = usage_metadata.get("cachedContentTokenCount", 0)
    
    return {
        "id": generate_message_id(),
        "type": "message",
        "role": "assistant",
        "content": anthropic_content if anthropic_content else [{"type": "text", "text": ""}],
        "model": model,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {
            "input_tokens": prompt_tokens - cached_tokens,
            "output_tokens": usage_metadata.get("candidatesTokenCount", 0),
            "cache_read_input_tokens": cached_tokens,
            "cache_creation_input_tokens": 0
        }
    }
