from __future__ import annotations

import logging
from collections.abc import Callable
from importlib.metadata import entry_points
from typing import Any

from arp_standard_model import AtomicExecuteRequest, NodeType

from .sdk import NodePack

AtomicHandler = Callable[[AtomicExecuteRequest], Any]

logger = logging.getLogger(__name__)


def load_nodepacks() -> list[NodePack]:
    eps = entry_points()
    if hasattr(eps, "select"):
        selected = eps.select(group="jarvis.nodepacks")
    elif isinstance(eps, dict):  # pragma: no cover - older Python
        selected = eps.get("jarvis.nodepacks", [])
    else:  # pragma: no cover - safety fallback
        selected = []
    packs: list[NodePack] = []
    for ep in selected:
        pack = ep.load()
        if not isinstance(pack, NodePack):
            raise TypeError(f"Entry point {ep.name} did not return a NodePack")
        packs.append(pack)
    logger.info("Loaded node packs (count=%s)", len(packs))
    return packs


def load_node_types() -> list[NodeType]:
    node_types: list[NodeType] = []
    for pack in load_nodepacks():
        node_types.extend(pack.node_types())
    logger.info("Loaded node types (count=%s)", len(node_types))
    return node_types


def load_handlers() -> dict[str, AtomicHandler]:
    handlers: dict[str, AtomicHandler] = {}
    for pack in load_nodepacks():
        handlers.update(pack.handlers())
    logger.info("Loaded atomic handlers (count=%s)", len(handlers))
    return handlers
