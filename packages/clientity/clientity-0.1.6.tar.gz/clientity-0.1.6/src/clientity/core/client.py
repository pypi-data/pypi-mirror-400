# ~/clientity/src/clientity/core/client.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import ResponseObject, Responded
from clientity.core.utils import http, bound, synced
from clientity.core.endpoint import Endpoint
from clientity.core.grouping import (
    Grouping, Namespace, Resource
)
from clientity.core.protocols import (
    Interface,
    Interfacing
)
from clientity.core.primitives import (
    URL, Location, Locatable,
    Instructions, Bound
)
from clientity.core.adapters import adapt, Adapter

Binds = dict[str, Bound[Endpoint]]

class Client:
    __bound__: Binds
    base: str
    interface: Interface

    def __init__(
        self,
        interface: Interfacing,
        base: str = "",
        name: str = ""
        ) -> None:
        self.__bound__ = {}
        self.name = (name or http.domain(base))
        self.base = base.rstrip("/")
        self.interface = interface if (not callable(interface)) else (synced(interface)())
        self.adapter: Adapter = adapt(self.interface)

    def __wrap(self, endpoint: Endpoint, exhaust: bool = False) -> Bound[Endpoint]:
        base, adapter, instructions = self.base, self.adapter, endpoint.instructions()
        async def wrapper(*args, **kwargs) -> Responded:
            return await http.execute(
                base, adapter, instructions,
                exhaust, *args, **kwargs
            )
        return bound(endpoint, wrapper)

    def __spaced(self, namespace: Namespace) -> Namespace:
        log.debug(f"(Client[{self.name}]) preparing namespace for attribution: {namespace.name}")
        if namespace.independent:
            log.debug(f"(Client[{self.name}]) namespace[{namespace.name}] is independent, returning as is")
            return namespace
        wrapped = Namespace(base=self.base, name=namespace.name)
        wrapped.adapter = self.adapter
        wrapped.interface = self.interface
        for name, endpoint in namespace.endpoints():
            setattr(wrapped, name, self.__wrap(endpoint))
        for name, group in namespace.groupings():
            if not isinstance(group, (Resource, Namespace)):
                log.warning(f"(Client[{self.name}]) unknown grouping type: {type(group).__name__}")
                continue
            grouping = self.__sourced(group) if isinstance(group, Resource) else self.__spaced(group)
            setattr(wrapped, name, grouping)
        return wrapped

    def __sourced(self, resource: Resource) -> Resource:
        log.debug(f"(Client[{self.name}]) preparing resource for attribution: {resource.name}")
        wrapped = Resource(resource.location)
        for name, endpoint in resource.endpoints():
            setattr(wrapped, name, self.__wrap(endpoint))
        for name, group in resource.groupings():
            if not isinstance(group, (Resource, Namespace)):
                log.warning(f"(Client[{self.name}]) unknown grouping type: {type(group).__name__}")
                continue
            grouping = self.__sourced(group) if isinstance(group, Resource) else self.__spaced(group)
            # bypass __setattr__ to avoid re-nesting
            object.__setattr__(wrapped, name, grouping)
        return wrapped

    def __getattr__(self, name: str) -> t.Any:
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: t.Any) -> None:
        default = lambda v: v
        setter = default
        special = [(Endpoint, self.__wrap), (Resource, self.__sourced), (Namespace, self.__spaced)]
        for vtype, method in special:
            if isinstance(value, vtype):
                setter = method
                break
        attr = setter(value)
        if isinstance(value, Endpoint):
            self.__bound__[name] = attr
        super().__setattr__(name, attr)

    def __matmul__(self, base: str) -> 'Client':
        """@ - set base URL"""
        return Client(self.interface, base=base, name=self.name)


def client(interface: Interfacing) -> Client:
    return Client(interface)


"""
def __getattr__(self, name: str) -> Bound[Endpoint]:#t.Union[Bound[Endpoint], Grouping]:
    if name in self.__bound__:
        return self.__bound__[name]
    raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
"""
