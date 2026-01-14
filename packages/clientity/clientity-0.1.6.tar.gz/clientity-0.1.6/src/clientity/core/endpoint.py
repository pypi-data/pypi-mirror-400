# ~/clientity/src/clientity/core/endpoint.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import Call, Requesting, Responding
from clientity.core.primitives import (
    MethodType, Location, Locatable, Instructions, Hooks,
    GET, PUT, HEAD, POST, PATCH, DELETE, OPTIONS
)
if t.TYPE_CHECKING:
    from clientity.core.primitives.bound import Bound

class Endpoint:
    __copying__: set[str] = {
        'method', 'location', 'hooks',
        'querying', 'requesting', 'responding'
    }
    hooks: Hooks
    method: MethodType
    location: Location
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

    @property
    def name(self) -> str:
        return self.location.name

    def __copy(self, **updates) -> 'Endpoint':
        data = {
            attr: updates.get(attr, getattr(self, attr))
            for attr in self.__copying__
        }
        return Endpoint(**data)

    def mutate(self, **kwargs) -> 'Endpoint': return self.__copy(**kwargs)


    def at(self, path: Locatable) -> 'Endpoint':
        location = Location(path)
        return self.__copy(location=location)

    def prehook(self, call: Call) -> 'Endpoint':
        hooks = Hooks(
            pre=[*self.hooks.pre, call],
            post=self.hooks.post.copy()
        )
        return self.__copy(hooks=hooks)

    def posthook(self, call: Call) -> 'Endpoint':
        hooks = Hooks(
            pre=self.hooks.pre.copy(),
            post=[*self.hooks.post, call]
        )
        return self.__copy(hooks=hooks)

    def queries(self, model: Requesting) -> 'Endpoint':
        return self.__copy(querying=model)

    def requests(self, model: Requesting) -> 'Endpoint':
        return self.__copy(requesting=model)

    def responds(self, model: Responding) -> 'Endpoint':
        return self.__copy(responding=model)

    def instructions(self) -> 'Instructions':
        data = {
            attr: getattr(self, attr)
            for attr in self.__copying__
        }
        return Instructions(**data)


    def __call__(self, *args, **kwargs) -> Instructions:
        """When called, return Instructions (to be executed by client)."""
        # For now just return the instructions
        # The client wrapper will handle args/kwargs at execution time
        return self.instructions()

    if t.TYPE_CHECKING:
        def __matmul__(self, path: str) -> "Bound['Endpoint']": ...
        def __mod__(self, model: Requesting) -> "Bound['Endpoint']": ...
        def __lshift__(self, model: Requesting) -> "Bound['Endpoint']": ...
        def __rshift__(self, model: Responding) -> "Bound['Endpoint']": ...
        def __and__(self, call: Call) -> "Bound['Endpoint']": ...
        def __or__(self, call: Call) -> "Bound['Endpoint']": ...
    else:
        # operators
        def __matmul__(self, path: Locatable) -> 'Endpoint':
            """@ - location"""
            return self.at(path)

        def __mod__(self, model: Requesting) -> 'Endpoint':
            """% - query model"""
            return self.queries(model)

        def __lshift__(self, model: Requesting) -> 'Endpoint':
            """<< - body model"""
            return self.requests(model)

        def __rshift__(self, model: Responding) -> 'Endpoint':
            """>> - response model"""
            return self.responds(model)

        def __and__(self, call: Call) -> 'Endpoint':
            """& - pre-hook"""
            return self.prehook(call)

        def __or__(self, call: Call) -> 'Endpoint':
            """| - post-hook"""
            return self.posthook(call)


class __Factory:
    @property
    def get(self) -> Endpoint: return Endpoint(GET)
    @property
    def post(self) -> Endpoint: return Endpoint(POST)
    @property
    def put(self) -> Endpoint: return Endpoint(PUT)
    @property
    def patch(self) -> Endpoint: return Endpoint(PATCH)
    @property
    def delete(self) -> Endpoint: return Endpoint(DELETE)
    @property
    def head(self) -> Endpoint: return Endpoint(HEAD)
    @property
    def options(self) -> Endpoint: return Endpoint(OPTIONS)

endpoint = __Factory()
