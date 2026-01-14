# ~/clientity/src/clientity/core/utils/http.py
from __future__ import annotations
import typing as t

from urllib.parse import urlparse

from clientity.exc import ModelingError, ResponseError
from clientity.logs import log
from clientity.core.hints import Requested, Embodied, Responded
from clientity.core.protocols import Requestable
from clientity.core.primitives import URL
from clientity.core.utils.calls import sift
from clientity.core.utils.models import dictate, respond
if t.TYPE_CHECKING:
    from clientity.core.adapters import Adapter
    from clientity.core.primitives import Instructions

def embody(obj: Requested) -> t.Optional[Embodied]:
    if obj is None: return None

    if isinstance(obj, Requestable):
        key = getattr(obj, "RequestKey", "json")
        return key, obj.__request__()

    if isinstance(obj, dict):
        return "json", obj

    if isinstance(obj, bytes):
        return "data", obj

    # TODO: handle known libraries e.g. dataclasses, pydantic

    return "json", dictate(obj)


def domain(url: str) -> str:
    parsed = urlparse(url)
    splits = parsed.path.split('/')[0]
    value = (parsed.netloc or splits)
    log.debug(f"(domain) parsed {url} -> {value}")
    return value

class __execute:
    async def __call__(
        self,
        base: str,
        adapter: 'Adapter',
        instructions: 'Instructions',
        exhaust: bool = False,
        *args, **kwargs
        ) -> Responded:
        pdata, qdata, bdata = sift.instructions(*args, provided=instructions, exhaust=exhaust, **kwargs)
        url = URL(base, instructions.location).resolve(**pdata)
        query, body = None, None

        if qdata:
            log.debug(f"(http.execute) preparing query data: {qdata}")
            query = (
                qdata if not instructions.querying else
                dictate(instructions.querying(**qdata))
            )
            log.debug(f"(http.execute) prepared query data: {query}")

        if bdata:
            log.debug(f"(http.execute) preparing body data: {bdata}")
            body = (
                embody(bdata) if not instructions.requesting
                else embody(instructions.requesting(**bdata))
            )
            log.debug(f"(http.execute) prepared body data: {body}")

        request = adapter.build(url=url, method=instructions.method, params=query, body=body)
        log.info(f"(http.execute) built request: {request}")
        for i, hook in enumerate(prehooks:=instructions.hooks.before):
            log.debug(f"(http.execute) applying pre-hook [{i}/{len(prehooks)}]: {hook.__name__}")
            request = await hook(request)
            # maybe log changes later


        response = await adapter.send(request)
        log.debug(f"(http.execute) received response: {response}")
        for i, hook in enumerate(posthooks:=instructions.hooks.after):
            log.debug(f"(http.execute) applying post-hook [{i}/{len(posthooks)}]: {hook.__name__}")
            response = await hook(response)
            # maybe log changes later

        #print(f"instructions.responding: {instructions.responding}")
        if instructions.responding: # probably will need to swap out for a utility that handles known methods when `__respond__` isnt implemented
            log.debug(f"(http.execute) attempting to return response model: {instructions.responding.__name__}")
            try:
                return respond(instructions.responding, response)
            except (ModelingError, ResponseError) as e:
                log.error(f"(http.execute) error returning response model (returning response object): {e!r}")
        return response
execute = __execute()
