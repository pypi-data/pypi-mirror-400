# ~/clientity/tests/unit/test_utils.py
from __future__ import annotations
import pytest
import asyncio
from dataclasses import dataclass

from clientity.core.utils import asynced, synced, sift, dictate, embody
from clientity.core.utils.http import respond
from clientity.core.primitives import Location, Instructions, GET
from clientity.core.protocols import Requestable, Responsive


class TestAsynced:
    def test_sync_to_async(self):
        def sync_fn(x): return x * 2
        async_fn = asynced(sync_fn)
        result = asyncio.run(async_fn(5))
        assert result == 10

    def test_async_passthrough(self):
        async def async_fn(x): return x * 2
        wrapped = asynced(async_fn)
        assert wrapped is async_fn

    def test_check_identifies_sync(self):
        def sync_fn(): pass
        assert asynced.check(sync_fn) is False

    def test_check_identifies_async(self):
        async def async_fn(): pass
        assert asynced.check(async_fn) is True


class TestSynced:
    def test_async_to_sync(self):
        async def async_fn(x): return x * 2
        sync_fn = synced(async_fn)
        result = sync_fn(5)
        assert result == 10

    def test_sync_passthrough(self):
        def sync_fn(x): return x * 2
        wrapped = synced(sync_fn)
        assert wrapped is sync_fn

    def test_eval_mode_async(self):
        async def async_fn(x): return x * 2
        result = synced(async_fn, eval=True, x=5)
        assert result == 10

    def test_eval_mode_sync(self):
        def sync_fn(x): return x * 2
        result = synced(sync_fn, eval=True, x=5)
        assert result == 10


class TestSift:
    def test_path_params_from_kwargs(self):
        loc = Location("users/{id}")
        path, query, body = sift(location=loc, id=123)
        assert path == {"id": 123}

    def test_path_params_from_args(self):
        loc = Location("users/{id}")
        path, query, body = sift(123, location=loc)
        assert path == {"id": 123}

    def test_query_params(self):
        @dataclass
        class Query:
            search: str
            limit: int

        path, query, body = sift(querying=Query, search="foo", limit=10)
        assert query == {"search": "foo", "limit": 10}

    def test_body_params(self):
        @dataclass
        class Body:
            name: str
            email: str

        path, query, body = sift(requesting=Body, name="joel", email="j@x.com")
        assert body == {"name": "joel", "email": "j@x.com"}

    def test_mixed_params(self):
        @dataclass
        class Query:
            search: str

        @dataclass
        class Body:
            name: str

        loc = Location("users/{id}")
        path, query, body = sift(
            location=loc, querying=Query, requesting=Body,
            id=123, search="foo", name="joel"
        )
        assert path == {"id": 123}
        assert query == {"search": "foo"}
        assert body == {"name": "joel"}

    def test_instructions_convenience(self):
        @dataclass
        class Query:
            q: str

        inst = Instructions(GET, "search", querying=Query)
        path, query, body = sift.instructions(provided=inst, q="test")
        assert query == {"q": "test"}


class TestDictate:
    def test_dict_passthrough(self):
        d = {"a": 1}
        assert dictate(d) == {"a": 1}

    def test_dataclass(self):
        @dataclass
        class Model:
            name: str
            value: int

        obj = Model(name="test", value=42)
        result = dictate(obj)
        assert result == {"name": "test", "value": 42}

    def test_none_returns_empty(self):
        assert dictate(None) == {}

    def test_object_with_dict_attr(self):
        class Model:
            def __init__(self):
                self.name = "test"
                self.value = 42

        obj = Model()
        result = dictate(obj)
        assert result["name"] == "test"
        assert result["value"] == 42


class TestEmbody:
    def test_none_returns_none(self):
        assert embody(None) is None

    def test_dict_returns_json(self):
        result = embody({"name": "test"})
        assert result == ("json", {"name": "test"})

    def test_bytes_returns_data(self):
        result = embody(b"raw bytes")
        assert result == ("data", b"raw bytes")

    def test_requestable_protocol(self):
        class Model:
            RequestKey = "json"
            def __request__(self):
                return {"encoded": True}

        result = embody(Model())
        assert result == ("json", {"encoded": True})


class TestRespond:
    def test_none_model_returns_none(self):
        result = respond(None, object())
        assert result is None

    def test_responsive_protocol(self):
        class Response:
            def json(self):
                return {"id": 1}

        class Model:
            def __init__(self, id: int):
                self.id = id

            @classmethod
            def __respond__(cls, response):
                return cls(**response.json())

        result = respond(Model, Response())
        assert result.id == 1

    def test_json_fallback(self):
        class Response:
            def json(self):
                return {"id": 1, "name": "test"}

        @dataclass
        class Model:
            id: int
            name: str

        result = respond(Model, Response())
        assert result.id == 1
        assert result.name == "test"
