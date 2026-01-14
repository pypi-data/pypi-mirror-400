from .utils import (
    asynced, embody
)
from .client import client
from .endpoint import endpoint
from .grouping import resource, namespace

from .protocols import (
    Requestable, Responsive,
    Interface, Interfacing,
    Interfaceable
)

from .primitives import (
    URL, MethodType, Methods,
    GET, PUT, POST, HEAD,
    PATCH, DELETE, OPTIONS,
    Hooks, Instructions
)
