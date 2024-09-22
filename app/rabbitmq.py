from typing import Any, Callable
from .mq import AsyncEventEmitter
import structlog

import aio_pika
import os
import json

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

logger = structlog.get_logger()

class RabbitMQConnection:
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()

    async def close(self):
        if self.connection:
            await self.connection.close()

    def get_channel(self):
        return self.channel

RABBITMQ_CONNECTION = RabbitMQConnection(url = RABBITMQ_URL)

class RabbitMQAsyncEventEmitter(AsyncEventEmitter):
    connection: RabbitMQConnection = RABBITMQ_CONNECTION
    format: Callable[..., Any]

    async def emit(self, name: str, *args: Any, **kwargs: Any):
        if self.connection.channel is None:
            await self.connection.connect()
            await self.connection.get_channel().declare_queue(self.topic)
        
        payload = json.dumps(self.format(name, *args, **kwargs).to_dict())

        ex = await self.connection.get_channel().get_exchange(self.topic)
        await ex.publish(
            aio_pika.Message(body = bytes(payload, 'utf-8')),
            routing_key=name
        )
        logger.info(f"Emit {name} - {payload}")
