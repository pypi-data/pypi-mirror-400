# tests/integration/test_client.py
from __future__ import annotations
import typing as t
import pytest
from dataclasses import dataclass

from clientity.core.client import Client
from clientity.core.endpoint import endpoint
from clientity.core.grouping import Resource, Namespace
from clientity.core.primitives import Bound

# import mock fixtures from conftest
pytestmark = pytest.mark.asyncio


# --- Models for testing ---

@dataclass
class UserQuery:
    search: str
    limit: int = 10


@dataclass
class CreateUser:
    name: str
    email: str


@dataclass
class User:
    id: int
    name: str
    email: str

    @classmethod
    def __respond__(cls, response) -> 'User':
        data = response.json()
        return cls(**data)


# --- Client + Endpoint ---

class TestClientEndpoint:
    def test_endpoint_assignment_wraps_to_bound(self, mock_adapter):
        client = Client(mock_adapter, base="https://api.example.com")
        client.users = endpoint.get @ "users"
        assert isinstance(client.users, Bound)

    async def test_simple_get(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"status": "ok"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")
        client.status = endpoint.get @ "status"

        response = await client.status()

        assert mock_adapter.last_request["url"] == "https://api.example.com/status"
        assert mock_adapter.last_request["method"] == "GET"

    async def test_get_with_path_params(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"id": 123, "name": "joel"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")
        client.user = endpoint.get @ "users/{id}"

        response = await client.user(id=123)

        assert mock_adapter.last_request["url"] == "https://api.example.com/users/123"

    async def test_get_with_path_params_positional(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"id": 123}, 200)
        client = Client(mock_adapter, base="https://api.example.com")
        client.user = endpoint.get @ "users/{id}"

        response = await client.user(123)

        assert mock_adapter.last_request["url"] == "https://api.example.com/users/123"

    async def test_get_with_query_model(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"users": []}, 200)
        client = Client(mock_adapter, base="https://api.example.com")
        client.search = endpoint.get @ "users/search" % UserQuery

        response = await client.search(search="joel", limit=5)

        assert mock_adapter.last_request["url"] == "https://api.example.com/users/search"
        assert mock_adapter.last_request["params"] == {"search": "joel", "limit": 5}

    async def test_post_with_body_model(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"id": 1, "name": "joel", "email": "j@x.com"}, 201)
        client = Client(mock_adapter, base="https://api.example.com")
        client.create_user = endpoint.post @ "users" << CreateUser

        response = await client.create_user(name="joel", email="j@x.com")

        assert mock_adapter.last_request["method"] == "POST"
        assert mock_adapter.last_request["body"] == ("json", {"name": "joel", "email": "j@x.com"})

    async def test_response_model(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"id": 1, "name": "joel", "email": "j@x.com"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")
        client.user = endpoint.get @ "users/{id}" >> User

        user = await client.user(id=1)

        assert isinstance(user, User)
        assert user.id == 1
        assert user.name == "joel"

    async def test_full_endpoint_chain(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"id": 1, "name": "joel", "email": "j@x.com"}, 201)
        client = Client(mock_adapter, base="https://api.example.com")
        client.create = endpoint.post @ "users" % UserQuery << CreateUser >> User

        user = await client.create(search="test", limit=1, name="joel", email="j@x.com")

        assert mock_adapter.last_request["params"] == {"search": "test", "limit": 1}
        assert mock_adapter.last_request["body"] == ("json", {"name": "joel", "email": "j@x.com"})
        assert isinstance(user, User)


# --- Client + Resource ---

