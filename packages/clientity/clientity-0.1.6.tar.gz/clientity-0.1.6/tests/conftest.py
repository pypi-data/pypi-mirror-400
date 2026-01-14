# tests/conftest.py
from __future__ import annotations
import typing as t
import pytest

from clientity.core.adapters.base import Adapter
from clientity.core.hints import Embodied


class MockResponse:
    def __init__(self, data: dict, status: int = 200):
        self._data = data
        self.status = status
        self.status_code = status

    def json(self) -> dict:
        return self._data


class MockAdapter(Adapter[dict]):
    """Mock adapter that acts as both interface and adapter."""

    def __init__(self):
        self.last_request: t.Optional[dict] = None
        self.response: MockResponse = MockResponse({})

    def build(
        self,
        url: str,
        method: str,
        params: t.Optional[dict] = None,
        body: t.Optional[Embodied] = None
    ) -> dict:
        req = {"url": url, "method": method, "params": params, "body": body}
        self.last_request = req
        return req

    async def send(self, request: dict) -> MockResponse:
        return self.response

    @classmethod
    def Compatible(cls, interface: t.Any) -> bool:
        return isinstance(interface, MockAdapter)


@pytest.fixture(autouse=True)
def register_mock_adapter(monkeypatch):
    """Register MockAdapter with the adapt() function."""
    import clientity.core.adapters as adapters_module

    original_adapt = adapters_module.adapt

    def patched_adapt(interface: t.Any) -> Adapter:
        if isinstance(interface, MockAdapter):
            return interface
        return original_adapt(interface)

    # Patch in all places that import adapt
    monkeypatch.setattr(adapters_module, 'adapt', patched_adapt)
    monkeypatch.setattr('clientity.core.client.adapt', patched_adapt)
    monkeypatch.setattr('clientity.core.grouping.namespace.adapt', patched_adapt)


@pytest.fixture
def mock_adapter() -> MockAdapter:
    return MockAdapter()


@pytest.fixture
def mock_response() -> t.Callable[[dict, int], MockResponse]:
    def factory(data: dict, status: int = 200) -> MockResponse:
        return MockResponse(data, status)
    return factory
