# ~/clientity/src/clientity/core/adapters/_aiohttp.py
from __future__ import annotations
import typing as t, asyncio as aio

import aiohttp as ah

from clientity.logs import log
from clientity.core.hints import Embodied
from clientity.core.primitives import MethodType
from clientity.core.adapters.base import Adapter

Interadapts = t.Union[
    None, t.Any,
    ah.ClientSession
]

class AIOHTTP:
    class Request(t.NamedTuple):
        url: str
        method: str
        kwargs: dict


class AiohttpAdapter(Adapter[AIOHTTP.Request]):
    def __init__(
        self,
        interface: Interadapts = None
        ) -> None:
        log.debug(f"(adapter[aiohttp]) received interface: {interface}")
        provided = not ((interface is None) or (interface is ah))
        self.interface = None if not provided else interface

    def build(
        self,
        url: str,
        method: MethodType,
        params: t.Optional[dict] = None,
        body: t.Optional[Embodied] = None
        ) -> AIOHTTP.Request:
        kwargs = {}
        if params:
            kwargs['params'] = params
        if body:
            key, data = body
            kwargs[key] = data
        req = AIOHTTP.Request(
            url=url,
            method=str(method),
            kwargs=kwargs
        )
        log.debug(f"(adapter[aiohttp].build) built request: {req}")
        return req

    async def send(
        self,
        request: AIOHTTP.Request
        ) -> ah.ClientResponse:
        if isinstance(self.interface, ah.ClientSession):
            return await self.interface.request(
                request.method,
                request.url,
                **request.kwargs
            )
        log.debug(f"(adapter[aiohttp].send) using temporary session to send: {request}")
        async with ah.ClientSession() as interface:
            return await interface.request(
                request.method,
                request.url,
                **request.kwargs
            )

    @classmethod
    def Compatible(cls, interface: t.Any) -> bool:
        return (
            (interface is ah) or
            isinstance(interface, ah.ClientSession)
        )
