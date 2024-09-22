import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from structlog import get_logger
from .rabbitmq import RABBITMQ_URL

logger = get_logger()
broker = RabbitBroker(RABBITMQ_URL)
app = FastStream(broker)
_faststream_run: Optional[asyncio.Task] = None


@broker.subscriber("create", exchange="user-events")
@broker.subscriber("update", exchange="user-events")
@broker.subscriber("delete", exchange="user-events")
async def handle_msg(msg: dict):
    logger.info(msg)


async def on_start():
    logger.info("Start consumer")
    global _faststream_run
    try:
        _faststream_run = asyncio.create_task(app.run())
    except Exception as e:
        raise e


async def on_stop():
    logger.info("Close consumer")
    global _faststream_run
    if _faststream_run:
        _faststream_run.cancel()
        try:
            await _faststream_run
        except asyncio.CancelledError:
            pass

    await broker.close()


@asynccontextmanager
async def consumer_lifespan(*args):
    await on_start()
    yield
    await on_stop()
