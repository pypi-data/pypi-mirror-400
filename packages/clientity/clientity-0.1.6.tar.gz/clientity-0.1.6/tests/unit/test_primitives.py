# ~/clientity/tests/unit/test_primitives.py
from __future__ import annotations
import pytest

from clientity.core.primitives import (
    Location, URL, Instructions, Hooks,
    GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
)


class TestLocation:
    def test_basic_path(self):
        loc = Location("users")
        assert str(loc) == "users"
        assert loc.parameters == []

    def test_strips_slashes(self):
        loc = Location("/users/")
        assert str(loc) == "users"

    def test_single_parameter(self):
        loc = Location("users/{id}")
        assert loc.parameters == ["id"]

    def test_multiple_parameters(self):
        loc = Location("users/{user_id}/posts/{post_id}")
        assert loc.parameters == ["user_id", "post_id"]

    def test_ready_without_params(self):
        loc = Location("users")
        assert loc.ready is True

    def test_ready_with_params(self):
        loc = Location("users/{id}")
        assert loc.ready is False

    def test_resolve_single(self):
        loc = Location("users/{id}")
        assert loc.resolve(id=123) == "users/123"

    def test_resolve_multiple(self):
        loc = Location("users/{user_id}/posts/{post_id}")
        assert loc.resolve(user_id=1, post_id=42) == "users/1/posts/42"

    def test_join_with_truediv(self):
        loc = Location("api") / "v1" / "users"
        assert str(loc) == "api/v1/users"

    def test_join_empty_left(self):
        loc = Location("") / "users"
        assert str(loc) == "users"

    def test_join_empty_right(self):
        loc = Location("users") / ""
        assert str(loc) == "users"

    def test_join_preserves_parameters(self):
        loc = Location("users") / "{id}" / "posts"
        assert loc.parameters == ["id"]

    def test_idempotent(self):
        loc1 = Location("users")
        loc2 = Location(loc1)
        assert loc1 is loc2

    def test_name_simple(self):
        loc = Location("users")
        assert loc.name == "Users"

    def test_name_multi_segment(self):
        loc = Location("api/v1/users")
        assert loc.name == "ApiV1Users"

    def test_name_excludes_params(self):
        loc = Location("users/{id}/posts")
        assert loc.name == "UsersPosts"


class TestURL:
    def test_basic(self):
        url = URL("https://api.example.com", "users")
        assert url.base == "https://api.example.com"
        assert str(url.location) == "users"

    def test_strips_trailing_slash(self):
        url = URL("https://api.example.com/", "users")
        assert url.base == "https://api.example.com"

    def test_resolve_no_params(self):
        url = URL("https://api.example.com", "users")
        assert url.resolve() == "https://api.example.com/users"

    def test_resolve_with_params(self):
        url = URL("https://api.example.com", "users/{id}")
        assert url.resolve(id=123) == "https://api.example.com/users/123"

    def test_resolve_empty_location(self):
        url = URL("https://api.example.com", "")
        assert url.resolve() == "https://api.example.com"

    def test_parameters_passthrough(self):
        url = URL("https://api.example.com", "users/{id}/posts/{post_id}")
        assert url.parameters == ["id", "post_id"]

    def test_ready_passthrough(self):
        url = URL("https://api.example.com", "users/{id}")
        assert url.ready is False

    def test_truediv_extends_location(self):
        url = URL("https://api.example.com", "api") / "v1" / "users"
        assert url.resolve() == "https://api.example.com/api/v1/users"


class TestHooks:
    def test_empty_defaults(self):
        hooks = Hooks()
        assert hooks.pre == []
        assert hooks.post == []

    def test_pre_hooks(self):
        def hook1(x): return x
        def hook2(x): return x
        hooks = Hooks(pre=[hook1, hook2])
        assert len(hooks.pre) == 2

    def test_post_hooks(self):
        def hook1(x): return x
        hooks = Hooks(post=[hook1])
        assert len(hooks.post) == 1

    def test_before_returns_async(self):
        def sync_hook(x): return x
        hooks = Hooks(pre=[sync_hook])
        assert len(hooks.before) == 1
        # should be wrapped as async
        import inspect
        assert inspect.iscoroutinefunction(hooks.before[0])

    def test_after_returns_async(self):
        def sync_hook(x): return x
        hooks = Hooks(post=[sync_hook])
        assert len(hooks.after) == 1
        import inspect
        assert inspect.iscoroutinefunction(hooks.after[0])


class TestInstructions:
    def test_basic_construction(self):
        inst = Instructions(GET, "users")
        assert inst.method == GET
        assert str(inst.location) == "users"

    def test_default_hooks(self):
        inst = Instructions(GET, "users")
        assert inst.hooks.pre == []
        assert inst.hooks.post == []

    def test_default_models(self):
        inst = Instructions(GET, "users")
        assert inst.querying is None
        assert inst.requesting is None
        assert inst.responding is None

    def test_prehook_adds(self):
        inst = Instructions(GET, "users")
        def hook(x): return x
        inst.prehook(hook)
        assert len(inst.hooks.pre) == 1

    def test_posthook_adds(self):
        inst = Instructions(GET, "users")
        def hook(x): return x
        inst.posthook(hook)
        assert len(inst.hooks.post) == 1

    def test_merge_updates_method(self):
        inst = Instructions(GET, "users")
        merged = inst.merge(method=POST)
        assert merged.method == POST
        assert inst.method == GET  # original unchanged

    def test_merge_updates_location(self):
        inst = Instructions(GET, "users")
        merged = inst.merge(location=Location("posts"))
        assert str(merged.location) == "posts"

    def test_prepend_location(self):
        inst = Instructions(GET, "users/{id}")
        prepended = inst.prepend("api/v1")
        assert str(prepended.location) == "api/v1/users/{id}"


class TestMethodConstants:
    def test_get(self):
        assert GET == "GET"

    def test_post(self):
        assert POST == "POST"

    def test_put(self):
        assert PUT == "PUT"

    def test_patch(self):
        assert PATCH == "PATCH"

    def test_delete(self):
        assert DELETE == "DELETE"

    def test_head(self):
        assert HEAD == "HEAD"

    def test_options(self):
        assert OPTIONS == "OPTIONS"
