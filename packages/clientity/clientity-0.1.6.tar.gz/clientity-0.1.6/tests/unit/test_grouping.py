# ~/clientity/tests/unit/test_grouping.py
from __future__ import annotations
import pytest

from clientity.core.endpoint import Endpoint, endpoint
from clientity.core.grouping import Resource, Namespace
from clientity.core.primitives import GET, POST, Location, Bound


class TestResource:
    def test_init_empty(self):
        r = Resource()
        assert str(r.location) == ""

    def test_init_with_location(self):
        r = Resource("api/v1")
        assert str(r.location) == "api/v1"

    def test_matmul_sets_location(self):
        r = Resource() @ "users"
        assert str(r.location) == "users"

    def test_name_from_location(self):
        r = Resource("api/v1/users")
        assert r.name == "ApiV1Users"

    def test_wrap_prepends_location(self):
        r = Resource("api/v1")
        ep = endpoint.get @ "users"
        wrapped = r.__wrap__(ep)
        assert str(wrapped.location) == "api/v1/users"

    def test_wrap_returns_endpoint(self):
        r = Resource("api")
        ep = endpoint.get @ "users"
        wrapped = r.__wrap__(ep)
        assert isinstance(wrapped, Endpoint)

    def test_setattr_wraps_endpoint(self):
        r = Resource("api")
        r.users = endpoint.get @ "users"
        assert str(r.users.location) == "api/users"

    def test_nest_resource(self):
        parent = Resource("api")
        child = Resource("v1")
        child.users = endpoint.get @ "users"

        parent.v1 = child
        assert str(parent.v1.location) == "api/v1"
        assert str(parent.v1.users.location) == "api/v1/users"

    def test_endpoints_iterator(self):
        r = Resource("api")
        r.users = endpoint.get @ "users"
        r.posts = endpoint.get @ "posts"

        eps = list(r.endpoints())
        names = [name for name, _ in eps]
        assert "users" in names
        assert "posts" in names
        assert len(eps) == 2


class TestNamespace:
    def test_init_empty(self):
        ns = Namespace()
        assert ns.base == ""
        assert ns.interface is None

    def test_init_with_base(self):
        ns = Namespace("https://api.example.com")
        assert ns.base == "https://api.example.com"

    def test_matmul_sets_base(self):
        ns = Namespace() @ "https://api.example.com"
        assert ns.base == "https://api.example.com"

    def test_strips_trailing_slash(self):
        ns = Namespace("https://api.example.com/")
        assert ns.base == "https://api.example.com"

    def test_independent_with_interface(self):
        import httpx
        ns = Namespace("https://api.example.com", interface=httpx.AsyncClient())
        assert ns.independent is True
        assert ns.adapter is not None

    def test_dependent_without_interface(self):
        ns = Namespace("https://api.example.com")
        assert ns.independent is False
        assert ns.adapter is None

    def test_wrap_passthrough_when_dependent(self):
        ns = Namespace("https://api.example.com")
        ep = endpoint.get @ "users"
        wrapped = ns.__wrap__(ep)
        # Should return endpoint unchanged (not Bound)
        assert isinstance(wrapped, Endpoint)

    def test_wrap_returns_bound_when_independent(self):
        import httpx
        ns = Namespace("https://api.example.com", interface=httpx.AsyncClient())
        ep = endpoint.get @ "users"
        wrapped = ns.__wrap__(ep)
        assert isinstance(wrapped, Bound)

    def test_setattr_wraps_endpoint(self):
        import httpx
        ns = Namespace("https://api.example.com", interface=httpx.AsyncClient())
        ns.users = endpoint.get @ "users"
        assert isinstance(ns.users, Bound)

    def test_endpoints_iterator(self):
        ns = Namespace("https://api.example.com")
        ns.users = endpoint.get @ "users"
        ns.posts = endpoint.get @ "posts"

        eps = list(ns.endpoints())
        names = [name for name, _ in eps]
        assert "users" in names
        assert "posts" in names
