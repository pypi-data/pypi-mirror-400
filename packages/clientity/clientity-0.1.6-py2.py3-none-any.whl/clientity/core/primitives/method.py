# ~/clientity/src/clientity/core/primitives/method.py
from __future__ import annotations
import typing as t

from clientity.logs import log

MethodType = t.Literal[
    'GET', 'PUT',
    'HEAD', 'POST',
    'PATCH', 'DELETE',
    'OPTIONS'
]

GET: MethodType = "GET"
PUT: MethodType = "PUT"
HEAD: MethodType = "HEAD"
POST: MethodType = "POST"
PATCH: MethodType = "PATCH"
DELETE: MethodType = "DELETE"
OPTIONS: MethodType = "OPTIONS"

Methods: list[MethodType] = [
    GET, PUT, HEAD, POST,
    PATCH, DELETE, OPTIONS
]
