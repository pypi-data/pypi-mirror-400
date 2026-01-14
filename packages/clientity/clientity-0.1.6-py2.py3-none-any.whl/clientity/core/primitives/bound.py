# ~/clientity/src/clientity/core/primitives/bound.py
from __future__ import annotations
import typing as t

from clientity.core.hints import Callable, Call, Requesting, Responding
from clientity.core.utils.calls import asynced

B = t.TypeVar("B")
class Bound(t.Generic[B]):
    __ref__: B
    __caller__: Callable.Async

    def __init__(self, ref: B, caller: Callable.Async) -> None:
        self.__ref__ = ref
        self.__caller__ = caller

    async def __call__(self, *args, **kwargs):
        return await self.__caller__(*args, **kwargs)

    if t.TYPE_CHECKING:
        def __matmul__(self, path: str) -> 'Bound[B]': ...
        def __mod__(self, model: Requesting) -> 'Bound[B]': ...
        def __lshift__(self, model: Requesting) -> 'Bound[B]': ...
        def __rshift__(self, model: Responding) -> 'Bound[B]': ...
        def __and__(self, call: Call) -> 'Bound[B]': ...
        def __or__(self, call: Call) -> 'Bound[B]': ...
