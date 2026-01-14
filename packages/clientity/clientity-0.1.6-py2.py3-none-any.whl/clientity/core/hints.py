# ~/clientity/src/clientity/core/hints.py
from __future__ import annotations
import typing as t, types as ts, typing_extensions as tx

_T = t.TypeVar("_T")
_R = t.TypeVar('_R')
Stringable = t.Union[str, int, float]

class Callable:
    Sync = t.Callable[..., _T]
    Async = t.Callable[..., t.Coroutine[t.Any, t.Any, _T]]

type Call = t.Union[
    Callable.Sync,
    Callable.Async
]

Synced = t.Union[Callable.Sync, t.Any]
Asynced = t.Union[Callable.Async, t.Any]


RequestObject = t.TypeVar("RequestObject")
ResponseType = t.Type[_R]
ResponseObject = t.TypeVar("ResponseObject")
ResponseCoroutine = t.Coroutine[t.Any, t.Any, ResponseObject]

type Embodied = tuple[str, t.Union[dict, bytes]]

if t.TYPE_CHECKING:
    from clientity.core.protocols.models import Requestable, Responsive

Requesting = t.Union[None, t.Any, t.Type['Requestable']]
Responding = t.Union[None, ResponseType, t.Type['Responsive']]
Responded = t.Union[ResponseObject, 'Responsive']
Requested = t.Union['Requestable', dict, bytes, t.Any]
