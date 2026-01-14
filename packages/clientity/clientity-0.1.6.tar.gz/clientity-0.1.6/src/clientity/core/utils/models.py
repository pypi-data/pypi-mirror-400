# ~/clientity/src/clientity/core/utils/models.py
from __future__ import annotations
import typing as t, dataclasses as dc
from collections.abc import Set, Iterable, Sequence

from clientity.exc import ModelingError, ResponseError
from clientity.logs import log
from clientity.core.hints import (
    Responding, Responded,
    ResponseType, ResponseObject
)
from clientity.core.protocols import Responsive, ResponsiveFactory

class __constructors:
    __known__: tuple[tuple[str, str], ...] = (
        ('model_fields', 'annotation'), # pydantic v2
        ('__fields__', 'outer_type_'), # pydantic v1
        ('__dataclass_fields__', 'type') # dataclasses
    )

    def __call__(self, model: t.Any) -> dict[str, type]:
        if model is None: return {}
        for mattr, fattr in self.__known__:
            if (mapping:=getattr(model, mattr, {})):
                log.debug(f"(constructors.__call__) identified mapping for model [{model.__name__}]: {mattr}")
                return {
                    name: getattr(f, fattr) for
                    name, f in mapping.items()
                }
        if (annotated:=getattr(model, '__annotations__')):
            log.debug(f"(constructors.__call__) falling back to annotations for model: {model.__name__}")
            return dict(annotated)

        log.warning(f"(constructors.__call__) could not identify constructor mapping for model: {model.__name__}")
        return {}

constructors = __constructors()


class __dictate:
    __known__: tuple[tuple[str, t.Callable[..., dict]], ...] = (
        ("model_dump", lambda m: m.model_dump()),
        ("dict", lambda m: m.dict()),
        ("__dataclass_fields__", dc.asdict),
        ("__dict__", lambda m: m.__dict__)
    )

    def __call__(self, obj: t.Any) -> dict:
        if obj is None: return {}
        if hasattr(obj, '__request__'):
            try:
                return obj.__request__()
            except:
                pass

        for attr, method in self.__known__:
            if hasattr(obj, attr):
                return method(obj)
        return dict(obj)

dictate = __dictate()


class __respond:
    __seqs__: tuple[type, ...] = (list, tuple, set, frozenset, Set, Sequence, Iterable)

    def __item(self, model: t.Type[Responsive], data: dict) -> Responsive:
        if hasattr(model, '__respond__'):
            return model.__respond__(data)
        return model(**data)

    @t.overload
    def __call__(self, model: None, response: ResponseObject) -> None: ...
    @t.overload
    def __call__(self, model: ResponseType, response: ResponseObject) -> ResponseType: ...
    def __call__(
        self,
        model: Responding,
        response: ResponseObject
        ) -> Responded:
        if model is None: return None

        origin = t.get_origin(model)

        # Handle sequence types
        if origin in self.__seqs__:
            inner = t.get_args(model)[0]
            if hasattr(inner, '__respondall__'):
                try:
                    return inner.__respondall__(response)
                except Exception as e:
                    raise ModelingError(f"Failed to instantiate models ({inner.__name__}) via __respondall__") from e

            rbody = getattr(response, 'json', None)
            if not (rbody and callable(rbody)):
                raise ResponseError("No JSON method available in response")

            try:
                data = rbody()
            except Exception as e:
                raise ResponseError("Failed to parse json data") from e

            if not isinstance(data, (list, tuple, set)):
                raise ResponseError(f"Expected iterable response, got {type(data).__name__}")

            items = [self.__item(inner, item) for item in data]

            if origin in (set, frozenset, Set):
                return frozenset(items) if origin is frozenset else set(items)
            if origin is tuple:
                return tuple(items)
            return items

        # Handle single model with __respond__
        if hasattr(model, '__respond__'):
            try:
                return model.__respond__(response)
            except Exception as e:
                raise ModelingError(f"Failed to instantiate model ({model.__name__}) from response") from e

        # Fallback: json -> model(**data)
        rbody = getattr(response, 'json', None)
        if rbody and callable(rbody):
            try:
                data = rbody()
            except Exception as e:
                raise ResponseError("Failed to parse json data") from e
            try:
                return model(**t.cast(dict, data))
            except Exception as e:
                raise ModelingError(f"Failed to instantiate model ({model.__name__})") from e

        raise ModelingError("No JSON method available in response")
respond = __respond()
