# ~/clientity/src/clientity/core/grouping/resource.py
from __future__ import annotations
import typing as t

from clientity.logs import log
from clientity.core.hints import Responded
from clientity.core.utils import bound
from clientity.core.endpoint import Endpoint
from clientity.core.protocols import Located
from clientity.core.primitives import (
    Location, Locatable,
    Bound, Instructions,
)
from clientity.core.grouping.base import Grouping

class Resource(Grouping):
    location: Location

    def __init__(
        self,
        location: Locatable = ""
        ) -> None:
        self.location = Location(location)

    @property
    def name(self) -> str:
        return self.location.name

    def __matmul__(self, path: Locatable) -> 'Resource':
        location = Location(path)
        log.debug(f"(Resource[{self.name}]) setting path @ {location}")
        return Resource(location)

    def __wrap__(self, endpoint: Endpoint) -> Endpoint:
        log.debug(f"(Resource[{self.name}]) wrapping endpoint: {endpoint.location}")
        prepended = (self.location / endpoint.location)
        wrapped =  endpoint.mutate(location=prepended)
        log.debug(f"(Resource[{self.name}]) wrapped endpoint: {wrapped.location}")
        return wrapped

    def __nest__(self, child: Located) -> 'Grouping':
        if not isinstance(child, Resource):
            raise TypeError(f"(Resource[{self.name}]) cannot nest: {child.__class__.__name__}")
        log.debug(f"(Resource[{self.name}]) nesting resource: {child.name}")
        nested = Resource((self.location / child.location))
        for name, endpoint in child.endpoints():
            original = str(endpoint.location).removeprefix(str(child.location)).lstrip('/')
            setattr(nested, name, endpoint.mutate(location=Location(original)))
        return nested

    def __getattr__(self, name: str) -> t.Any:
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

def resource(location: Locatable = "") -> Resource: return Resource(location)
