from __future__ import annotations

import base64
import json
import os
from typing import Any
from urllib.parse import urlparse

from .sdk import NodeContext, atomic_node

_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
_DEFAULT_TIMEOUT = 10.0
_DEFAULT_MAX_BYTES = 1024 * 1024

_KEY_VALUE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "key": {"type": "string"},
        "value": {"type": "string"},
    },
    "required": ["key", "value"],
}

_WEB_FETCH_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "url": {"type": "string"},
        "method": {"type": ["string", "null"]},
        "headers": {"type": ["array", "null"], "items": _KEY_VALUE_SCHEMA},
        "params": {"type": ["array", "null"], "items": _KEY_VALUE_SCHEMA},
        "json": {"type": ["string", "null"]},
        "body": {"type": ["string", "null"]},
        "timeout_seconds": {"type": ["number", "null"]},
        "max_bytes": {"type": ["integer", "null"]},
        "follow_redirects": {"type": ["boolean", "null"]},
    },
    "required": [
        "url",
        "method",
        "headers",
        "params",
        "json",
        "body",
        "timeout_seconds",
        "max_bytes",
        "follow_redirects",
    ],
}

_WEB_FETCH_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status_code": {"type": "integer"},
        "headers": {"type": "array", "items": _KEY_VALUE_SCHEMA},
        "content_type": {"type": ["string", "null"]},
        "content_base64": {"type": "string"},
        "final_url": {"type": "string"},
        "content_bytes": {"type": "integer"},
    },
    "required": [
        "status_code",
        "headers",
        "content_type",
        "content_base64",
        "final_url",
        "content_bytes",
    ],
}


def _env_csv(name: str) -> set[str]:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return set()
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _env_float(name: str) -> float | None:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _env_int(name: str) -> int | None:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _pairs_to_str_dict(items: list[dict[str, Any]] | None) -> dict[str, str]:
    if not items:
        return {}
    result: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("headers/params must be objects")
        key = item.get("key")
        value = item.get("value")
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("headers/params items must have string key/value")
        result[key] = value
    return result


def _parse_json_body(raw: str | None) -> Any | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValueError("json must be a string")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("json must be valid JSON") from exc


@atomic_node(
    name="jarvis.web.fetch",
    side_effect="read",
    trust_tier="first_party",
    egress_policy="external_http",
    input_schema=_WEB_FETCH_INPUT_SCHEMA,
    output_schema=_WEB_FETCH_OUTPUT_SCHEMA,
)
async def web_fetch(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Fetch a URL over HTTP(S) and return response bytes (base64)."""
    url = inputs.get("url")
    if not isinstance(url, str):
        raise ValueError("url must be a string")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("url scheme must be http or https")
    if not parsed.hostname:
        raise ValueError("url must include a hostname")

    host = (parsed.hostname or "").lower()

    if allowed := _env_csv("JARVIS_ATOMIC_HTTP_ALLOWED_HOSTS"):
        if host not in allowed:
            raise ValueError("host not allowed")
    if host in _env_csv("JARVIS_ATOMIC_HTTP_BLOCKED_HOSTS"):
        raise ValueError("host blocked")

    method = inputs.get("method") or "GET"
    if not isinstance(method, str):
        raise ValueError("method must be a string")
    method = method.upper()
    if method not in _ALLOWED_METHODS:
        raise ValueError(f"method {method} not allowed")

    headers = _pairs_to_str_dict(inputs.get("headers"))
    params = _pairs_to_str_dict(inputs.get("params"))
    json_payload = _parse_json_body(inputs.get("json"))

    body = inputs.get("body")
    if body is not None and not isinstance(body, str):
        raise ValueError("body must be a string")

    timeout_seconds = inputs.get("timeout_seconds")
    if timeout_seconds is None:
        timeout_seconds = _env_float("JARVIS_ATOMIC_HTTP_TIMEOUT_SECONDS") or _DEFAULT_TIMEOUT
    if not isinstance(timeout_seconds, (int, float)):
        raise ValueError("timeout_seconds must be a number")

    max_bytes = inputs.get("max_bytes")
    if max_bytes is None:
        max_bytes = _env_int("JARVIS_ATOMIC_HTTP_MAX_BYTES") or _DEFAULT_MAX_BYTES
    if not isinstance(max_bytes, int):
        raise ValueError("max_bytes must be an integer")

    follow_redirects = inputs.get("follow_redirects")
    if follow_redirects is None:
        follow_redirects = False
    if not isinstance(follow_redirects, bool):
        raise ValueError("follow_redirects must be a boolean")

    if ctx.http is None:
        try:
            import httpx
        except ModuleNotFoundError as exc:  # pragma: no cover - runtime only
            raise RuntimeError("httpx is required for jarvis.web.fetch; install [runtime].") from exc
        async with httpx.AsyncClient(follow_redirects=follow_redirects, timeout=timeout_seconds) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                content=body.encode("utf-8") if isinstance(body, str) else None,
                json=json_payload,
            )
    else:
        response = await ctx.http.request(
            method,
            url,
            headers=headers,
            params=params,
            content=body.encode("utf-8") if isinstance(body, str) else None,
            json=json_payload,
            timeout=timeout_seconds,
            follow_redirects=follow_redirects,
        )

    content = response.content
    if len(content) > max_bytes:
        raise ValueError("response too large")

    return {
        "status_code": response.status_code,
        "headers": [
            {"key": key, "value": value} for key, value in sorted(response.headers.items())
        ],
        "content_type": response.headers.get("content-type"),
        "content_base64": base64.b64encode(content).decode("utf-8"),
        "final_url": str(response.url),
        "content_bytes": len(content),
    }
