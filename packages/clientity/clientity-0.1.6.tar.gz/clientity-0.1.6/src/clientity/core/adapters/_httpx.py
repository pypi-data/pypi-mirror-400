# ~/clientity/src/clientity/core/adapters/_httpx.py
from __future__ import annotations
import typing as t, asyncio as aio

import httpx as hx

from clientity.logs import log
from clientity.core.hints import Embodied
from clientity.core.primitives import MethodType
from clientity.core.adapters.base import Adapter


Interadapts = t.Union[
    None, t.Any,
    hx.Client,
    hx.AsyncClient
]

class HttpxAdapter(Adapter[hx.Request]):
    def __init__(self, interface: Interadapts = None) -> None:
        log.debug(f"(adapter[httpx]) received interface: {interface}")
        inter = hx.AsyncClient() if (interface is None) or (interface is hx) else interface
        self.interface = inter


    def build(
        self,
        url: str,
        method: MethodType,
        params: t.Optional[dict] = None,
        body: t.Optional[Embodied] = None
        ) -> hx.Request:
        kwargs = {}
        if params:
            kwargs['params'] = params
        if body:
            key, data = body
            kwargs[key] = data
        req = self.interface.build_request(str(method), url, **kwargs)
        log.debug(f"(adapter[httpx].build) built request: {req}")
        return req


    async def send(
        self,
        request: hx.Request
        ) -> hx.Response:
        if isinstance(self.interface, hx.AsyncClient):
            return await self.interface.send(request)
        return await aio.to_thread(self.interface.send, request)


    @classmethod
    def Compatible(cls, interface: t.Any) -> bool:
        return (
            (interface is hx) or
            isinstance(interface, (hx.Client, hx.AsyncClient))
        )
