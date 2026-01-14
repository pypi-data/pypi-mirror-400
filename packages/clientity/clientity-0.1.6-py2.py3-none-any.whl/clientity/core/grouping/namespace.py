# ~/clientity/src/clientity/core/grouping/namespace.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import Responded
from clientity.core.utils import http, bound, synced
from clientity.core.endpoint import Endpoint
from clientity.core.adapters import Adapter, adapt
from clientity.core.protocols import (
    Located, Interface, Interfacing
)
from clientity.core.primitives import (
    Bound, Instructions,
    URL, Location, Locatable
)
from clientity.core.grouping.base import Grouping, WrappedEndpoint
from clientity.core.grouping.resource import Resource


class Namespace(Grouping):
    base: str
    adapter: t.Optional[Adapter] = None
    interface: t.Optional[Interface] = None

    def __init__(
        self,
        base: str = "",
        name: str = "",
        interface: t.Optional[Interfacing] = None
        ) -> None:
        self.base = base.rstrip("/")
        self.name = name if name else (http.domain(self.base) if self.base else "")
        if interface is not None:
            self.interface = interface if( not callable(interface)) else (synced(interface)())
            self.adapter = adapt(self.interface)

    @property
    def independent(self) -> bool:
        return (self.interface is not None)

    def __wrap__(self, endpoint: Endpoint, exhaust: bool = False) -> WrappedEndpoint:
        if self.adapter is None:
            log.debug(f"(Namespace[{self.name}]) passing through endpoint: {endpoint.location}")
            return endpoint
        log.debug(f"(Namespace[{self.name}]) wrapping endpoint @ {endpoint.location}")
        base, adapter, instructions = self.base, self.adapter, endpoint.instructions()
        async def wrapper(*args, **kwargs) -> Responded:
            return await http.execute(
                base, adapter, instructions,
                exhaust, *args, **kwargs
            )
        return bound(endpoint, wrapper)

    def __nest__(self, child: Located) -> Resource:
        if not isinstance(child, Resource):
            raise TypeError(f"(Namespace[{self.name}]) cannot nest: {child.__class__.__name__}")
        log.debug(f"(Namespace[{self.name}]) nesting resource: {child.name})")
        nested = Resource(child.location)
        for name, endpoint in child.endpoints():
            original = str(endpoint.location).removeprefix(str(child.location)).lstrip('/')
            setattr(nested, name, endpoint.mutate(location=Location(original)))
        return nested

    def __matmul__(self, base: str) -> 'Namespace':
        log.debug(f"(Namespace) basing @ {base}")
        return Namespace(base, self.name, self.interface)

    def __getattr__(self, name: str) -> t.Any:
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")


def namespace(interface: t.Optional[Interfacing] = None, base: str = "", name: str = "") -> Namespace:
    return Namespace(base=base, name=name, interface=interface)
