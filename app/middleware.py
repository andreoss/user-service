import time
import uuid

from typing import Callable
from litestar import Request
from litestar.types import Scope, Receive, Send
from litestar.middleware import AbstractMiddleware
import structlog


async def measure[T](
    async_task_callable: Callable[..., T], *args, **kwargs
) -> (float, Callable[..., T]):
    start = time.time()
    result = None
    error = None
    try:
        result = await async_task_callable(*args, **kwargs)
    except Exception as e:
        error = e
    end = time.time()
    elapsed = end - start

    async def next():
        if error is not None:
            raise error
        else:
            return result

    return elapsed, next


class MeasureExecutionTimeMiddleware(AbstractMiddleware):
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req = Request(scope, receive, send)
        (t, result) = await measure(self.app, scope, receive, send)
        try:
            await result()
            req.logger.info(f"Took - {t:.2f}s")
        except Exception as e:
            req.logger.error(f"Failed - {t:.2f}s - {e}")
            raise e


class TraceIdMiddleware(AbstractMiddleware):
    trace_id_header: str = "X-Request-Id"

    def trace_id(self, req: Request) -> uuid:
        trace_id = None
        try:
            if self.trace_id_header in req.headers:
                trace_id = uuid.UUID(req.headers.get(self.trace_id_header))
            else:
                trace_id = uuid.uuid4()
        except ValueError as e:
            req.logger.warn(f"Malformed header {self.trace_id_header} - {e}")
            trace_id = uuid.uuid4()
        return trace_id

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req = Request(scope, receive, send)
        trace_id = self.trace_id(req)
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
        structlog.contextvars.bind_contextvars(method=req.method)
        structlog.contextvars.bind_contextvars(path=req.scope["path"])

        async def trace_and_send(message: dict):
            if message["type"] == "http.response.start":
                structlog.contextvars.bind_contextvars(
                    status_code=message.get("status")
                )
            headers = message.get("headers", [])
            headers.append(
                (bytes(self.trace_id_header, "utf-8"), bytes(str(trace_id), "utf-8"))
            )
            message["headers"] = headers
            await send(message)

        await self.app(scope, receive, trace_and_send)
