from __future__ import annotations

import asyncio
import copy
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Optional, overload

from arp_standard_model import AtomicExecuteRequest, ConstraintEnvelope, Extensions, NodeKind, NodeType

JsonObject = dict[str, Any]
JsonSchema = Mapping[str, Any]


@dataclass
class NodeContext:
    """Execution context passed into atomic nodes."""

    run_id: str
    node_run_id: str
    trace_id: str | None = None
    principal: str | None = None
    budgets: dict[str, Any] | None = None
    clients: dict[str, Any] = field(default_factory=dict)

    @property
    def http(self) -> Any | None:
        return self.clients.get("http")


@dataclass(frozen=True)
class AtomicNodeSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    side_effect: str = "read"
    trust_tier: str = "first_party"
    egress_policy: str | None = None
    budget_hints: dict[str, Any] | None = None
    tags: list[str] | None = None
    constraints: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None


class AtomicNode:
    def __init__(self, spec: AtomicNodeSpec, fn: Callable[..., Any]) -> None:
        self.spec = spec
        self.fn = fn

    async def ainvoke(self, inp: JsonObject | None, ctx: NodeContext) -> JsonObject:
        payload = _ensure_json_object(inp, "inputs")
        result = self.fn(payload, ctx)
        if inspect.isawaitable(result):
            result = await result
        return _ensure_json_object(result, "outputs")

    def invoke(self, inp: JsonObject | None, ctx: NodeContext) -> JsonObject:
        result = self.fn(_ensure_json_object(inp, "inputs"), ctx)
        if inspect.isawaitable(result):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(_awaitable(result))
            raise RuntimeError("invoke() cannot be used while an event loop is running; use ainvoke().")
        return _ensure_json_object(result, "outputs")

    def as_handler(self) -> Callable[[AtomicExecuteRequest], Any]:
        async def _handler(request: AtomicExecuteRequest) -> dict[str, object]:
            ctx = NodeContext(run_id=request.run_id, node_run_id=request.node_run_id)
            output = await self.ainvoke(request.inputs or {}, ctx)
            return output

        return _handler


@overload
def atomic_node(fn: Callable[..., Any]) -> AtomicNode: ...


@overload
def atomic_node(
    *,
    name: str | None = None,
    description: str | None = None,
    input_schema: Mapping[str, Any] | None = None,
    output_schema: Mapping[str, Any] | None = None,
    side_effect: str = "read",
    trust_tier: str = "first_party",
    egress_policy: str | None = None,
    budget_hints: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    constraints: dict[str, Any] | None = None,
    evaluation: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], AtomicNode]: ...


def atomic_node(
    fn: Optional[Callable[..., Any]] = None,
    *,
    name: str | None = None,
    description: str | None = None,
    input_schema: Mapping[str, Any] | None = None,
    output_schema: Mapping[str, Any] | None = None,
    side_effect: str = "read",
    trust_tier: str = "first_party",
    egress_policy: str | None = None,
    budget_hints: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    constraints: dict[str, Any] | None = None,
    evaluation: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], AtomicNode] | AtomicNode:
    def _wrap(fn: Callable[..., Any]) -> AtomicNode:
        if input_schema is None or output_schema is None:
            raise ValueError("input_schema and output_schema are required for JSON-first atomic nodes")

        desc = description or (inspect.getdoc(fn) or "").strip()
        if not desc:
            desc = f"Atomic node: {fn.__name__}"

        spec = AtomicNodeSpec(
            name=name or fn.__name__,
            description=desc,
            input_schema=_to_schema_dict(input_schema),
            output_schema=_to_schema_dict(output_schema),
            side_effect=side_effect,
            trust_tier=trust_tier,
            egress_policy=egress_policy,
            budget_hints=budget_hints,
            tags=tags,
            constraints=constraints,
            evaluation=evaluation,
        )
        return AtomicNode(spec=spec, fn=fn)

    return _wrap if fn is None else _wrap(fn)


@dataclass(frozen=True)
class NodePack:
    pack_id: str
    version: str
    nodes: Iterable[AtomicNode]

    def node_types(self) -> list[NodeType]:
        return [node_to_node_type(self.pack_id, self.version, node) for node in self.nodes]

    def handlers(self) -> Mapping[str, Callable[[AtomicExecuteRequest], Any]]:
        return {node.spec.name: node.as_handler() for node in self.nodes}


def node_to_node_type(pack_id: str, version: str, node: AtomicNode) -> NodeType:
    extensions: dict[str, Any] = {
        "jarvis.pack_id": pack_id,
        "jarvis.pack_version": version,
        "jarvis.node_name": node.spec.name,
        "jarvis.side_effect": node.spec.side_effect,
        "jarvis.trust_tier": node.spec.trust_tier,
    }
    if node.spec.egress_policy is not None:
        extensions["jarvis.egress_policy"] = node.spec.egress_policy
    if node.spec.budget_hints is not None:
        extensions["jarvis.budget_hints"] = node.spec.budget_hints
    if node.spec.tags is not None:
        extensions["jarvis.tags"] = node.spec.tags

    return NodeType(
        node_type_id=node.spec.name,
        version=version,
        kind=NodeKind.atomic,
        description=node.spec.description,
        input_schema=copy.deepcopy(node.spec.input_schema),
        output_schema=copy.deepcopy(node.spec.output_schema),
        constraints=ConstraintEnvelope.model_validate(node.spec.constraints)
        if node.spec.constraints is not None
        else None,
        evaluation=node.spec.evaluation,
        extensions=Extensions.model_validate(extensions),
    )


def _ensure_json_object(value: Any, label: str) -> JsonObject:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _to_schema_dict(schema: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(schema, Mapping):
        raise TypeError("schema must be a mapping")
    return dict(schema)


async def _awaitable(result: Any) -> Any:
    return await result
