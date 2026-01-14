# ~/clientity/src/clientity/core/protocols/located.py
from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from clientity.core.primitives.url import Location

@t.runtime_checkable
class Located(t.Protocol):
    location: 'Location'
