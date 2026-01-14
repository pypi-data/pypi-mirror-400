# ~/clientity/src/clientity/core/adapters/_requests.py
from __future__ import annotations
import typing as t, asyncio as aio

import requests as rq

from clientity.logs import log
from clientity.core.hints import Embodied
from clientity.core.primitives import MethodType
from clientity.core.adapters.base import Adapter

Interadapts = t.Union[
    rq.Session,
    t.Any,
    None
]

class RequestsAdapter(Adapter[rq.PreparedRequest]):
    def __init__(self, interface: Interadapts = None) -> None:
        log.debug(f"(adapter[requests]) received interface: {interface}")
        inter = rq.Session() if (interface is None) or (interface is rq) else interface
        self.interface = inter

    def build(
        self,
        url: str,
        method: MethodType,
        params: t.Optional[dict] = None,
        body: t.Optional[Embodied] = None
        ) -> rq.PreparedRequest:
        kwargs = {}
        if params:
            kwargs['params'] = params
        if body:
            key, data = body
            kwargs[key] = data
        req = rq.Request(str(method), url, **kwargs)
        log.debug(f"(adapter[requests].build) built request: {req}")
        return self.interface.prepare_request(req)


    async def send(
        self,
        request: rq.PreparedRequest
        ) -> rq.Response:
        return await aio.to_thread(self.interface.send, request)

    @classmethod
    def Compatible(cls, interface: t.Any) -> bool:
        return (
            (interface is rq) or
            isinstance(interface, rq.Session)
        )
