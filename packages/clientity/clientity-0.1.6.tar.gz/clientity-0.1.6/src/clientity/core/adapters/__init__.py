# ~/clientity/src/clientity/core/adapters/__init__.py
from __future__ import annotations
import typing as t

from .base import Adapter

def adapt(interface: t.Any) -> Adapter:
    from ._httpx import HttpxAdapter
    from ._aiohttp import AiohttpAdapter
    from ._requests import RequestsAdapter

    if not interface: raise ValueError(f"No interface provided for adaptation")
    for A in [HttpxAdapter, AiohttpAdapter, RequestsAdapter]:
        if A.Compatible(interface):
            return A(interface)

    raise ValueError(f"No adapter available for: {type(interface).__name__}")
