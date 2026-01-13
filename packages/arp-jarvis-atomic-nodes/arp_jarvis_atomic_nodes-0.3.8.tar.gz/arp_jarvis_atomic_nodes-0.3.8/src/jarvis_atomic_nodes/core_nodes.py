from __future__ import annotations

import asyncio
import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from .sdk import NodeContext, atomic_node


_ECHO_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "echo": {"type": "string"},
    },
    "required": ["echo"],
}

_ECHO_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "echo": {"type": "string"},
    },
    "required": ["echo"],
}

_SLEEP_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "seconds": {"type": ["number", "null"]},
        "duration_seconds": {"type": ["number", "null"]},
    },
    "required": ["seconds", "duration_seconds"],
}

_SLEEP_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "slept_seconds": {"type": "number"},
    },
    "required": ["slept_seconds"],
}

_UUID4_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {},
    "required": [],
}

_UUID4_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "uuid4": {"type": "string"},
    },
    "required": ["uuid4"],
}

_TIME_NOW_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {},
    "required": [],
}

_TIME_NOW_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "time": {"type": "string"},
    },
    "required": ["time"],
}

_HASH_SHA256_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "content_base64": {"type": ["string", "null"]},
        "text": {"type": ["string", "null"]},
        "encoding": {"type": ["string", "null"]},
    },
    "required": ["content_base64", "text", "encoding"],
}

_HASH_SHA256_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "sha256": {"type": "string"},
    },
    "required": ["sha256"],
}


@atomic_node(
    name="jarvis.core.echo",
    side_effect="read",
    input_schema=_ECHO_INPUT_SCHEMA,
    output_schema=_ECHO_OUTPUT_SCHEMA,
)
async def core_echo(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Return the provided `echo` string (deterministic baseline node)."""
    _ = ctx
    echo = inputs.get("echo")
    if not isinstance(echo, str):
        raise ValueError("echo must be a string")
    return {"echo": echo}


@atomic_node(
    name="jarvis.core.sleep",
    side_effect="read",
    input_schema=_SLEEP_INPUT_SCHEMA,
    output_schema=_SLEEP_OUTPUT_SCHEMA,
)
async def core_sleep(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Sleep for a number of seconds (best-effort)."""
    _ = ctx
    seconds = inputs.get("seconds")
    duration_seconds = inputs.get("duration_seconds")

    if seconds is None:
        seconds = duration_seconds or 0.0
    if not isinstance(seconds, (int, float)):
        raise ValueError("seconds must be a number")
    if seconds < 0:
        raise ValueError("seconds must be >= 0")
    if seconds:
        await asyncio.sleep(float(seconds))
    return {"slept_seconds": float(seconds)}


@atomic_node(
    name="jarvis.core.uuid4",
    side_effect="read",
    input_schema=_UUID4_INPUT_SCHEMA,
    output_schema=_UUID4_OUTPUT_SCHEMA,
)
async def core_uuid4(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Generate a UUIDv4 string."""
    _ = inputs, ctx
    return {"uuid4": str(uuid.uuid4())}


@atomic_node(
    name="jarvis.core.time.now",
    side_effect="read",
    input_schema=_TIME_NOW_INPUT_SCHEMA,
    output_schema=_TIME_NOW_OUTPUT_SCHEMA,
)
async def core_time_now(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Return the current UTC time in ISO-8601 format."""
    _ = inputs, ctx
    return {"time": datetime.now(timezone.utc).isoformat()}


@atomic_node(
    name="jarvis.core.hash.sha256",
    side_effect="read",
    input_schema=_HASH_SHA256_INPUT_SCHEMA,
    output_schema=_HASH_SHA256_OUTPUT_SCHEMA,
)
async def core_hash_sha256(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Compute SHA-256 for text or base64 content."""
    _ = ctx
    content_base64 = inputs.get("content_base64")
    text = inputs.get("text")
    encoding = inputs.get("encoding") or "utf-8"

    if content_base64 is None and text is None:
        raise ValueError("Provide either content_base64 or text")

    if not isinstance(encoding, str):
        raise ValueError("encoding must be a string")

    if content_base64 is not None:
        if not isinstance(content_base64, str):
            raise ValueError("content_base64 must be a string")
        data = base64.b64decode(content_base64.encode("utf-8"), validate=True)
    else:
        if text is not None and not isinstance(text, str):
            raise ValueError("text must be a string")
        data = (text or "").encode(encoding)

    digest = hashlib.sha256(data).hexdigest()
    return {"sha256": digest}