class TestClientResource:
    def test_resource_assignment(self, mock_adapter):
        client = Client(mock_adapter, base="https://api.example.com")
        users = Resource("users")
        users.list = endpoint.get @ ""
        users.get = endpoint.get @ "{id}"

        client.users = users

        assert isinstance(client.users, Resource)
        assert isinstance(client.users.list, Bound)
        assert isinstance(client.users.get, Bound)

    async def test_resource_endpoint_execution(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"users": []}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        users = Resource("users")
        users.list = endpoint.get @ ""
        client.users = users

        response = await client.users.list()

        assert mock_adapter.last_request["url"] == "https://api.example.com/users"

    async def test_resource_endpoint_with_path_param(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"id": 123, "name": "joel", "email": "joel@test.com"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        users = Resource("users")
        users.get = endpoint.get @ "{id}" >> User
        print(f"endpoint responding: {users.get.responding}")
        client.users = users
        print(f"bound ref responding: {client.users.get.__ref__.responding}")
        user = await client.users.get(id=123)

        assert mock_adapter.last_request["url"] == "https://api.example.com/users/123"
        assert isinstance(user, User)

    async def test_nested_resource(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"posts": []}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        api = Resource("api")
        v1 = Resource("v1")
        v1.posts = endpoint.get @ "posts"
        api.v1 = v1
        client.api = api

        response = await client.api.v1.posts()

        assert mock_adapter.last_request["url"] == "https://api.example.com/api/v1/posts"


# --- Client + Namespace (dependent) ---

class TestClientNamespaceDependent:
    def test_dependent_namespace_assignment(self, mock_adapter):
        client = Client(mock_adapter, base="https://api.example.com")

        auth = Namespace(name="auth")
        auth.login = endpoint.post @ "auth/login"
        client.auth = auth

        assert isinstance(client.auth, Namespace)
        assert isinstance(client.auth.login, Bound)

    async def test_dependent_namespace_uses_client_adapter(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"token": "abc123"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        auth = Namespace(name="auth")
        auth.login = endpoint.post @ "auth/login" << CreateUser
        client.auth = auth

        response = await client.auth.login(name="joel", email="j@x.com")

        assert mock_adapter.last_request["url"] == "https://api.example.com/auth/login"
        assert mock_adapter.last_request["method"] == "POST"


# --- Client + Namespace (independent) ---

class TestClientNamespaceIndependent:
    def test_independent_namespace_keeps_own_adapter(self, mock_adapter):
        client = Client(mock_adapter, base="https://api.example.com")

        other_adapter = mock_adapter.__class__()
        search_ns = Namespace(base="https://search.example.com", interface=other_adapter)
        search_ns.query = endpoint.post @ "query"
        client.search = search_ns

        assert client.search.adapter is other_adapter
        assert client.search.adapter is not client.adapter

    async def test_independent_namespace_uses_own_base(self, mock_adapter, mock_response):
        client_adapter = mock_adapter.__class__()
        client = Client(client_adapter, base="https://api.example.com")

        search_adapter = mock_adapter.__class__()
        search_adapter.response = mock_response({"results": []}, 200)
        search_ns = Namespace(base="https://search.example.com", interface=search_adapter)
        search_ns.query = endpoint.post @ "query"
        client.search = search_ns

        response = await client.search.query()

        assert search_adapter.last_request["url"] == "https://search.example.com/query"
        assert client_adapter.last_request is None  # client adapter not used


# --- Hooks ---

class TestHooks:
    async def test_prehook(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"status": "ok"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        called = []
        def prehook(request):
            called.append("pre")
            return request

        client.status = endpoint.get @ "status" & prehook

        await client.status()

        assert called == ["pre"]

    async def test_posthook(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"status": "ok"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        called = []
        def posthook(response):
            called.append("post")
            return response

        client.status = endpoint.get @ "status" | posthook

        await client.status()

        assert called == ["post"]

    async def test_both_hooks(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"status": "ok"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        called = []
        def prehook(request):
            called.append("pre")
            return request
        def posthook(response):
            called.append("post")
            return response

        client.status = endpoint.get @ "status" & prehook | posthook

        await client.status()

        assert called == ["pre", "post"]

    async def test_hook_can_modify_request(self, mock_adapter, mock_response):
        mock_adapter.response = mock_response({"status": "ok"}, 200)
        client = Client(mock_adapter, base="https://api.example.com")

        def add_header(request):
            request["headers"] = {"X-Custom": "value"}
            return request

        client.status = endpoint.get @ "status" & add_header

        await client.status()

        assert mock_adapter.last_request["headers"] == {"X-Custom": "value"}
