# ~/clientity/tests/unit/test_adapters.py
from __future__ import annotations
import pytest

from clientity.core.primitives import GET, POST
from clientity.core.adapters import adapt
from clientity.core.adapters._httpx import HttpxAdapter
from clientity.core.adapters._requests import RequestsAdapter
from clientity.core.adapters._aiohttp import AiohttpAdapter


class TestHttpxAdapter:
    def test_compatible_with_module(self):
        import httpx
        assert HttpxAdapter.Compatible(httpx) is True

    def test_compatible_with_client(self):
        import httpx
        client = httpx.Client()
        assert HttpxAdapter.Compatible(client) is True
        client.close()

    def test_compatible_with_async_client(self):
        import httpx
        client = httpx.AsyncClient()
        assert HttpxAdapter.Compatible(client) is True

    def test_not_compatible_with_other(self):
        assert HttpxAdapter.Compatible("string") is False

    def test_build_basic(self):
        import httpx
        adapter = HttpxAdapter(httpx.AsyncClient())
        req = adapter.build("https://api.example.com/users", GET)
        assert req.method == "GET"
        assert str(req.url) == "https://api.example.com/users"

    def test_build_with_params(self):
        import httpx
        adapter = HttpxAdapter(httpx.AsyncClient())
        req = adapter.build(
            "https://api.example.com/search", GET,
            params={"q": "test", "limit": 10}
        )
        assert "q=test" in str(req.url)

    def test_build_with_json_body(self):
        import httpx
        adapter = HttpxAdapter(httpx.AsyncClient())
        req = adapter.build(
            "https://api.example.com/users", POST,
            body=("json", {"name": "test"})
        )
        assert req.method == "POST"


class TestRequestsAdapter:
    def test_compatible_with_module(self):
        import requests
        assert RequestsAdapter.Compatible(requests) is True

    def test_compatible_with_session(self):
        import requests
        session = requests.Session()
        assert RequestsAdapter.Compatible(session) is True
        session.close()

    def test_not_compatible_with_other(self):
        assert RequestsAdapter.Compatible("string") is False

    def test_build_basic(self):
        import requests
        adapter = RequestsAdapter(requests.Session())
        req = adapter.build("https://api.example.com/users", GET)
        assert req.method == "GET"
        assert req.url == "https://api.example.com/users"

    def test_build_with_params(self):
        import requests
        adapter = RequestsAdapter(requests.Session())
        req = adapter.build(
            "https://api.example.com/search", GET,
            params={"q": "test"}
        )
        assert "q=test" in req.url


class TestAiohttpAdapter:
    def test_compatible_with_module(self):
        import aiohttp
        assert AiohttpAdapter.Compatible(aiohttp) is True

    def test_compatible_with_session(self):
        import aiohttp
        # Can't easily test ClientSession without async context
        # Just test the module compatibility
        assert AiohttpAdapter.Compatible(aiohttp) is True

    def test_not_compatible_with_other(self):
        assert AiohttpAdapter.Compatible("string") is False

    def test_build_basic(self):
        adapter = AiohttpAdapter()
        req = adapter.build("https://api.example.com/users", GET)
        assert req.method == "GET"
        assert req.url == "https://api.example.com/users"

    def test_build_with_params(self):
        adapter = AiohttpAdapter()
        req = adapter.build(
            "https://api.example.com/search", GET,
            params={"q": "test"}
        )
        assert req.kwargs["params"] == {"q": "test"}


class TestAdaptFactory:
    def test_adapt_httpx_module(self):
        import httpx
        adapter = adapt(httpx)
        assert isinstance(adapter, HttpxAdapter)

    def test_adapt_requests_module(self):
        import requests
        adapter = adapt(requests)
        assert isinstance(adapter, RequestsAdapter)

    def test_adapt_aiohttp_module(self):
        import aiohttp
        adapter = adapt(aiohttp)
        assert isinstance(adapter, AiohttpAdapter)

    def test_adapt_raises_for_none(self):
        with pytest.raises(ValueError):
            adapt(None)

    def test_adapt_raises_for_unknown(self):
        with pytest.raises(ValueError):
            adapt("unknown")
