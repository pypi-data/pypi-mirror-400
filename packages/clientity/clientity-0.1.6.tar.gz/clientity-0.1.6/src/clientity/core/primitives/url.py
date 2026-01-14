# ~/clientity/src/clientity/core/primitives/url.py
from __future__ import annotations
import re, typing as t

from clientity.logs import log
from clientity.core.hints import Stringable

Locatable = t.Union[str, 'Location']

class Location(str):
    """
    A path fragment, possibly with parameters.

    Examples:
        Location("login")
        Location("users") / "{id}" / "posts"
        Location("api/v1") / "search"
    """
    PARAMEX: t.ClassVar[re.Pattern] = re.compile(r"\{(\w+)\}")
    parameters: list[str]

    def __new__(cls, path: Locatable = "") -> 'Location':
        if isinstance(path, Location): return path
        instance = str.__new__(cls, path.strip("/"))
        instance.parameters = cls.PARAMEX.findall(instance)
        log.debug(f"(Location.__new__) parsed {len(instance.parameters)} parameters from location path: {path}")
        return instance

    @property
    def name(self) -> str:
        param = lambda v: v.startswith('{') and v.endswith('}')
        parts = [
            p.title() for p in
            self.split('/')
            if not param(p)
        ]
        return ''.join(parts)


    @property
    def ready(self) -> bool:
        return (len(self.parameters) == 0)

    def resolve(self, **params: Stringable) -> str:
        log.debug(f"(location.resolve) resolving [{self}] with: {params}")
        result = str.__str__(self)
        for k, v in params.items():
            result = result.replace(f"{{{k}}}", str(v))
        log.debug(f"(location.resolve) resolved: {result}")
        return result


    def __truediv__(self, other: Locatable) -> 'Location':
        log.debug(f"(location.__truediv__) joining self [{self}] with: {other}")
        _other = str(other).strip("/")
        if not self:
            location = Location(_other)
            log.debug(f"(location.__truediv__) joined -> {location}")
            return location
        if not _other:
            location = Location(self)
            log.debug(f"(location.__truediv__) joined -> {location}")
            return location

        location = Location(f"{self}/{_other}")
        log.debug(f"(location.__truediv__) joined -> {location}")
        return location


class URL(str):
    base: str
    location: Location

    def __new__(
        cls,
        base: str,
        location: Locatable = ""
        ) -> 'URL':
        loc = Location(location)
        instance = str.__new__(cls, "")
        instance.base = base.rstrip("/")
        instance.location = loc
        return instance

    @property
    def ready(self) -> bool:
        return self.location.ready

    @property
    def parameters(self) -> list[str]:
        return self.location.parameters

    def resolve(self, **params: str) -> str:
        if (loc:=self.location.resolve(**params)):
            return f"{self.base}/{loc}"
        return self.base

    def __truediv__(self, location: Locatable) -> 'URL':
        loc = self.location / location
        url = URL(self.base, loc)
        return url


URI = t.Union[Location, URL]
