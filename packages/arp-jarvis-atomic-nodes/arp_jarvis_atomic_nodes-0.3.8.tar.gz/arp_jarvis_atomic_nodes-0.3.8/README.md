# JARVIS Atomic Nodes (Node Pack)

First-party “node pack” for the JARVIS stack. This package provides:
- **NodeType metadata** for Node Registry + Selection
- **Atomic handler implementations** for Atomic Executor

This is a trusted, in-process node pack (v0.x). It does **not** implement runtime code download.

## Install

Metadata-only (safe for Node Registry):

```bash
python3 -m pip install arp-jarvis-atomic-nodes
```

Or explicitly:

```bash
python3 -m pip install "arp-jarvis-atomic-nodes[metadata]"
```

Runtime handlers (Atomic Executor):

```bash
python3 -m pip install "arp-jarvis-atomic-nodes[runtime]"
```

## Usage

### NodeType metadata (Node Registry)

```python
from jarvis_atomic_nodes.catalog import node_types

node_type_list = node_types()
```

### Handler registry (Atomic Executor)

```python
from jarvis_atomic_nodes.handlers import handlers

handler_map = handlers(require_http=True)
```

### Authoring nodes (JSON-first)

```python
from typing import Any

from jarvis_atomic_nodes.sdk import atomic_node, NodeContext

HEALTH_INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "base_url": {"type": ["string", "null"]},
    },
    "required": ["base_url"],
}

HEALTH_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "status_code": {"type": "integer"},
        "text": {"type": "string"},
    },
    "required": ["status_code", "text"],
}

@atomic_node(
    name="acme.api.health",
    side_effect="read",
    input_schema=HEALTH_INPUT_SCHEMA,
    output_schema=HEALTH_OUTPUT_SCHEMA,
)
async def acme_api_health(inputs: dict[str, Any], ctx: NodeContext) -> dict[str, Any]:
    """Call `GET /health` on an existing service and return the raw response text."""
    base_url = (inputs.get("base_url") or "").strip()
    if not base_url:
        raise ValueError("Missing base_url")
    resp = await ctx.http.get(f"{base_url.rstrip('/')}/health")
    return {"status_code": resp.status_code, "text": resp.text}
```

### Entry point discovery

This package exposes a NodePack entry point:

- group: `jarvis.nodepacks`
- name: `jarvis.core`
- object: `jarvis_atomic_nodes.pack:core_pack`

```python
from jarvis_atomic_nodes.discovery import load_nodepacks, load_handlers, load_node_types

packs = load_nodepacks()
handlers = load_handlers()
node_types = load_node_types()
```

## NodeType `extensions` metadata

Each NodeType emitted by this pack includes JARVIS metadata in `NodeType.extensions`, including:
- `jarvis.pack_id` / `jarvis.pack_version` (provenance)
- `jarvis.node_name` (stable node name)
- `jarvis.side_effect`, `jarvis.trust_tier` (governance hints)
- Optional: `jarvis.egress_policy`, `jarvis.budget_hints`, `jarvis.tags`

Node Registry stores these fields verbatim and Selection Service may use a subset to enrich candidate ranking.

Full cross-stack list: `https://github.com/AgentRuntimeProtocol/BusinessDocs/blob/main/Business_Docs/JARVIS/Extensions.md`.

## Included nodes (v0.3.7 baseline)

Core:
- `jarvis.core.echo`
- `jarvis.core.sleep`
- `jarvis.core.uuid4`
- `jarvis.core.time.now`
- `jarvis.core.hash.sha256`

HTTP:
- `jarvis.web.fetch`
