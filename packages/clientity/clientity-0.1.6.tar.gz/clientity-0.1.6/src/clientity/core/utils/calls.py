# ~/clientity/src/clientity/core/utils/calls.py
from __future__ import annotations
import inspect, typing as t, asyncio as aio
from concurrent.futures import ThreadPoolExecutor

from clientity.logs import log
from clientity.core.hints import (
    Call, Callable,
    Synced, Asynced,
    Requesting,
)
from clientity.core.utils.models import constructors
if t.TYPE_CHECKING:
    from clientity.core.primitives import Location, Instructions


class __synced:
    def check(self, call: Call) -> bool:
        return (not inspect.iscoroutinefunction(call))

    def wrap(self, call: Callable.Async) -> Callable.Sync:
        cocast = lambda c: t.cast(t.Coroutine, c)
        def wrapper(*args, **kwargs):
            coro = call(*args, **kwargs)
            try:
                loop = aio.get_running_loop()
            except RuntimeError:
                return aio.run(cocast(coro))

            with ThreadPoolExecutor() as pool:
                future = pool.submit(aio.run, cocast(coro))
                return future.result()
        return wrapper

    def eval(self, call: Call, *args, **kwargs) -> t.Any:
        if self.check(call):
            return call(*args, **kwargs)
        sync = self.wrap(call)
        return sync(*args, **kwargs)

    @t.overload
    def __call__(self, call: Call, eval: t.Literal[False] = ..., *args, **kwargs) -> Callable.Sync: ...
    @t.overload
    def __call__(self, call: Call, eval: t.Literal[True], *args, **kwargs) -> t.Any: ...
    def __call__(
        self,
        call: Call,
        eval: bool = False,
        *args, **kwargs
        ) -> Synced:
        needs = not self.check(call)
        match (needs, eval):
            case (True, True):
                sync = self.wrap(call)
                return sync(*args, **kwargs)
            case (False, True):
                return call(*args, **kwargs)
            case (False, False):
                return call
            case (True, False):
                return self.wrap(call)

synced = __synced()

class __asynced:
    def check(self, call: Call) -> bool:
        return inspect.iscoroutinefunction(call)

    def wrap(self, call: Callable.Sync) -> Callable.Async:
        async def wrapper(*args, **kwargs):
            return await aio.to_thread(call, *args, **kwargs)
        return wrapper

    async def eval(self, call: Call, *args, **kwargs) -> t.Any:
        if self.check(call):
            return await call(*args, **kwargs)
        wrapped = self.wrap(call)
        return await wrapped(*args, **kwargs)

    def __call__(self, call: Call, ) -> Callable.Async:
        if self.check(call):
            return call
        return self.wrap(call)
asynced = __asynced()


class __sift:
    def __call__(
        self,
        *args,
        location: t.Optional['Location'] = None,
        querying: Requesting = None,
        requesting: Requesting = None,
        exhaust: bool = False,
        **kwargs
        ) -> tuple[dict, dict, dict]: # path, query, body
        log.debug(f"(sift.__call__) sifting [exhaust: {exhaust}]: [location: {location}] [querying: {querying}] [requesting: {requesting}]")
        pf = set(location.parameters) if location else set() # path fields
        qf = set(constructors(querying).keys()) if querying else set() # query fields
        bf = set(constructors(requesting).keys()) if requesting else set() # body fields
        log.debug(f"(sift.__call__) received args: {args}")
        log.debug(f"(sift.__call__) received kwargs: {kwargs}")

        available = set(kwargs.keys())

        path = {}
        if pf:
            pparams = list(location.parameters) if location else []
            for i, arg in enumerate(args):
                if (i < len(pparams)):
                    path[pparams[i]] = arg

            pk = (available & pf)
            for k in pk:
                path[k] = kwargs[k]
            log.info(f"(sift.__call__) sifted path: {path}")
            if exhaust:
                available -= pk
                log.debug(f"(sift.__call__) available after path: {available}")

        query = {}
        if qf:
            qk = (available & qf)
            for k in qk:
                query[k] = kwargs[k]
            log.info(f"(sift.__call__) sifted query: {query}")
            if exhaust:
                available -= qk
                log.debug(f"(sift.__call__) available after query: {available}")

        body = {}
        if bf:
            bk = (available & bf)
            for k in bk:
                body[k] = kwargs[k]
            log.info(f"(sift.__call__) sifted body: {body}")
            if exhaust:
                available -= bk
                log.debug(f"(sift.__call__) available after body: {available}")

        return (path, query, body)

    def instructions(
        self,
        *args,
        provided: 'Instructions',
        exhaust: bool = False,
        **kwargs
        ) -> tuple[dict, dict, dict]:
        return self.__call__(
            *args,
            location=provided.location,
            querying=provided.querying,
            requesting=provided.requesting,
            exhaust=exhaust,
            **kwargs
        )


sift = __sift()
