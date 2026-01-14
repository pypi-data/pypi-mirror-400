# tests/unit/test_respond.py
from __future__ import annotations
import pytest
from dataclasses import dataclass
from collections.abc import Sequence

from clientity.core.utils.http import respond
from clientity.exc.models import ModelingError
from clientity.exc.http import ResponseError


class MockResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class TestRespondSingle:
    def test_none_model_returns_none(self):
        result = respond(None, MockResponse({}))
        assert result is None

    def test_dict_to_model(self):
        @dataclass
        class User:
            id: int
            name: str

        result = respond(User, MockResponse({"id": 1, "name": "joel"}))
        assert isinstance(result, User)
        assert result.id == 1
        assert result.name == "joel"

    def test_respond_protocol(self):
        @dataclass
        class User:
            id: int
            name: str

            @classmethod
            def __respond__(cls, response) -> 'User':
                data = response.json()
                return cls(id=data["user_id"], name=data["user_name"])

        result = respond(User, MockResponse({"user_id": 1, "user_name": "joel"}))
        assert isinstance(result, User)
        assert result.id == 1
        assert result.name == "joel"


class TestRespondList:
    def test_list_of_models(self):
        @dataclass
        class Item:
            id: int

        result = respond(list[Item], MockResponse([{"id": 1}, {"id": 2}, {"id": 3}]))
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(item, Item) for item in result)
        assert result[0].id == 1
        assert result[2].id == 3

    def test_empty_list(self):
        @dataclass
        class Item:
            id: int

        result = respond(list[Item], MockResponse([]))
        assert isinstance(result, list)
        assert len(result) == 0


class TestRespondSet:
    def test_set_of_models(self):
        @dataclass(frozen=True)
        class Item:
            id: int

        result = respond(set[Item], MockResponse([{"id": 1}, {"id": 2}]))
        assert isinstance(result, set)
        assert len(result) == 2

    def test_frozenset_of_models(self):
        @dataclass(frozen=True)
        class Item:
            id: int

        result = respond(frozenset[Item], MockResponse([{"id": 1}, {"id": 2}]))
        assert isinstance(result, frozenset)
        assert len(result) == 2


class TestRespondTuple:
    def test_tuple_of_models(self):
        @dataclass
        class Item:
            id: int

        result = respond(tuple[Item, ...], MockResponse([{"id": 1}, {"id": 2}]))
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0].id == 1


class TestRespondSequence:
    def test_sequence_of_models(self):
        @dataclass
        class Item:
            id: int

        result = respond(Sequence[Item], MockResponse([{"id": 1}, {"id": 2}]))
        assert isinstance(result, list)
        assert len(result) == 2


class TestRespondAll:
    def test_respondall_protocol(self):
        @dataclass
        class Item:
            id: int

            @classmethod
            def __respondall__(cls, response) -> list['Item']:
                data = response.json()
                return [cls(id=d["id"] * 10) for d in data["items"]]

        result = respond(list[Item], MockResponse({"items": [{"id": 1}, {"id": 2}]}))
        assert len(result) == 2
        assert result[0].id == 10
        assert result[1].id == 20

    def test_respondall_with_nested_response(self):
        @dataclass
        class User:
            id: int
            name: str

            @classmethod
            def __respondall__(cls, response) -> list['User']:
                data = response.json()
                return [cls(**u) for u in data["data"]["users"]]

        result = respond(list[User], MockResponse({
            "data": {"users": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]},
            "meta": {"total": 2}
        }))
        assert len(result) == 2
        assert result[0].name == "a"


class TestRespondItemWithRespond:
    def test_item_respond_protocol(self):
        @dataclass
        class Item:
            id: int
            doubled: int

            @classmethod
            def __respond__(cls, data) -> 'Item':
                return cls(id=data["id"], doubled=data["id"] * 2)

        result = respond(list[Item], MockResponse([{"id": 1}, {"id": 2}]))
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].doubled == 2
        assert result[1].doubled == 4


class TestRespondErrors:
    def test_non_iterable_response_for_list(self):
        @dataclass
        class Item:
            id: int

        with pytest.raises(ResponseError):
            respond(list[Item], MockResponse({"id": 1}))

    def test_no_json_method(self):
        @dataclass
        class Item:
            id: int

        class BadResponse:
            pass

        with pytest.raises(ResponseError):
            respond(list[Item], BadResponse())

    def test_model_instantiation_failure(self):
        @dataclass
        class Item:
            id: int
            required_field: str

        with pytest.raises(ModelingError):
            respond(Item, MockResponse({"id": 1}))
