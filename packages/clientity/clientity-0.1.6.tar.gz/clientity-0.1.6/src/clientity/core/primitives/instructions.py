# ~/clientity/src/clientity/core/primitives/instructions.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import Call, Callable, Requesting, Responding
from clientity.core.utils.calls import asynced
from clientity.core.primitives.url import Location, Locatable
from clientity.core.primitives.method import MethodType


class Hooks:
    pre: list[Call]
    post: list[Call]

    def __init__(
        self,
        pre: t.Optional[list[Call]] = None,
        post: t.Optional[list[Call]] = None
    ) -> None:
        self.pre = (pre or [])
        self.post = (post or [])

    @property
    def before(self) -> list[Callable.Async]:
        return [asynced(hook) for hook in self.pre]

    @property
    def after(self) -> list[Callable.Async]:
        return [asynced(hook) for hook in self.post]


class Instructions:
    __merging__: t.ClassVar[set[str]] = {
        'method', 'location', 'hooks',
        'querying', 'requesting', 'responding'
    }

    method: MethodType
    location: Location
    hooks: Hooks

    querying: Requesting
    requesting: Requesting
    responding: Responding

    def __init__(
        self,
        method: MethodType,
        location: Locatable = "",
        *,
        hooks: t.Optional[Hooks] = None,
        querying: Requesting = None,
        requesting: Requesting = None,
        responding: Responding = None
    ) -> None:
        self.method = method
        self.location = Location(location)
        self.hooks = (hooks or Hooks())
        self.querying = querying
        self.requesting = requesting
        self.responding = responding

    def prehook(self, *calls: Call) -> None:
        self.hooks.pre.extend([asynced(call) for call in calls])

    def posthook(self, *calls: Call) -> None:
        self.hooks.post.extend([asynced(call) for call in calls])

    def merge(self, **updates: t.Any) -> 'Instructions':
        data = {
            attr: updates.get(attr, getattr(self, attr))
            for attr in self.__merging__
        }
        return Instructions(**data)

    def prepend(self, prefix: Locatable) -> 'Instructions':
        location = Location(prefix)
        return self.merge(location=(location / self.location))
