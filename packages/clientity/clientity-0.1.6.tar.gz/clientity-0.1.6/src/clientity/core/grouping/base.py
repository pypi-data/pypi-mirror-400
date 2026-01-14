# ~/clientity/src/clientity/core/grouping/base.py
from __future__ import annotations
import abc, typing as t

from clientity.logs import log
from clientity.core.hints import Responded
from clientity.core.endpoint import Endpoint
from clientity.core.protocols import Located
from clientity.core.primitives import (
    Location, Locatable,
    Bound, Instructions
)

if t.TYPE_CHECKING:
    from clientity.core.adapters import Adapter

WrappedEndpoint = t.Union[Endpoint, Bound[Endpoint]]
GroupedEndpoint = tuple[str, Endpoint]
GroupedGrouping = tuple[str, 'Grouping']

class Grouping(abc.ABC):

    @abc.abstractmethod
    def __wrap__(self, endpoint: Endpoint) -> WrappedEndpoint:
        ...

    @abc.abstractmethod
    def __nest__(self, child: Located) -> 'Grouping':
        ...

    def __getattr__(self, name: str) -> t.Any:
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: t.Any) -> None:
        v = value
        if isinstance(value, Endpoint):
            v = self.__wrap__(value)
        if isinstance(value, Grouping):
            if not isinstance(value, Located):
                raise TypeError(f"({self.__class__.__name__}) cannot nest: {value.__class__.__name__}")
            v = self.__nest__(value)
        super().__setattr__(name, v)

    def endpoints(self) -> t.Iterator[GroupedEndpoint]:
        def ref(ep: WrappedEndpoint) -> t.Optional[Endpoint]:
            if isinstance(ep, Endpoint): return ep
            if isinstance(ep, Bound):
                if isinstance(ep.__ref__, Endpoint):
                    return ep.__ref__
            return None
        for name, value in self.__dict__.items():
            if name.startswith('_'): continue
            if (endpoint:=ref(value)) is not None:
                yield name, endpoint

    def groupings(self) -> t.Iterator[GroupedGrouping]:
        for name, value in self.__dict__.items():
            if name.startswith('_'): continue
            if isinstance(value, Grouping):
                yield name, value
