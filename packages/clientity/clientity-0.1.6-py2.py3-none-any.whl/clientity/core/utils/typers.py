# ~/clientity/src/clientity/core/utils/typers.py
from __future__ import annotations
import typing as t

from clientity.core.hints import Callable, ResponseObject
from clientity.core.utils.calls import asynced
from clientity.core.primitives.bound import (
    B, Bound
)

def bound(ref: B, caller: t.Optional[Callable.Async] = None) -> Bound:
    call = caller
    if call is None:
        if callable(ref):
            call = asynced(ref.__call__)
        raise ValueError("...")
    return Bound(ref, call)
