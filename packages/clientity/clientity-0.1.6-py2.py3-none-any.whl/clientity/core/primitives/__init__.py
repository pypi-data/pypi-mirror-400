# ~/clientity/src/clientity/core/primitives/__init__.py
from .url import (
    URL, Location, Locatable
)
from .bound import (
    Bound
)
from .method import (
    MethodType, Methods,
    GET, PUT, POST, HEAD,
    PATCH, DELETE, OPTIONS
)
from .instructions import (
    Hooks, Instructions
)
