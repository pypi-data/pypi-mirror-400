"""AI CLI adapters registry."""

from __future__ import annotations

import importlib

from .base import AIAdapter, ResponseCollector
from .generic import GenericAdapter


def get_adapter(name: str) -> AIAdapter:
    """Get an adapter instance by name.

    Loads adapter dynamically from registry to avoid duplication.
    """
    from ai_comm.registry import CLI_REGISTRY

    info = CLI_REGISTRY.get(name)
    if info is None:
        return GenericAdapter()

    module = importlib.import_module(info.adapter_module)
    class_name = f"{name.capitalize()}Adapter"
    adapter_class: type[AIAdapter] = getattr(module, class_name)
    return adapter_class()


def list_adapters() -> list[str]:
    """List available adapter names."""
    from ai_comm.registry import list_cli_names

    return list_cli_names()


__all__ = [
    "AIAdapter",
    "GenericAdapter",
    "ResponseCollector",
    "get_adapter",
    "list_adapters",
]
