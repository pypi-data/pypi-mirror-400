# ~/clientity/tests/unit/test_endpoint.py
from __future__ import annotations
import pytest

from clientity.core.endpoint import Endpoint, endpoint
from clientity.core.primitives import (
    GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS,
    Location, Instructions
)


class TestEndpointFactory:
    def test_get(self):
        ep = endpoint.get
        assert ep.method == GET

    def test_post(self):
        ep = endpoint.post
        assert ep.method == POST

    def test_put(self):
        ep = endpoint.put
        assert ep.method == PUT

    def test_patch(self):
        ep = endpoint.patch
        assert ep.method == PATCH

    def test_delete(self):
        ep = endpoint.delete
        assert ep.method == DELETE

    def test_head(self):
        ep = endpoint.head
        assert ep.method == HEAD

    def test_options(self):
        ep = endpoint.options
        assert ep.method == OPTIONS


class TestEndpointBuilder:
    def test_at_sets_location(self):
        ep = Endpoint(GET).at("users/{id}")
        assert str(ep.location) == "users/{id}"

    def test_at_returns_new_instance(self):
        ep1 = Endpoint(GET)
        ep2 = ep1.at("users")
        assert ep1 is not ep2

    def test_prehook_adds_hook(self):
        def hook(x): return x
        ep = Endpoint(GET).prehook(hook)
        assert len(ep.hooks.pre) == 1

    def test_prehook_returns_new_instance(self):
        def hook(x): return x
        ep1 = Endpoint(GET)
        ep2 = ep1.prehook(hook)
        assert ep1 is not ep2
        assert len(ep1.hooks.pre) == 0

    def test_posthook_adds_hook(self):
        def hook(x): return x
        ep = Endpoint(GET).posthook(hook)
        assert len(ep.hooks.post) == 1

    def test_queries_sets_model(self):
        class QueryModel: pass
        ep = Endpoint(GET).queries(QueryModel)
        assert ep.querying is QueryModel

    def test_requests_sets_model(self):
        class BodyModel: pass
        ep = Endpoint(POST).requests(BodyModel)
        assert ep.requesting is BodyModel

    def test_responds_sets_model(self):
        class ResponseModel: pass
        ep = Endpoint(GET).responds(ResponseModel)
        assert ep.responding is ResponseModel

    def test_mutate_returns_new_instance(self):
        ep1 = Endpoint(GET, "users")
        ep2 = ep1.mutate(method=POST)
        assert ep1 is not ep2
        assert ep1.method == GET
        assert ep2.method == POST

    def test_instructions_returns_instructions(self):
        ep = Endpoint(GET, "users/{id}")
        inst = ep.instructions()
        assert isinstance(inst, Instructions)
        assert inst.method == GET
        assert str(inst.location) == "users/{id}"

    def test_call_returns_instructions(self):
        ep = Endpoint(GET, "users")
        inst = ep()
        assert isinstance(inst, Instructions)

    def test_name_from_location(self):
        ep = Endpoint(GET, "users/{id}/posts")
        assert ep.name == "UsersPosts"


class TestEndpointOperators:
    def test_matmul_location(self):
        ep = endpoint.get @ "users/{id}"
        assert str(ep.location) == "users/{id}"

    def test_xor_query_model(self):
        class QueryModel: pass
        ep = endpoint.get @ "search" % QueryModel
        assert ep.querying is QueryModel

    def test_lshift_body_model(self):
        class BodyModel: pass
        ep = endpoint.post @ "users" << BodyModel
        assert ep.requesting is BodyModel

    def test_rshift_response_model(self):
        class ResponseModel: pass
        ep = endpoint.get @ "users" >> ResponseModel
        assert ep.responding is ResponseModel

    def test_le_prehook(self):
        def hook(x): return x
        ep = endpoint.get @ "users" & hook
        assert len(ep.hooks.pre) == 1

    def test_ge_posthook(self):
        def hook(x): return x
        ep = endpoint.get @ "users" | hook
        assert len(ep.hooks.post) == 1

    def test_chained_operators(self):
        class Query: pass
        class Body: pass
        class Response: pass
        def pre(x): return x
        def post(x): return x

        ep = endpoint.post @ "users/{id}" % Query << Body >> Response & pre | post

        assert str(ep.location) == "users/{id}"
        assert ep.querying is Query
        assert ep.requesting is Body
        assert ep.responding is Response
        assert len(ep.hooks.pre) == 1
        assert len(ep.hooks.post) == 1
