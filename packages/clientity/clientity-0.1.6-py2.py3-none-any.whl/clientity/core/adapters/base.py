# ~/clientity/src/clientity/core/adapters/base.py
from __future__ import annotations
import abc, typing as t

from clientity.logs import log
from clientity.core.hints import (
    Embodied, ResponseObject, RequestObject
)
from clientity.core.primitives import MethodType


class Adapter(abc.ABC, t.Generic[RequestObject]):
    @abc.abstractmethod
    def build(
        self,
        url: str,
        method: MethodType,
        params: t.Optional[dict] = None,
        body: t.Optional[Embodied] = None,
        ) -> RequestObject:
            ...


    @abc.abstractmethod
    async def send(
        self,
        request: RequestObject
        ) -> ResponseObject:
        ...

    @classmethod
    @abc.abstractmethod
    def Compatible(
        cls,
        interface: t.Any
        ) -> bool:
        ...
