from typing import Callable, Type, Any

import uuid

from structlog.contextvars import get_contextvars


class AsyncEventEmitter:
    def __init__(self):
        pass

    topic: str = None

    async def emit(self, name: str, *args: Any, **kwargs: Any):
        pass


def emit_on(*method_names: str) -> Callable[[Type], Type]:
    def decorator(cls: Type[AsyncEventEmitter]) -> Type[AsyncEventEmitter]:
        for method_name in method_names:
            if hasattr(cls, method_name):
                original_method = getattr(cls, method_name)
                wrapped_method = async_event_emitter(original_method)
                setattr(cls, method_name, wrapped_method)
        return cls

    return decorator


def emit_to(topic: str) -> Callable[[Type], Type]:
    def decorator(cls: Type[AsyncEventEmitter]) -> Type[AsyncEventEmitter]:
        setattr(cls, "topic", topic)
        return cls

    return decorator


def emit_format(format: Callable[..., Any]) -> Callable[[Type], Type]:
    def decorator(cls: Type[AsyncEventEmitter]) -> Type[AsyncEventEmitter]:
        setattr(cls, "format", format)
        return cls

    return decorator


def async_event_emitter(func: Callable) -> Callable:
    async def wrapper(self: AsyncEventEmitter, *args: Any, **kwargs: Any):
        result = await func(self, *args, **kwargs)
        await self.emit(
            func.__name__,
            *args,
            result=result,
            trace_id=get_contextvars().get("trace_id"),
            **kwargs
        )
        return result

    return wrapper
